---
name: ifc-spec-lookup
description: Use when querying the IFC 4.3 specification from local research/ sources - entity definitions (IfcDoor, IfcWall, IfcSpace...), property sets (Pset_*), quantity sets (Qto_*), single properties (FireRating, FireExit...), EXPRESS schema structure (IFC4X3_ADD2.exp), PSD XML, or IFC2x3/IFC4 old-version compatibility. Never fetch buildingsmart.org for these - all sources are local.
---

# IFC 规范本地查询

所有 IFC 4.3 规范查询一律走本地 `research\` 目录，禁止联网抓取 buildingsmart.org（主站有 Cloudflare 拦截，且本地已有完整官方包）。

## 数据源分层（重要）

| 层 | 路径（相对 `D:\ProgramData\ArchiTestMajun\research\`） | 用途 |
|---|---|---|
| **权威依据（盖章版 ADD2）** | `IFC4_3\HTML\IFC4X3_ADD2.exp` / `.xsd` | 实体继承、显式属性、WHERE 规则的最终依据 |
| **权威 PSD** | `IFC4_3\HTML\psd\*.xml`（760 个） | Pset/Qto 机器可读定义的最终依据 |
| **权威 HTML 全文** | `IFC4_3\HTML\lexical\<名称>.htm` 等 | 正式引用条文、概念模板、Annex |
| **快查层（markdown）** | `IFC4.3.x-development\docs\` | 日常语义查询首选，token 最省；注意它对应 master 分支，条文引用最终以 ADD2 为准 |
| **旧版本兼容层** | `IFC4.3.x-development\reference_schemas\`（IFC2x3/IFC4/4x1/4x2 EXPRESS+PSD） | 仅版本差异比对时启用 |
| ~~已废弃~~ | `IFC4x3_DEV-build_NOT-normative\` | 勿作依据，勿引用 |

docs\ 快查层内部结构：
- 实体/类型：`docs\schemas\{core,shared,domain,resource}\<Schema>\{Entities,Types}\<名称>.md`
- 属性集/数量集：`docs\schemas\...\<Schema>\{PropertySets,QuantitySets}\<名称>.md`
- 单个属性：`docs\properties\<首字母小写>\<属性名>.md`

## 查询流程

1. **先跑固定脚本**（见下），拿到命中路径
2. **只读命中文件的相关片段**（md 直接读；htm 仅在需要正式条文时读）
3. 结构问题（继承/属性签名/WHERE）→ 以 `.exp` 命中行为准
4. Pset/属性适用性 → 以 `psd\*.xml` 为准
5. 旧版本兼容 → 才碰 `reference_schemas\`，并在输出中单列

## 固定脚本

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\ProgramData\ArchiTestMajun\.opencode\skills\ifc-spec-lookup\scripts\ifc-lookup.ps1" <Kind> <Term> [-After N]
```

| Kind | 用途 | 示例 |
|---|---|---|
| `entity` | 实体：md + lexical.htm + exp 定义行 | `entity IfcDoor` |
| `type` | 类型/枚举 | `type IfcDoorTypeEnum` |
| `pset` | 属性集：md + 官方 psd xml | `pset Pset_DoorCommon` |
| `qto` | 数量集 | `qto Qto_DoorBaseQuantities` |
| `prop` | 单属性：定义 md + 出现在哪些 psd | `prop FireRating` |
| `express` | 在 ADD2 exp 内正则检索，`-After 15` 带上下文 | `express "ENTITY IfcDoor" -After 15` |
| `psd` | 在官方 psd xml 内全文检索 | `psd OverallWidth` |
| `old` | 旧版本 reference_schemas 检索 | `old FireRating` |
| `all` | 名称跨层模糊定位 | `all Door` |

先查 `research\IFC_INDEX.md`（MVP 热点关键词直达表），命中则可跳过脚本第一步。

## 输出格式（必须遵守）

```text
Query Intent: <一句话>
Primary Sources: <实际命中的本地路径>
Key Findings: <仅写命中文件可直接确认的结论>
Confidence: high|medium|low + 原因
Cross-Version Notes: <仅在真的查过 reference_schemas 时填>
Unknowns: <未命中/版本差异/需业务层补充的点，禁止猜测补全>
```

## 行为约束

- 未命中本地文件时不得假装已确认
- 不得把 master 分支 docs 的措辞当作 ADD2 盖章条文引用；正式引用先对照 `IFC4_3\HTML`
- 不得把示例模型习惯当成标准要求
- 每完成一个规则调研，把新关键词回填 `research\IFC_INDEX.md`
