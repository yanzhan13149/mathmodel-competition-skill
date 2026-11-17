---
name: 论文手
description: 根据数学建模竞赛题目、分析与真实代码结果装配 LaTeX/PDF 论文；用户明确要求时通过已安装文档工具生成 Word。
---

# 论文手

遵循根 `SKILL.md`：默认 LaTeX/PDF，Word 仅在明确需要时生成。本文件路径向上三层是 `SKILL_ROOT`；输入和输出位于用户的 `PROJECT_ROOT`，不修改技能资源。

## 输入与证据

读取题目及附件、`题目分析报告.md`、`术语表格.md`、可运行代码、真实结果表、原始/过程/结果图及已核验的文献。缺少关键输入时回到相应角色补齐，不编造数值、图片或引文。

先核验当届官方规则、语言、模板、页数、匿名和 AI 披露。优先使用当届官方模板；没有合适模板时用 `templates/latex/<competition>/main.tex` 的内置装配基线，并说明它不代表官方认可。历史经验、字数和图数目标不属于官方要求。

建立每个子问题的主张—证据映射，精确到公式、表格行列、图文件、代码输出或 DOI。长篇正文前按 `../../../references/Subagent调度.md` 执行独立 `W1` 证据大纲门禁，失败先补证据。保持摘要、正文、表格与图中的数值一致；引用必须打开原始出版页面核验。

## 构建与验收

1. 读取 `references/工作流程.md` 和对应竞赛 `paper_skeleton.md`，将共同正文写入 `PROJECT_ROOT/paper_workspace/`。
2. 默认使用根 `scripts/render_paper.py` 装配 `templates/latex/<competition>`；参数先查看 `--help`。使用完整官方 LaTeX 工程时再读取 `../../../tools/latex/SKILL.md`，按其初始化、绑定与编译程序操作，不混用两条装配链。
3. 中文竞赛使用 XeLaTeX，美赛使用 pdfLaTeX；当届官方模板有更具体要求时记录来源并遵循。实际编译后检查引用、图表、页数和匿名，保留真实执行命令及退出码。
4. 明确需要 Word 时读取 `../../../tools/docx/SKILL.md`，调用当前环境已安装的文档工具，按官方模板制作并实际渲染。不能调用本版未提供的旧专有脚本。双格式共用同一正文与证据源。
5. 打开实际生成的 PDF 逐页核对；使用 `scripts/latex_check/` 的引用、关键词、环境和 PDF 检查补充自动验证。缺少编译或渲染环境时明确报告尚未验证的环节。
6. 内容与用户要求的格式冻结后执行独立 `W2` 终检。检查当届规则、主张—证据、单位、图表引用、文献及实际版面。实质性修改后重跑受影响门禁。

未通过必要门禁不得声称终稿可提交。交付仅包括用户要求的源码和已验证论文，报告实际页数、关键检查结果与尚未解决的问题。

## 按需参考

| 任务 | 读取 |
|---|---|
| 开始写作 | `references/工作流程.md`、`references/章节模板.md` |
| Word | `references/论文格式规范.md`、`../../../tools/docx/SKILL.md` |
| 完整 LaTeX 工程 | `references/LaTeX格式规范.md`、`../../../tools/latex/SKILL.md` |
| 中文、摘要与结论 | `references/写作规范.md` |
| MCM/ICM | `references/英文化工作流.md` |
| 交付前 | `references/自审框架.md` |
