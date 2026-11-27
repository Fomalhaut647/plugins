#!/usr/bin/env python3
"""Compute independent annual market scenarios using Decimal and explicit factors.

Python 3.10+; standard library only. No network calls or file writes.
Exit codes: 0 = computed, 1 = reported amount disagrees, 2 = invalid input.
This checks numeric/structural invariants, NOT evidence, dimensions or deduplication.
"""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, DecimalException, InvalidOperation, localcontext
from pathlib import Path
from typing import Any

EVIDENCE_TYPES = {
    "course_given", "course_assumption", "user_given", "sourced", "assumption", "derived"
}
SCOPE_FIELDS = {
    "geography", "period", "currency", "level", "metric", "population_unit",
    "annual_user_definition", "event_unit"
}


class InputError(ValueError):
    """A malformed or internally incompatible scenario."""


def object_fields(
    value: Any, required: set[str], optional: set[str], location: str
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InputError(f"{location}: expected a JSON object")
    missing = required - value.keys()
    extra = value.keys() - required - optional
    if missing:
        raise InputError(f"{location}: missing fields {sorted(missing)}")
    if extra:
        raise InputError(f"{location}: unknown fields {sorted(extra)}")
    return value


def text(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{location}: expected a non-empty string")
    return value.strip()


def nonnegative(value: Any, location: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise InputError(f"{location}: expected a decimal number, not a boolean/null")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise InputError(f"{location}: invalid decimal number") from exc
    if not number.is_finite() or number < 0:
        raise InputError(f"{location}: number must be finite and nonnegative")
    # Keep accidental extreme exponents from producing enormous JSON output.
    if number and (abs(number.adjusted()) > 1000 or len(number.as_tuple().digits) > 1000):
        raise InputError(f"{location}: number exceeds supported decimal size")
    return number


def decimal_text(value: Decimal) -> str:
    if not value:
        return "0"
    rendered = format(value, "f")
    return rendered.rstrip("0").rstrip(".") if "." in rendered else rendered


def parse_factor(value: Any, location: str, probability: bool = False) -> dict[str, Any]:
    value = object_fields(
        value, {"label", "value", "unit", "evidence", "source"}, set(), location
    )
    result = {key: text(value[key], f"{location}.{key}")
              for key in ("label", "unit", "evidence", "source")}
    if result["evidence"] not in EVIDENCE_TYPES:
        raise InputError(f"{location}.evidence: use one of {sorted(EVIDENCE_TYPES)}")
    result["value"] = nonnegative(value["value"], f"{location}.value")
    if probability and result["value"] > 1:
        raise InputError(f"{location}.value: a probability must be between 0 and 1")
    return result


def factor_list(value: Any, location: str, probability: bool = False) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise InputError(f"{location}: expected a non-empty array of factors")
    return [parse_factor(item, f"{location}[{index}]", probability)
            for index, item in enumerate(value)]


def multiply(factors: list[dict[str, Any]]) -> Decimal:
    value = Decimal(1)
    for factor in factors:
        value *= factor["value"]
    return value


def serializable_factor(factor: dict[str, Any]) -> dict[str, str]:
    return {**factor, "value": decimal_text(factor["value"])}


def evaluate_case(raw: Any, location: str = "case") -> dict[str, Any]:
    case = object_fields(
        raw, {"id", "scope", "population", "penetration", "intensity", "frequency"},
        {"label", "reported"}, location
    )
    case_id = text(case["id"], f"{location}.id")
    scope_raw = object_fields(case["scope"], SCOPE_FIELDS, {"exclusions"}, f"{location}.scope")
    scope = {key: text(value, f"{location}.scope.{key}") for key, value in scope_raw.items()}
    if scope["level"] not in {"brand", "category"}:
        raise InputError(f"{location}.scope.level: use 'brand' or 'category'")

    population = parse_factor(case["population"], f"{location}.population")
    penetration = factor_list(case["penetration"], f"{location}.penetration", True)
    intensity = factor_list(case["intensity"], f"{location}.intensity")
    frequency = factor_list(case["frequency"], f"{location}.frequency")
    all_factors = [population] + penetration + intensity + frequency

    # Enough significant digits for exact products of the supplied finite decimals.
    with localcontext() as ctx:
        ctx.prec = max(60, sum(len(f["value"].as_tuple().digits) for f in all_factors) + 20)
        n = population["value"]
        r = multiply(penetration)
        b = n * r
        i = multiply(intensity)
        f = multiply(frequency)
        if b > 0 and f < 1:
            raise InputError(
                f"{location}.frequency: annual users have at least one matching event; "
                "frequency below 1 suggests a cohort/event mismatch"
            )
        amount = b * i * f
        claim = None
        if "reported" in case:
            reported = object_fields(
                case["reported"], {"value", "source"}, {"absolute_tolerance"},
                f"{location}.reported"
            )
            claimed = nonnegative(reported["value"], f"{location}.reported.value")
            tolerance = nonnegative(
                reported.get("absolute_tolerance", 0), f"{location}.reported.absolute_tolerance"
            )
            difference = abs(amount - claimed)
            claim = {
                "value": decimal_text(claimed),
                "source": text(reported["source"], f"{location}.reported.source"),
                "absolute_tolerance": decimal_text(tolerance),
                "absolute_difference": decimal_text(difference),
                "consistent": difference <= tolerance,
            }

        unit = scope["population_unit"]
        event = scope["event_unit"]
        currency = scope["currency"]
        result = {
            "id": case_id,
            "label": text(case.get("label", case_id), f"{location}.label"),
            "scope": scope,
            "population_N": {"value": decimal_text(n), "unit": unit},
            "annual_penetration_r": decimal_text(r),
            "annual_users_B": {"value": decimal_text(b), "unit": unit},
            "intensity_I": {"value": decimal_text(i), "unit": f"{currency}/{event}"},
            "frequency_F": {"value": decimal_text(f), "unit": f"{event}/{unit}/year"},
            "annual_scale_R": {
                "value": decimal_text(amount),
                "unit": f"{currency}/year",
                "in_10k_currency_units": decimal_text(amount / Decimal(10000)),
                "in_100m_currency_units": decimal_text(amount / Decimal(100000000)),
            },
            "formula": " × ".join(decimal_text(x) for x in (n, r, i, f))
                       + " = " + decimal_text(amount),
            "input_factors": {
                "population": serializable_factor(population),
                "penetration": [serializable_factor(x) for x in penetration],
                "intensity": [serializable_factor(x) for x in intensity],
                "frequency": [serializable_factor(x) for x in frequency],
            },
            "reported_amount_audit": claim,
        }
    return result


def evaluate_document(raw: Any) -> dict[str, Any]:
    document = object_fields(raw, {"schema_version", "cases"}, set(), "document")
    if type(document["schema_version"]) is not int or document["schema_version"] != 1:
        raise InputError("document.schema_version: expected integer 1")
    if not isinstance(document["cases"], list) or not document["cases"]:
        raise InputError("document.cases: expected a non-empty array")
    results = []
    seen_ids = set()
    for index, case in enumerate(document["cases"]):
        result = evaluate_case(case, f"cases[{index}]")
        if result["id"] in seen_ids:
            raise InputError(f"cases[{index}].id: duplicate id {result['id']!r}")
        seen_ids.add(result["id"])
        results.append(result)
    mismatches = [x["id"] for x in results
                  if x["reported_amount_audit"] is not None
                  and not x["reported_amount_audit"]["consistent"]]
    return {
        "schema_version": 1,
        "cases": results,
        "reported_amount_mismatches": mismatches,
        "aggregation": "No total: cases may be alternative scenarios or incompatible markets.",
        "limitations": (
            "Numeric/structure checks only. Evidence labels are supplied by the author. "
            "Verify units, conditional denominators, annual deduplication, payment-rate "
            "placement and non-overlapping money flows separately."
        ),
    }


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError(f"duplicate JSON field: {key!r}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise InputError(f"non-finite JSON number: {value}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="UTF-8 JSON input file, or '-' for stdin")
    args = parser.parse_args(argv)
    try:
        source = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        document = json.loads(
            source, parse_float=Decimal, parse_constant=reject_constant,
            object_pairs_hook=unique_object
        )
        result = evaluate_document(document)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result["reported_amount_mismatches"] else 0
    except (InputError, OSError, UnicodeError, json.JSONDecodeError, DecimalException) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
