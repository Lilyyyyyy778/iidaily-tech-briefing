# 每日科技简报站 - AI 多 Agent 自动化系统

> 基于 CrewAI 1.x 多 Agent 架构的自动化科技新闻简报生成系统

## 系统架构

```
信息搜索 Agent -> 内容生成 Agent -> 质检审核 Agent
   (Collector)      (Writer)          (Checker)
```

## 技术栈

- Agent 框架: CrewAI 1.x
- LLM: DeepSeek-V3 (通过环境变量配置)
- 搜索: Serper API
- 部署: GitHub Actions -> GitHub Pages

## 快速开始

### 1. 配置环境变量

复制 .env.example 为 .env，填入你的 API Key：

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
```

## 环境变量

| 变量名 | 说明 | 获取方式 |
|--------|------|---------|
| DEEPSEEK_API_KEY | DeepSeek API 密钥 | platform.deepseek.com |
| SERPER_API_KEY | Serper 搜索 API | serper.dev |

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
