#!/usr/bin/env python3
"""Behavioral/numeric regression tests; no external services or dependencies."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from decimal import Decimal
from pathlib import Path

from size_market import InputError, evaluate_case, evaluate_document

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = json.loads((ROOT / "references" / "teaching-cases.json").read_text(encoding="utf-8"))
SCRIPT = ROOT / "scripts" / "size_market.py"


def base_case() -> dict:
    case = copy.deepcopy(FIXTURE["cases"][2])
    case.pop("reported", None)
    return case


def factor(value: str, unit: str = "无量纲") -> dict:
    return {"label": "测试因子", "value": value, "unit": unit,
            "evidence": "assumption", "source": "仅用于数值测试，不是市场数据"}


def annual(case: dict) -> Decimal:
    return Decimal(evaluate_case(case)["annual_scale_R"]["value"])


class MarketSizingTests(unittest.TestCase):
    def test_three_course_examples(self):
        report = evaluate_document(FIXTURE)
        self.assertEqual([Decimal(x["annual_scale_R"]["value"]) for x in report["cases"]],
                         [Decimal("91875000000"), Decimal("28000000000"), Decimal("7620000")])
        self.assertEqual(report["reported_amount_mismatches"], [])

    def test_ad_cpm_and_frequency(self):
        result = evaluate_case(FIXTURE["cases"][0])
        self.assertEqual(result["annual_users_B"]["value"], "980000000")
        self.assertEqual(result["intensity_I"]["value"], "0.09375")
        self.assertEqual(result["frequency_F"]["value"], "1000")
        self.assertEqual(result["annual_scale_R"]["in_100m_currency_units"], "918.75")

    def test_payment_rate_applied_once(self):
        result = evaluate_case(base_case())
        self.assertEqual(result["annual_users_B"]["value"], "127000")
        self.assertEqual(result["intensity_I"]["value"], "20")
        self.assertEqual(result["annual_scale_R"]["in_10k_currency_units"], "762")

    def test_payment_rate_sensitivity(self):
        for rate, expected in [("0.005", "3810000"), ("0.01", "7620000"), ("0.02", "15240000")]:
            with self.subTest(rate=rate):
                case = base_case()
                case["penetration"][0]["value"] = rate
                self.assertEqual(annual(case), Decimal(expected))

    def test_conditional_probability_product(self):
        case = base_case()
        case["penetration"] = [factor("0.1"), factor("0.1")]
        self.assertEqual(annual(case), Decimal("7620000"))

    def test_precounted_payers_equivalent_to_population_times_rate(self):
        case = base_case()
        case["population"]["value"] = "127000"
        case["penetration"][0]["value"] = "1"
        self.assertEqual(annual(case), Decimal("7620000"))

    def test_split_frequency_is_equivalent(self):
        case = base_case()
        case["frequency"] = [factor("1.5"), factor("2")]
        self.assertEqual(annual(case), Decimal("7620000"))

    def test_zero_penetration_produces_zero_market(self):
        case = base_case()
        case["penetration"][0]["value"] = "0"
        case["frequency"][0]["value"] = "0"
        self.assertEqual(annual(case), Decimal(0))

    def test_zero_population_produces_zero_market(self):
        case = base_case()
        case["population"]["value"] = "0"
        self.assertEqual(annual(case), Decimal(0))

    def test_zero_monetization_is_allowed(self):
        case = base_case()
        case["intensity"][0]["value"] = "0"
        self.assertEqual(annual(case), Decimal(0))

    def test_invalid_probability_rejected(self):
        for value in ["-0.1", "1.01", "70", "70%"]:
            with self.subTest(value=value):
                case = base_case()
                case["penetration"][0]["value"] = value
                with self.assertRaises(InputError):
                    evaluate_case(case)

    def test_negative_amount_rejected(self):
        case = base_case()
        case["intensity"][0]["value"] = "-20"
        with self.assertRaises(InputError):
            evaluate_case(case)

    def test_nonfinite_numbers_rejected(self):
        for value in ["NaN", "Infinity", "-Infinity", Decimal("NaN"), float("inf")]:
            with self.subTest(value=str(value)):
                case = base_case()
                case["population"]["value"] = value
                with self.assertRaises(InputError):
                    evaluate_case(case)

    def test_boolean_null_and_composite_numbers_rejected(self):
        for value in [True, None, [], {}]:
            with self.subTest(value=value):
                case = base_case()
                case["population"]["value"] = value
                with self.assertRaises(InputError):
                    evaluate_case(case)

    def test_extreme_exponents_rejected(self):
        case = base_case()
        case["population"]["value"] = "1e1001"
        with self.assertRaises(InputError):
            evaluate_case(case)

    def test_frequency_below_one_rejected_for_annual_users(self):
        for value in ["0", "0.5"]:
            with self.subTest(value=value):
                case = base_case()
                case["frequency"][0]["value"] = value
                with self.assertRaises(InputError):
                    evaluate_case(case)

    def test_missing_scope_rejected(self):
        case = base_case()
        del case["scope"]["annual_user_definition"]
        with self.assertRaises(InputError):
            evaluate_case(case)

    def test_invalid_market_level_rejected(self):
        case = base_case()
        case["scope"]["level"] = "whatever"
        with self.assertRaises(InputError):
            evaluate_case(case)

    def test_scope_preserved(self):
        case = copy.deepcopy(FIXTURE["cases"][0])
        self.assertEqual(evaluate_case(case)["scope"], case["scope"])
        self.assertEqual(evaluate_case(case)["scope"]["level"], "brand")

    def test_evidence_is_not_upgraded_to_verified(self):
        result = evaluate_case(base_case())
        stored = result["input_factors"]["penetration"][0]
        self.assertEqual(stored["evidence"], "course_assumption")
        self.assertEqual(stored["source"], base_case()["penetration"][0]["source"])

    def test_missing_or_invalid_evidence_rejected(self):
        for action in ["missing", "invalid"]:
            with self.subTest(action=action):
                case = base_case()
                if action == "missing":
                    del case["intensity"][0]["source"]
                else:
                    case["intensity"][0]["evidence"] = "magically_verified"
                with self.assertRaises(InputError):
                    evaluate_case(case)

    def test_empty_factor_lists_rejected(self):
        for field in ("penetration", "intensity", "frequency"):
            with self.subTest(field=field):
                case = base_case()
                case[field] = []
                with self.assertRaises(InputError):
                    evaluate_case(case)

    def test_unknown_fields_rejected_not_silently_ignored(self):
        case = base_case()
        case["pay_rate"] = "0.01"
        with self.assertRaises(InputError):
            evaluate_case(case)

    def test_duplicate_case_ids_rejected(self):
        with self.assertRaises(InputError):
            evaluate_document({"schema_version": 1, "cases": [base_case(), base_case()]})

    def test_invalid_schema_and_empty_document_rejected(self):
        for doc in [{"schema_version": True, "cases": [base_case()]},
                    {"schema_version": 2, "cases": [base_case()]},
                    {"schema_version": 1, "cases": []}]:
            with self.subTest(doc=doc):
                with self.assertRaises(InputError):
                    evaluate_document(doc)

    def test_alternative_scenarios_have_no_grand_total(self):
        case2 = base_case()
        case2["id"] = "higher-rate"
        case2["penetration"][0]["value"] = "0.02"
        result = evaluate_document({"schema_version": 1, "cases": [base_case(), case2]})
        self.assertEqual(len(result["cases"]), 2)
        self.assertNotIn("total", result)
        self.assertNotIn("grand_total", result)
        self.assertEqual([x["annual_scale_R"]["value"] for x in result["cases"]],
                         ["7620000", "15240000"])

    def test_gaokao_source_conflict_is_flagged_not_fixed(self):
        case = base_case()
        case["population"]["value"] = "13500000"
        case["penetration"][0]["value"] = "0.001"
        case["intensity"][0]["value"] = "10000"
        case["frequency"][0]["value"] = "1"
        case["reported"] = {"value": "1000000000", "source": "课件 PDF 第76页标题10亿"}
        result = evaluate_case(case)
        self.assertEqual(result["annual_scale_R"]["value"], "135000000")
        self.assertFalse(result["reported_amount_audit"]["consistent"])
        self.assertEqual(result["reported_amount_audit"]["absolute_difference"], "865000000")
        self.assertEqual(case["penetration"][0]["value"], "0.001")

    def test_reported_baseline_exposes_a_duplicated_payment_factor(self):
        case = copy.deepcopy(FIXTURE["cases"][2])
        case["intensity"].append(factor("0.01"))
        result = evaluate_case(case)
        self.assertEqual(result["annual_scale_R"]["value"], "76200")
        self.assertFalse(result["reported_amount_audit"]["consistent"])

    def test_rounding_tolerance_is_explicit(self):
        result = evaluate_case(FIXTURE["cases"][0])
        self.assertEqual(result["reported_amount_audit"]["absolute_difference"], "25000000")
        self.assertTrue(result["reported_amount_audit"]["consistent"])
        case = copy.deepcopy(FIXTURE["cases"][0])
        case["reported"]["absolute_tolerance"] = "0"
        self.assertFalse(evaluate_case(case)["reported_amount_audit"]["consistent"])

    def test_negative_tolerance_rejected(self):
        case = copy.deepcopy(FIXTURE["cases"][0])
        case["reported"]["absolute_tolerance"] = "-1"
        with self.assertRaises(InputError):
            evaluate_case(case)

    def test_decimal_arithmetic_avoids_binary_float_artifacts(self):
        case = base_case()
        case["population"]["value"] = 100
        case["penetration"][0]["value"] = 0.1
        case["intensity"][0]["value"] = 0.2
        case["frequency"][0]["value"] = 3
        self.assertEqual(annual(case), Decimal("6"))

    def test_input_is_not_mutated(self):
        before = copy.deepcopy(FIXTURE)
        evaluate_document(FIXTURE)
        self.assertEqual(FIXTURE, before)

    def test_cli_file_success(self):
        proc = subprocess.run([sys.executable, str(SCRIPT), str(ROOT / "references/teaching-cases.json")],
                              text=True, capture_output=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(len(json.loads(proc.stdout)["cases"]), 3)

    def test_cli_stdin_and_mismatch_exit(self):
        case = base_case()
        case["reported"] = {"value": "1", "source": "测试故意不一致"}
        payload = json.dumps({"schema_version": 1, "cases": [case]})
        proc = subprocess.run([sys.executable, str(SCRIPT), "-"], input=payload,
                              text=True, capture_output=True, check=False)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["reported_amount_mismatches"], [case["id"]])

    def test_cli_malformed_json_duplicate_keys_and_nan(self):
        for raw in ["{", '{"schema_version":1,"schema_version":1,"cases":[]}',
                    '{"schema_version":1,"cases":NaN}']:
            with self.subTest(raw=raw):
                proc = subprocess.run([sys.executable, str(SCRIPT), "-"], input=raw,
                                      text=True, capture_output=True, check=False)
                self.assertEqual(proc.returncode, 2)
                self.assertEqual(proc.stdout, "")
                self.assertTrue(proc.stderr.startswith("Error:"))

    def test_cli_missing_file_has_no_traceback(self):
        proc = subprocess.run([sys.executable, str(SCRIPT), str(ROOT / "does-not-exist.json")],
                              text=True, capture_output=True, check=False)
        self.assertEqual(proc.returncode, 2)
        self.assertNotIn("Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
