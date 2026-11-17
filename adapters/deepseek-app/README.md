# DeepSeek App 数学建模使用包

这是为 DeepSeek App 对话准备的资料包，通过上传文件使用，无需配置 API Key。文件已准备好，但不表示已绑定你的 DeepSeek 账号或已上传到手机。

下载完整使用包：[GitHub 最新发布页](https://github.com/yanzhan13149/mathmodel-competition-skill/releases/latest)。解压后，首次只需上传 `上传到DeepSeek.txt` 与赛题附件。

## 第一次使用

1. 在 DeepSeek App 新建对话，上传本目录的 **`上传到DeepSeek.txt`**，再上传当场比赛的题目 PDF 和数据附件。若 App 未接收 TXT，可以打开文件并将其文字粘贴到对话中。
2. 复制 **`开场提示词.txt`** 的“第一次开赛”部分发给它；把已知的竞赛届次、队员分工、截止时间写上，未知信息可以留空。
3. 让它先检查实际读到了哪些文件，再做选题、拆题和建模。需要更详细流程时，按任务上传 `阶段卡/` 中对应文件，不必一次上传整库。
4. 求解代码保存到电脑运行，将真实结果表、运行记录或完整报错传回 App，再分析、画图和写作。具体见 `代码运行指南.txt`。
5. 阶段结束让它按 `接力记录模板.txt` 整理进度。将这段记录保存到手机或电脑；换对话时重新上传总控文件、最新接力记录和必要的结果文件。

首次只需总控文件、题目和必要附件。ZIP 用于下载和转移，解压后上传里面的 TXT，不依赖 App 能否读取压缩包。不要用 Codex 的安装按钮代替 App 上传，也不要假定发送 GitHub 链接会加载整个仓库。

## 两端分别做什么

| DeepSeek App 中 | 电脑或队伍成员执行 |
|---|---|
| 题目分析、模型推导、代码草稿、结果解释、论文草稿与自查 | 安装依赖、保存代码、实际运行、检查结果、编译或渲染论文、保存接力记录 |
| 有可用联网功能时核对官方规则与原始文献 | App 无法访问时补充官方文件，复核最终提交要求 |
| 列出需要复核的证据与问题 | 独立复算、成员复核与实际提交 |

本模式不把同一对话的自查声称为独立子代理验收。缺少执行记录、独立复核或官方来源的环节保持待完成。

## 从仓库重新生成使用包

Windows 可双击根目录 `生成DeepSeekApp使用包.cmd`，默认在仓库旁生成 `DeepSeekApp使用包/` 和同名 ZIP。已存在时会停止，不覆盖你添加的比赛文件。

也可以在仓库根目录执行：

```powershell
python scripts/export_deepseek_app.py ../DeepSeekApp使用包 --zip
# 按需附带国赛历史规则基线；它仍需在实际比赛时重新核验
python scripts/export_deepseek_app.py ../DeepSeekApp国赛包 --competition cumcm --zip
# 从已有比赛目录附带只读状态快照；不会自动附带数据、代码或结果
python scripts/export_deepseek_app.py ../DeepSeekApp续聊包 --workspace ../my-cumcm --zip
```

`--competition` 也支持 `mcm`、`diangong`。`--workspace` 只导出已有状态中的选定字段，不修改原项目。导出位置必须在技能仓库外；含有真实比赛进度的包保留在本地，按需要自行上传。

## 官方能力依据

DeepSeek 官方介绍了 App 的文件输入、联网搜索和阅读链接功能：[官方说明](https://api-docs.deepseek.com/zh-cn/news/news261113/)。本资料包没有在你的私人 App 会话中实测；按钮、上传格式或额度以实际 App 为准。上传后先让模型列出已读取的文件与缺失项，解析失败时补传关键页面或直接粘贴文字。

流程来自本仓库的建模工作流，App 版将文件落盘、脚本运行和独立门禁改为显式的人工交接。来源与许可见仓库根目录 `SOURCES.md`、`LICENSE`，导出的使用包中保存在 `来源与许可/`。
