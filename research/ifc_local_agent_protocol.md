# IFC 本地规范索引与检索协议

> **[已被取代 2026-07-19]** 本文件为初版草案，其中 `IFC4x3-machine-readable/`（DEV 构建）相关路径已废弃。
> 现行方案：`.opencode\skills\ifc-spec-lookup\`（查询 skill + 固定脚本），权威依据为 `research\IFC4_3\`（IFC4X3_ADD2 盖章版），索引见 `research\IFC_INDEX.md`。本文件仅作历史参考。

## 目的

这份文件用于指导本地 agent 在 `research/` 目录下稳定、可复用地检索 IFC 4.3 规范、属性集和旧版本参考内容，并输出**可核对、可追溯、尽量不含不确定表述**的结果。IFC 4.3 目前是 buildingSMART 官方最新正式标准，对应 ISO 16739-1:2024；但实现和样本验证阶段仍可能需要同时参考 IFC4 / IFC2x3 等旧版本资料。[cite:4][cite:6]

## 目录理解

假设本地目录如下：

```text
research/
├─ IFC4.3.x-development/
│  ├─ docs/
│  ├─ content/
│  ├─ schemas/
│  └─ reference_schemas/
└─ IFC4x3-machine-readable/
   ├─ IFC4X3_DEV_3f67a89.exp
   ├─ IFC4X3_DEV_3f67a89.xsd
   └─ psd/
