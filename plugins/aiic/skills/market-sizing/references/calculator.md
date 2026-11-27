# 计算器输入说明

附带脚本只做确定性的数值与结构检查，不联网、不安装依赖、不修改输入、不写文件。需要 Python 3.10 或更高版本，全部使用标准库。

## 运行

下面的 `<skill 目录>` 指本 skill 的安装目录，SKILL.md 里给出了脚本的完整路径：

```bash
python3 <skill 目录>/scripts/size_market.py <skill 目录>/references/teaching-cases.json
python3 <skill 目录>/scripts/size_market.py my-market.json > my-result.json
python3 <skill 目录>/scripts/test_size_market.py
```

输入文件写它自己的实际路径。也可用 `-` 从标准输入读取 JSON。重定向生成的文件由调用者选择路径；脚本本身仅输出到标准输出。

[teaching-cases.json](teaching-cases.json) 包含三组互不相加的课程情景：抖音约 918.75 亿元、海底捞 280 亿元、应届生纯 AI 面试前陪练 762 万元。这些是教学输入的乘法结果，不是验证过的当前市场数据。测试另包含第 76 页标题金额与算式不一致的情形。

退出码：`0` 表示完成计算且没有超出指定容差的原文金额差异；`1` 表示完成计算但至少有一项原文金额不一致，详情仍在输出 JSON 中；`2` 表示输入或文件错误，错误写入标准错误流。

## 输入结构

顶层是 `schema_version: 1` 和非空 `cases` 数组。每个 case 独立计算，不产生总额。输入允许中文标签。

```json
{
  "schema_version": 1,
  "cases": [
    {
      "id": "illustrative-case",
      "scope": {
        "geography": "示范地区",
        "period": "一年，纯演示假设",
        "currency": "CNY",
        "level": "category",
        "metric": "用户实付金额",
        "population_unit": "人",
        "annual_user_definition": "当年至少购买一次此类服务的去重用户",
        "event_unit": "次付费服务",
        "exclusions": "不含其他需求、企业采购及人工服务"
      },
      "population": {
        "label": "潜在人群总数",
        "value": "100000",
        "unit": "人",
        "evidence": "assumption",
        "source": "演示假设，无外部数据依据"
      },
      "penetration": [
        {
          "label": "潜在人群中的年度付费比例",
          "value": "0.01",
          "unit": "无量纲",
          "evidence": "assumption",
          "source": "演示假设，付费率仅在此出现"
        }
      ],
      "intensity": [
        {
          "label": "每次实付",
          "value": "20",
          "unit": "CNY/次付费服务",
          "evidence": "assumption",
          "source": "演示假设"
        }
      ],
      "frequency": [
        {
          "label": "每年度付费用户全年购买次数",
          "value": "3",
          "unit": "次付费服务/人/年",
          "evidence": "assumption",
          "source": "演示假设"
        }
      ]
    }
  ]
}
```

该纯演示算式为 `100000 × 0.01 × 20 × 3 = 60000 元/年`。

### 字段约定

`id` 在同一文件内不能重复。可选 `label` 作为显示名。`scope` 中除 `exclusions` 外，上例字段全部必填；`level` 只能是 `brand` 或 `category`。这些字段用于保留测算边界，不意味着程序理解或验证了边界。

`population` 是一个因子；`penetration`、`intensity`、`frequency` 是非空因子数组，同一数组内连乘。广告强度可拆成时长、计费曝光率、CPM 和 `0.001`；年度频度可拆成年度活跃天数与活跃日内次数。拆分是否语义成立、单位能否约掉仍由分析者审查。

每个因子包含 `label`、`value`、`unit`、`evidence`、`source`。建议 `value` 使用十进制字符串，也支持 JSON 数字；不接受含逗号、中文万亿单位或百分号的数值。`1%` 填 `"0.01"`，`1270 万` 填 `"12700000"`。本示例数据的人民币金额都以元输入。

| evidence 值 | 含义 |
|---|---|
| `course_given` | 课件给定的约数或引述值，不代表本次独立核验 |
| `course_assumption` | 课件明确的教学假设 |
| `user_given` | 用户直接提供，是否已验证需由来源说明 |
| `sourced` | 本次有外部或实测来源支持，需保留来源与日期 |
| `assumption` | 本次分析或演示假设 |
| `derived` | 来自明确的数学推导或单位转换 |

程序只保留标签，不能证明 `sourced` 真的有依据。没有来源的已知数不能通过随便填一个网址就变成可靠事实；假设的 `source` 应说明假设缘由或验证方法。

### 可选原文金额审计

在 case 中加入：

```json
"reported": {
  "value": "1000000000",
  "absolute_tolerance": "0",
  "source": "原材料标题声称10亿元，需与其参数核对"
}
```

`reported.value` 和可选的 `absolute_tolerance` 都使用 scope 中币种的基础货币单位。默认容差为零。容差只用来处理声明的舍入精度，不是市场估计误差、可信区间或修改参数的许可。课件抖音结果约 919 亿元，样例使用 0.5 亿元绝对容差来对照其按亿元舍入的写法。

## 检查范围

程序检查有限非负数字、概率因子不超过 1、字段缺失或误拼、重复 JSON 字段、重复 case id、证据字段存在、年度用户为正时频度不少于一次，以及原文金额是否落在明确容差内。Decimal 用于避免常见二进制浮点舍入误差，输出保留基础单位、除以一万及除以一亿的结果。

程序**不检查**：数据真实性、人口和渗透率是否同分母、付费率有没有语义上的重复、具体单位是否可约分、年去重是否正确、某两组人群是否重叠、某金额流是不是另一金额流的一部分、`period` 是否代表合适的完整年度、标价是否等于实付。这些必须按 [口径与计算指南](calculation-guide.md) 人工审查。

不自动汇总是有意的：文件可能同时包含品牌、赛道、不同金额指标或乐观 / 悲观情景。已确认可加总的子市场，可以读取输出中的 `annual_scale_R.value` 后另行汇总，并在报告里交代去重与兼容性依据。
