# 每日科技简报站 - AI 多 Agent 自动化系统

> 基于 CrewAI 1.x 多 Agent 架构的自动化科技新闻简报生成系统
点击这个！直接看！公网地址：https://lilyyyyyy778.github.io/iidaily-tech-briefing/
> 
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


