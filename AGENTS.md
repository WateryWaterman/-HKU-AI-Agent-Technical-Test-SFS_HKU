# AGENTS.md

## IFC 规范查询（重要）

- 一切 IFC 4.3 规范查询使用 `ifc-spec-lookup` skill（本地检索，禁止抓取 buildingsmart.org）。
- 权威依据：`research\IFC4_3\`（IFC4X3_ADD2 盖章版：`HTML\IFC4X3_ADD2.exp`、`HTML\psd\`、`HTML\lexical\*.htm`）。
- 快查层：`research\IFC4.3.x-development\docs\`（纯 markdown，master 分支；正式引用条文以 ADD2 为准）。
- 旧版本兼容：`research\IFC4.3.x-development\reference_schemas\`。
- `research\IFC4x3_DEV-build_NOT-normative\` 已废弃，勿引用。
- 热点关键词直达表：`research\IFC_INDEX.md`（调研新规则后回填）；版本差异记录：`research\VERSION_MAP.md`。
- `research\ifc_local_agent_protocol.md` 是初版协议草案，路径已过时，仅作历史参考。

## 网络

- 外网访问需走代理 `http://127.0.0.1:7890`（curl.exe -x）。
