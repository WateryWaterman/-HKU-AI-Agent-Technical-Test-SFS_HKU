# IFC 样本文件 — 出处与许可证

本目录下所有 `.ifc` 文件均来自公开开源仓库，仅用于本项目的功能测试、字段填充率调研与演示。

## 样本清单

| 文件名 | 建筑类型 | IFC 版本 | 大小 | 源仓库 | 源路径 |
|---|---|---|---:|---|---|
| `Duplex_Apartment_IFC2x3.ifc` | 多层民居（2 层双拼公寓） | IFC2x3 | 2.27 MB | buildingsmart-community/Community-Sample-Test-Files | `IFC 2.3.0.1 (IFC 2x3)/Duplex Apartment/Duplex_A_20110907.ifc` |
| `Clinic_Architectural_IFC2x3.ifc` | 教学/机构类（2 层医疗牙科诊所，含医疗/牙科/儿科/影像科室） | IFC2x3 | 12.40 MB | buildingsmart-community/Community-Sample-Test-Files | `IFC 2.3.0.1 (IFC 2x3)/Medical-Dental Clinic/Clinic_Architectural.ifc` |
| `Revit_SnowdonTower_ARC_FireRating_IFC4.ifc` | 小型大厦（Revit 示例商业多层建筑，已含 FireRating 属性） | IFC4 | 13.02 MB | youshengCode/IfcSampleFiles | `Ifc4_Revit_ARC_FireRatingAdded.ifc` |
| `SampleHouse_IFC4.ifc` | 单户住宅（Autodesk Revit 2015 示例房屋） | IFC4 | 2.17 MB | youshengCode/IfcSampleFiles | `Ifc4_SampleHouse.ifc` |

## 许可证

### 1. Duplex_Apartment_IFC2x3.ifc 与 Clinic_Architectural_IFC2x3.ifc
- 许可证：**Creative Commons Attribution 4.0 International (CC BY 4.0)**
- 完整文本：http://creativecommons.org/licenses/by/4.0/
- 本地副本：`_LICENSE_buildingsmart_community.txt`
- 原始 README：`_duplex_readme.md` / `_clinic_readme.md`
- **引用要求（来自原始 README）**：
  > "You must identify the source of the information as 'BSI (2020) Duplex Apartment Test Files' / 'BSI (2020) Medical-Dental Test Files,' buildingSMART International" and add the GitHub URL.
- 源仓库 URL：https://github.com/buildingsmart-community/Community-Sample-Test-Files
- 项目历史：最早由德国发布，后由美国 NIBS / US Construction Engineering Research Laboratory 托管（2009–2020），2020 年起由 buildingSMART International 在 GitHub 重新发布。

### 2. Revit_SnowdonTower_ARC_FireRating_IFC4.ifc 与 SampleHouse_IFC4.ifc
- 源仓库：https://github.com/youshengCode/IfcSampleFiles
- 仓库自述："A collection of IFC sample files for software test use."（未在仓库根提供明确许可证文件）
- 原始来源：Autodesk Revit 自带示例项目（Snowdon Towers 与 Sample House）经 Revit IFC Exporter 导出
- Revit IFC Exporter 本身开源（MIT/自定义混合，详见 https://github.com/Autodesk/revit-ifc）
- `*_FireRatingAdded` 版本为社区在原 Revit 导出文件基础上补充了 `FireRating` 属性的派生版本
- **使用建议**：用于内部测试与字段填充率调研属于合理使用；若需公开发布或商用，建议改用 buildingSMART CC BY 4.0 样本或自行从 Revit 重新导出。

## 备注
- 文件名重命名为"建筑类型_IFC版本.ifc"格式以便识别；内容字节与源仓库完全一致。
- 所有 Git LFS 指针文件已通过 `https://github.com/.../raw/refs/heads/main/...` 端点解析为真实 IFC 内容。
- 调研报告见上级目录 `taskrequest/ifc_field_fill_rate.md`。
