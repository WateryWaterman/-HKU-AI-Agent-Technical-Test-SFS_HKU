# HKU AI+BIM Team — Technical Assessment Invitation

> 来源：`reserch/task.pdf`（邮件正文，发件人 Jia Fu <junnaifj@hku.hk>，2026-07-03 17:48）
> 收件人：2172353152@qq.com
> 性质：香港大学建筑学院城市规划与设计系 AI+BIM 团队岗位的能力测试邀请

---

## 一、任务概述（Task）

在 **7 天内** 构建一个 **Web 微原型** 或 **智能 Agent**，用于对 **建筑模型 / 设计** 进行 **基础合规与合理性检查**（实现 **1–2 条规则** 即可）。

---

## 二、交付与提交（Submission）

| 项目 | 要求 |
| --- | --- |
| 交付内容 | 两个链接：① GitHub 仓库（含 **代码 + 提示词 prompts**）；② 3 分钟以内的 **演示/介绍视频** 链接 |
| 提交方式 | 邮件发送至 `junnaifj@hku.hk`，主题格式：`【HKU AI Agent Technical Test】姓名_学校` |
| 截止时间 | **2026 年 7 月 20 日 23:59** 之前完成全部交付 |
| 参与确认 | 需先回复邮件确认参与及提交时间线 |

---

## 三、提示与建议（Hints & Suggestions）

### 1. 检查内容（Audit Scope）
利用 AI 调研 **BIM/CAD 模型检查、IFC 结构、工程规范**（碰撞检测、消防安全、算量等）。
**只需实现 1–2 条规则，精炼优先**。候选示例：
- 几何碰撞（墙 / 梁 / 管道）geometric clashes (walls/beams/pipes)
- 疏散门净宽度检查 clear exit door width
- 房间到出口的疏散距离 room-to-exit travel distances
- 模型属性完善（如名称 / FireRating）model property enrichment

### 2. 数据格式（Data Formats）
均可接受：真实 IFC 模型、CAD 图纸、简化 JSON 表示、AutoCAD/Revit 导出。
需 **自行调研并搜集** sample、模型，或用 AI 生成测试数据集。

### 3. 实现形式（Implementation Form）
Web 工具、智能 Agent、本地脚本均可。**技术栈完全自由**（如 `Python + ifcopenshell`、JS、`LangChain / Claude Agent` 等）。

### 4. 考察重点（Evaluation Focus）
**不要追求完美**，核心指标 = **"可运行 + 有思考 + 有品味"（functional + thoughtful + tasteful）**：
- 代码结构清晰
- 人机交互友好、实用
- 设计决策背后有工程判断力
- 结果可视化真正有帮助

### 5. 其他（Other Notes）
**更看重学习速度、工程判断力与潜力**，而非已有的建筑领域知识。

---

## 四、最终要求（Final Requirements — 针对性清单）

要做的事可以拆成以下硬性要求，便于后续针对性调研：

1. **产出物 1：GitHub 仓库**
   - 含可运行代码
   - 含使用的 **prompts（提示词）** ← 必须包含
2. **产出物 2：演示视频**（≤ 3 分钟）
3. **功能底线**：对建筑模型执行 **1–2 条** 合规/合理性检查规则
4. **数据来源**：自行获取或 AI 生成（IFC / CAD / JSON / Revit 导出均可）
5. **形态**：Web 微原型 或 智能 Agent（二选一或结合）
6. **技术栈**：自由选择，但需体现工程判断
7. **质量取向**：精炼 > 完美；重交互、可视化、代码清晰度
8. **时间线**：7 天内完成，**2026-07-20 23:59 前提交**

---

## 五、建议的下一步调研方向（待确认后展开）

为满足"有思考 + 有品味"，建议先就以下主题做针对性调研：

- **A. IFC 文件结构与解析**：`ifcopenshell` 用法、IFC 实体（IfcWall/IfcBeam/IfcDoor/IfcSpace/IfcRel*）关系
- **B. 选定规则的技术可行性**：从示例中选 1–2 条（建议优先"碰撞检测"或"疏散门净宽"，数据易得、可视化直观）
- **C. 数据集来源**：公开 IFC sample（如 buildingSMART、IFC4 测试套件、Github 上的 IfcOpenHouse / Duplex 等）
- **D. 技术栈选型**：Web 前端可视化（Three.js / xeokit / web-ifc）+ 后端（FastAPI + ifcopenshell）+ AI Agent（LangChain / Claude / OpenAI）
- **E. 可视化方案**：3D 模型渲染 + 问题高亮标注
- **F. 人机交互形态**：对话式 Agent 还是表单式工具？如何体现"AI-native"

---

*说明：原 PDF 中文页存在字体编码乱码（部分标点/数字缺失），上文已根据英文原文与可读中文整合校对。*
