---
name: mathmodel-docx-adapter
description: 用户明确要求 Word 数学建模论文时，调用已安装的文档工具并按当届模板构建、渲染和核验 DOCX。
---

# Word 工具接口

这是本仓库独立编写的接口说明，不附带上游专有 Word 脚本。不要调用旧版的 paper_format.py、equations.py 或 office/validate.py，本版不提供这些程序。

优先使用当前环境的文档技能并读取其说明；独立环境可安装 python-docx，按当届官方模板构建。已有 LaTeX 主稿时，可用单独安装的 Pandoc 转换为 Word 初稿，随后核对模板、公式、引文和交叉引用。公式应为可编辑的 OMML，表格应可编辑；数值和图片来自已运行结果。

使用可用的 Word 或 LibreOffice 实际渲染 DOCX 为 PDF，检查分页、图表、页眉页脚、匿名与正文页数。工具或字体缺失时如实报告，不能声称已完成视觉验收。记录实际工具、版本、命令与检查结果，同源 PDF/DOCX 的结论和数值应一致。