```

建议将各目录理解为三层：

- `IFC4.3.x-development/docs/`：**语义解释层**，优先用于回答“某实体是什么”“某属性集是什么意思”“某章节如何定义”。[cite:6]
- `IFC4x3-machine-readable/*.exp`：**结构校验层**，优先用于核对实体继承、显式属性、类型关系和 schema 级定义。
- `IFC4x3-machine-readable/psd/`：**属性集层**，优先用于核对 Pset/Qto 的机器可读定义。
- `IFC4.3.x-development/reference_schemas/`：**旧版本兼容层**，只在需要做版本差异比对、旧样本解释、兼容性分析时启用。[cite:63]

## 查询优先级

本地 agent 必须按以下顺序检索，除非用户明确要求跨版本比较：

1. **先查 `docs/`**：获取最容易被人理解的定义和上下文。
2. **再查 `.exp`**：确认实体继承、属性签名、正式 schema 结构。
3. **再查 `psd/`**：确认属性集、属性名、适用对象。
4. **最后查 `reference_schemas/`**：仅在需要旧版本兼容说明时使用。[cite:6][cite:63]

这个顺序的目的是先得到“可解释答案”，再补“结构证据”。IfcOpenShell 文档也建议处理 IFC 时尽量使用 schema-aware / schema-agnostic 思维，避免把逻辑硬绑定到单一版本。[cite:71]

## 输出要求

本地 agent 每次检索后，输出必须包含以下字段：

```text
Query Intent:
Primary Sources:
Matched Paths:
Key Findings:
Confidence:
Cross-Version Notes:
Unknowns:
```

约束如下：

- `Primary Sources`：列出实际命中的本地文件路径。
- `Key Findings`：只写从命中文件中可以直接确认的结论。
- `Confidence`：只能用 `high / medium / low`，并说明原因。
- `Cross-Version Notes`：只有在确实查过 `reference_schemas/` 时才填写。
- `Unknowns`：凡是本地未命中、多个版本存在差异、或样本实现可能不一致的地方，都必须显式写出，不允许猜测补全。

## 索引文件设计

建议在 `research/` 下新增以下文件：

```text
research/
├─ AGENT_PROTOCOL.md
├─ IFC_INDEX.md
├─ IFC_INDEX.json
├─ VERSION_MAP.md
└─ queries/
   ├─ entity_lookup.md
   ├─ pset_lookup.md
   ├─ property_lookup.md
   └─ version_diff.md
```

### 1. `AGENT_PROTOCOL.md`

内容就是本文件，作为 agent 的总入口说明。

### 2. `IFC_INDEX.md`

人工可读索引，至少先覆盖当前 MVP 高相关对象：

- `IfcDoor`
- `IfcWall`
- `IfcSpace`
- `IfcOpeningElement`
- `Pset_DoorCommon`
- `FireRating`
- `FireExit`
- 宽度相关字段（如 OverallWidth 或门宽相关 property）
- 碰撞检测涉及的对象分类（墙、梁、管、风管、设备）

推荐格式：

| Keyword | Kind | Primary Path | Secondary Path | Notes |
|---|---|---|---|---|
| IfcDoor | Entity | `docs/.../IfcDoor.md` | `.exp` location | 门对象主实体 |
| Pset_DoorCommon | PropertySet | `docs/.../Pset_DoorCommon.md` | `psd/...xml` | 门常见属性集 |
| FireRating | Property | `docs/properties/f/FireRating.md` | `psd/...xml` | 常用消防属性 |

### 3. `IFC_INDEX.json`

给程序或 agent 自动消费，建议字段：

```json
[
  {
    "keyword": "IfcDoor",
    "kind": "Entity",
    "primary_path": "IFC4.3.x-development/docs/.../IfcDoor.md",
    "secondary_paths": ["IFC4x3-machine-readable/IFC4X3_DEV_3f67a89.exp"],
    "schema_versions": ["IFC4.3"],
    "tags": ["door", "mvp", "egress"],
    "notes": "Primary entity for door rules"
  }
]
```

### 4. `VERSION_MAP.md`

只记录**当前项目真正关心的差异**，避免变成无底洞。至少先记：

- `IfcDoor` 在不同版本中的读取注意事项
- 门宽字段的优先读取顺序
- `FireRating` / `FireExit` 的位置和可用性
- 碰撞检测常用对象类别的版本稳定性

## 推荐检索命令

以下命令模式可以直接交给本地 agent 执行：

### 查实体

```bash
grep -RIn "^# IfcDoor\b\|\bIfcDoor\b" research/IFC4.3.x-development/docs | head -n 20
```

### 查属性集

```bash
grep -RIn "Pset_DoorCommon" research/IFC4.3.x-development/docs research/IFC4x3-machine-readable/psd | head -n 20
```

### 查属性

```bash
grep -RIn "\bFireRating\b\|\bFireExit\b" research/IFC4.3.x-development/docs research/IFC4x3-machine-readable/psd | head -n 40
```

### 查旧版本参考

```bash
grep -RIn "IfcDoor\|FireRating\|Pset_DoorCommon" research/IFC4.3.x-development/reference_schemas | head -n 40
```

### 查 EXPRESS 中的结构定义

```bash
grep -n "ENTITY IfcDoor\|TYPE IfcDoorTypeEnum\|FireRating" research/IFC4x3-machine-readable/IFC4X3_DEV_3f67a89.exp | head -n 40
```

## 检索协议

### 场景 A：用户问“某对象/属性是什么”

1. 查 `docs/` 获取定义。
2. 查 `.exp` 确认实体或类型位置。
3. 若是属性集，再查 `psd/`。
4. 输出定义、来源路径、是否已核对结构。

### 场景 B：用户问“某条规则能否实现”

1. 查目标对象实体，如 `IfcDoor`、`IfcWall`。
2. 查相关属性集，如 `Pset_DoorCommon`。
3. 查字段是否有标准属性，若没有则明确说明需业务层补充。
4. 输出“标准可表达的部分”和“实现层仍需判断的部分”。

### 场景 C：用户问“旧版本是否兼容”

1. 先给出 4.3 主结论。
2. 再查 `reference_schemas/` 中对应对象与属性。
3. 明确区分：文件级兼容、服务级转换兼容、业务读取兼容。[cite:63]
4. 不允许只因名称相似就断定兼容。

## 本地 agent 的行为约束

- 不得在未命中本地文件时假装已确认。
- 不得把 DEV 构建内容表述为“盖章版正式文件”。
- 不得把示例模型中的字段习惯误当成 IFC 标准要求。
- 不得因旧版本样本能跑通，就自动推断 4.3 中完全一致。
- 必须优先引用本地路径，其次才考虑联网补充。

## 关于 `IFC4X3_ADD2.exp` 是否重要

重要，但不是当前阻断项。IFC 4.3 已作为正式标准发布；如果本地只有 DEV 构建版 `.exp`，在**做日常检索、实体理解、MVP 规则开发**时通常已经够用，但在**需要正式归档、精确版本对外说明、或排查 DEV 与正式版细小差异**时，盖章版 `IFC4X3_ADD2.exp` 更稳妥。[cite:4][cite:6]

### 什么时候必须补盖章版

- 准备对外写“本项目严格基于 IFC4.3 ADD2 正式版”时。
- 发现本地 DEV 文件与在线文档页存在不一致时。
- 需要做可复现的版本锁定与审计记录时。

### 如何操作

1. 通过浏览器手动访问 buildingSMART 的正式 schema 发布入口。[cite:6]
2. 下载正式版 `IFC4X3_ADD2.exp`。
3. 放入 `research/IFC4x3-machine-readable/`。
4. 在 `VERSION_MAP.md` 或 `AGENT_PROTOCOL.md` 记录：文件名、下载日期、来源 URL、是否为正式版。
5. 后续 agent 默认优先使用正式版；DEV 文件只作为补充或差异核验。

## 交给 opencode 的执行任务

1. 在 `research/` 下创建 `AGENT_PROTOCOL.md`、`IFC_INDEX.md`、`IFC_INDEX.json`、`VERSION_MAP.md`、`queries/`。
2. 先围绕 MVP 相关关键词建立第一版索引，不追求全量一次完成。
3. 每个关键词至少记录：主路径、次路径、版本、用途说明。
4. 以后每完成一个规则调研，就把新增关键词回填到索引。
5. 所有本地检索输出必须遵守本文件的输出格式与不确定性约束。
