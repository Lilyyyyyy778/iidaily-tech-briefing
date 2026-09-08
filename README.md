# 每日科技简报站 - AI 多 Agent 自动化系统

> 基于 CrewAI 1.x 多 Agent 架构的自动化科技新闻简报生成系统
> 
点击这个公网地址查看！！：https://lilyyyyyy778.github.io/iidaily-tech-briefing/

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


