# 每日科技简报站 - AI 多 Agent 自动化系统

> 基于 CrewAI 1.x 多 Agent 架构的自动化科技新闻简报生成系统

## 系统架构

```
确定性采集          内容整理 Agent        写作 Agent          质检 Agent
(Serper 搜索)  ->   (Collector)     ->   (Writer)     ->   (Checker)
      \                                                          /
       \------------------  Python 渲染 HTML  -----------------/
```

数据流说明：

1. **确定性采集**：`tools/search_tool.py` 按分类调用 Serper，拿到结构化新闻（这一步不依赖大模型，保证永远有数据）。
2. **AI Agent 流水线**：Collector 负责筛选/去重/分类，Writer 负责润色中文摘要，Checker 负责链接与完整性质检。
3. **确定性渲染**：`tools/html_tool.py` 用纯 Python 把最终数据渲染成完整 HTML，**不经过大模型**，因此部署到 GitHub Pages 的一定是结构完整的页面。
4. 如果 AI Agent 出错（比如 API 限流/欠费），`main.py` 会自动回退到第 1 步的采集结果，页面仍然可以正常生成。

## 技术栈

- Agent 框架: CrewAI 1.x
- LLM: DeepSeek-V3 (通过环境变量配置)
- 搜索: Serper API
- 部署: GitHub Actions -> GitHub Pages

## 快速开始

### 1. 配置环境变量

复制 `.env.example` 为 `.env`，填入你的 API Key：

```bash
cp .env.example .env
# 编辑 .env 填入 Key
```

### 2. 安装依赖

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. 运行

```bash
python main.py
# 指定日期
python main.py 2026-09-09
```

生成结果会写入 `output/index.html` 与 `output/daily-tech-briefing.html`。

## 环境变量

| 变量名 | 说明 | 获取方式 |
|--------|------|---------|
| DEEPSEEK_API_KEY | DeepSeek API 密钥 | platform.deepseek.com |
| SERPER_API_KEY | Serper 搜索 API | serper.dev |
| DEEPSEEK_BASE_URL | 可选，默认 `https://api.deepseek.com` | - |
| MAX_ITEMS_PER_CATEGORY | 可选，每个分类最多保留几条，默认 6 | - |

> 缺少 `DEEPSEEK_API_KEY` 或 `SERPER_API_KEY` 时不会崩溃：程序会跳过对应的步骤，仍然生成可部署的页面。

## 自动化部署

工作流文件为 `.github/workflows/daily.yml`，每次手动运行或定时运行后，会自动生成 `output/index.html` 并部署到 GitHub Pages。

首次配置 GitHub 仓库：

1. 打开仓库 `Settings -> Secrets and variables -> Actions`，新增以下两个 Repository secrets：
   - `DEEPSEEK_API_KEY`
   - `SERPER_API_KEY`
2. 打开 `Settings -> Pages`，将 `Build and deployment -> Source` 设置为 `GitHub Actions`。
3. 推送代码后，打开仓库的 `Actions -> Daily Tech Briefing`，点击 `Run workflow` 手动执行一次。
4. 工作流成功后，在 `Settings -> Pages` 或工作流部署结果中打开网站地址。首页地址通常是：
   `https://<用户名>.github.io/<仓库名>/`

注意：GitHub Actions 中不能使用本地 `.env`，必须通过 Repository secrets 注入 API 密钥；不要把 `.env` 提交到仓库。

## 常见问题

**页面显示「结果不是完整 HTML」/ 只有一段提示文字？**
这是旧版本才会出现的问题：旧代码把「质检报告」当成了最终 HTML，并且渲染依赖大模型。
现在 HTML 由 `tools/html_tool.py` 确定性渲染，`main.py` 还会在 AI 失败时回退到采集数据，不会再出现占位页面。
