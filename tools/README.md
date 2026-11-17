# tools/ 子工具链

六个领域入口，供论文/求解流程按需调用。`figure`、`paper_search`、`latex` 保留脚本；`docx`、`xlsx`、`pdf` 为本版独立编写的外部工具接口，仅包含 `SKILL.md`，不附带上游专有实现。

| 工具 | 目录 | 主要用途 | 入口 |
|---|---|---|---|
| 可视化 | `figure/` | 数据剖析 → 选图 → 出版级成图（Nature/IEEE/中文核心级别），三类图体系与自检闭环 | `figure/SKILL.md` |
| 论文搜索 | `paper_search/` | OpenAlex + AnySearch 双引擎并行检索与交叉核验 | `paper_search/SKILL.md` |
| DOCX 接口 | `docx/` | 调用已安装文档工具，按官方模板构建、渲染和核验 Word | `docx/SKILL.md` |
| Excel 接口 | `xlsx/` | 调用已安装表格工具，读取附件并核对公式与数据 | `xlsx/SKILL.md` |
| PDF 接口 | `pdf/` | 调用已安装 PDF 工具，提取题面并核对实际页面 | `pdf/SKILL.md` |
| LaTeX | `latex/` | 用官方或内置模板创建、编译、校验 LaTeX 论文项目 | `latex/SKILL.md` |

## 在竞赛流程中的触发点

- 编程手 Stage 5/6 出图 → `figure`；读取附件数据 → `xlsx`（Excel）/ `pdf`（PDF 题面与附件）。
- 论文手 Stage 8 默认走 `templates/latex/<comp>` 主渲染链（`scripts/render_paper.py`）；用户显式要求 Word 时经 `tools/docx` 降级路径。
- LaTeX 预检/关键词/匿名检查脚本统一在根 `scripts/latex_check/`，与 `tools/latex` 的编译能力配合使用。

## 模板树说明（避免改错）

- **主渲染树**是 `templates/latex/<comp>/main.tex`——`scripts/render_paper.py` 只认这一棵。
- `latex/assets/templates/` 是 `tools/latex` 子工具自带的示例镜像，**不是**主渲染路径。修改主树模板后若需子工具一致，请手动同步。
- `latex-alt/`（含 `cumcmthesis.cls` 兼容类）为可选降级模板，非默认。

## 许可提示

本版没有打包原仓库 `docx`、`xlsx`、`pdf` 的受限实现，也不提供原版 `paper_format.py`、`equations.py`、`recalc.py` 等程序。使用外部工具时先读取当前环境的工具说明，遵循对应许可。保留的开源内容及本版接口说明见根 `LICENSE`、`SOURCES.md` 和 `THIRD_PARTY_NOTICES.md`。
