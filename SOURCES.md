# 来源说明

## 本个人比赛版本

- 维护者：`yanzhan13149`。
- 发布仓库：[yanzhan13149/mathmodel-competition-skill](https://github.com/yanzhan13149/mathmodel-competition-skill)。
- 直接来源：[rootkiller6788/mathmodel-skill](https://github.com/rootkiller6788/mathmodel-skill)，基线提交 `a5f4d60c7db2a98e1284b1995a1aaaaa008facd5`，版本 `6.1.1`。
- 本版新增：Windows 安装入口、完整技能安装器、独立比赛项目初始化、最小依赖、中文快速指南与相关测试；同步修正论文手的默认交付说明，使其遵循根入口的 LaTeX/PDF 默认路线。
- v6.3.0 新增 DeepSeek App 上传资料、阶段任务卡、人工接力记录与导出器。App 版单独说明本地执行和独立验收边界，不声称已绑定 App 账号或自动运行工具。
- `tools/docx`、`tools/pdf`、`tools/xlsx` 的原代码和专有 Skill 未纳入本版，以独立编写的接口说明替代。新仓库使用干净历史，避免通过旧提交再次发布这些文件。
- 保留来源信息与原有 MIT 声明。本版插件署名表示维护身份，不将上游工作声称为原创。

## 直接来源仓库记录的原始来源

本 Skill（`mathmodel-skill`）由以下三个 MIT 许可的开源 skill 的核心内容合并而成。合并后仓库以自身 MIT 许可证发布；上游组件仍遵循其原始 MIT 声明，未被重新授权。

| 源 | 作者 / 版本 | 仓库 | 并入本 Skill 的部分 |
|---|---|---|---|
| mathmodel-skill | handsomeZR-netizen · v6.1 | [github.com/handsomeZR-netizen/mathmodel-skill](https://github.com/handsomeZR-netizen/mathmodel-skill) | 10 阶段项目流程、L1–L4 反馈层、三竞赛包（cumcm/mcm/diangong）、`decision_log.json` 状态持久化、确定性评分脚本 |
| math-modeling-skill | XiaoMaColtAI · v1.2 | [github.com/XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill) | 三角色执行引擎（建模手/编程手/论文手）、5 门禁质检、7 类算法资料、`tools/` 工具链（figure/paper_search/docx/xlsx/pdf/latex） |
| mathmodel-latex-skill | wangling-miao · v1.0.8 | [github.com/wangling-miao/mathmodel-latex-skill](https://github.com/wangling-miao/mathmodel-latex-skill) | LaTeX 编译预检、匿名检查、CUMCM 优秀论文风格规则、引用/关键词校验 |

## 许可

- 本仓库可再分发的内容：MIT（见 [LICENSE](./LICENSE)），保留 `rootkiller6788` 声明，并加入 `yanzhan13149` 对本版修改的声明。
- 上游三个源各自保留原始 MIT 版权声明，未被本仓库重新授权。
- 完整第三方合规说明见 [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md)。
