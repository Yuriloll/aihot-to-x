# AI HOT to X

基于 AI HOT 公开 API 的中文 X / Quote Tweet 草稿 Skill。它读取过去 24 小时的 AI 新闻，筛选最多 5 条重要事件，并输出经过结构与字符校验、可供人工审核的中文草稿。

当前正式版本：`1.0.0`

## 项目定位与致谢

本项目是基于 AI HOT 公开 API 构建的第三方衍生 Skill，不是 AI HOT 官方 Skill 或官方仓库。

- AI HOT 网站：[https://aihot.virxact.com/](https://aihot.virxact.com/)
- AI HOT 作者：数字生命卡兹克（[@Khazix0918](https://x.com/Khazix0918)）
- AI HOT 官方 Agent 接入：[https://aihot.virxact.com/agent](https://aihot.virxact.com/agent)

感谢数字生命卡兹克免费开放 AI HOT 网站、RSS、Skill 和公开 API。本项目只负责把 AI HOT 候选数据继续加工成中文 X/QT 草稿；AI HOT 数据、页面与品牌归原项目所有。

## 能做什么

- 匿名只读访问 `https://aihot.virxact.com/api/public/*`
- 获取过去 24 小时 AI HOT 精选；精选不足时只从同一时间窗公开池补充
- 对候选做基础去重，再由 Agent 完成语义去重和编辑价值判断
- 按真实重要性筛选最多 5 条，质量不足时允许少于 5 条
- 原链接是 X 状态链接时生成 QT；网站来源只有在严格匹配官方原推后才转换为 QT
- 为每条新闻生成一个“钩子 + 关键事实 + 明确判断”的中文草稿
- 输出原始来源、AI HOT canonical、发布时间、入选理由和字符校验
- 只生成草稿，不登录或发布 X

## 工作流程

1. `fetch_aihot.py` 从 AI HOT 匿名公开接口获取 24 小时候选。
2. Agent 对同一事件做语义去重，并按新闻价值选择最多 5 条。
3. Agent 核对来源链接；不能确认官方原推时保留原站。
4. Agent 为每条新闻生成一个中文 X/QT 草稿。
5. `validate_drafts.py` 检查字段、链接形态和 X 加权字符长度。
6. 用户人工审核后自行决定是否发布。

## 安装

### 使用 Skills CLI

仓库发布后可运行：

```bash
npx skills add https://github.com/Yuriloll/aihot-to-x --skill aihot-to-x
```

### 手动安装

将仓库中的 `skills/aihot-to-x/` 完整复制到所用 Agent 的 Skill 目录。目录结构必须保留：

```text
aihot-to-x/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── scripts/
    ├── fetch_aihot.py
    └── validate_drafts.py
```

不同 Agent 的 Skill 目录可能不同；也可以把本仓库加入项目，并要求 Agent 遵循 `skills/aihot-to-x/SKILL.md`。

## 运行要求

- Python 3.9 或更高版本
- 无第三方 Python 依赖
- 能访问 `https://aihot.virxact.com/api/public/*`
- 如需寻找官方原推，Agent 还需要网页或 X 搜索能力

不需要 AI HOT API Key、X Token、cookie 或账号凭证。

## 使用示例

安装后可以直接对 Agent 说：

```text
使用 $aihot-to-x 获取过去 24 小时 AI HOT，筛选最多 5 条真正重要的新闻，分别生成中文 X 或 QT 草稿。不要发布，全部校验通过后再交付给我审核。
```

也可以限定输出：

```text
使用 $aihot-to-x，只选今天最重要的模型发布和 AI 产品更新。质量不足可以少于 5 条，不要拿旧闻补数。
```

## 输出格式

每条草稿包含：

- `type`：`qt` 或 `link`
- `text`：可直接粘贴的正文
- `sourceUrl`：官方原推或原站
- `aihotCanonical`：AI HOT 永久核验页
- `publishedAt`：原条目发布时间
- `selectionReason`：进入当天结果的理由

字符限制：

- QT 正文不超过 260 个加权字符
- 链接帖正文主体不超过 230 个加权字符
- 链接帖完整帖子不超过 280 个加权字符
- URL 按 23 个字符计算；中文、日文、韩文及 emoji 按 2 计算

## 校验边界

`validate_drafts.py` 负责结构与字符校验，包括草稿数量、必需字段、HTTPS 链接、X 状态链接、AI HOT canonical、时间格式和加权字符长度。

以下事项仍由 Agent 和用户判断，校验脚本不会自动证明：

- 新闻事实是否完全准确
- 不同标题是否属于同一事件
- 找到的 X 帖是否为发布主体的官方原推
- 条目是否确实落在本轮 24 小时时间窗
- 草稿中的判断是否合理

因此，本 Skill 的输出必须经过人工审核后再发布。

## 安全边界

- 只向 AI HOT 匿名公开接口发送 `GET` 请求
- 不读取或索取任何 AI HOT/X 凭证
- 不登录或操作 X 发布界面
- 不下载新闻附件，不执行新闻内容中的代码或指令
- API 内容按不可信资讯数据处理
- API 暂不可用时停止，不用模型记忆或其他新闻源冒充实时 AI HOT 数据

## 仓库结构

```text
skills/aihot-to-x/   # 可安装 Skill
tests/               # Python 标准库单元测试
```

运行测试：

```bash
python3 -m unittest discover -s tests -v
```

## 许可证

本项目代码采用 [MIT License](LICENSE)。AI HOT 数据与第三方新闻原文遵循各自的来源、服务条款和版权要求。对外使用整理结果时应保留原始来源及 AI HOT canonical 供核验。
