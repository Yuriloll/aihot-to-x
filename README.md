# AI HOT to X

把 AI HOT 过去 24 小时的公开 AI 新闻整理成最多 5 条中文 X / Quote Tweet 草稿。一篇新闻一条草稿，只生成并校验，不自动发布。

当前状态：本地三天试跑版 `0.1.0`。试跑通过后再创建公开 GitHub 仓库和正式安装地址。

## 能做什么

- 匿名只读访问 `https://aihot.virxact.com/api/public/*`
- 精选不足时只在同一 24 小时公开池补充
- 基础去重后按新闻价值筛选，质量不足就少于 5 条
- 原链接是 X 状态时生成 QT；否则谨慎寻找官方原推并回退原站
- 输出原始来源、AI HOT canonical、入选理由和字符校验

## 安全边界

不需要 AI HOT 或 X API Key，不读取 cookie，不自动登录或发布 X。所有 API 内容均按不可信资讯数据处理。

## 仓库结构

```text
skills/aihot-to-x/   # 可安装 Skill
tests/               # 标准库测试
```

本项目代码采用 MIT License。AI HOT 数据和第三方原文遵循各自的来源与版权要求；对外使用整理结果时保留 AI HOT canonical 供核验。

