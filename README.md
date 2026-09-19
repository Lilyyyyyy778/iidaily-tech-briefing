# 每日科技简报站 - AI 多 Agent 自动化系统

> 基于 CrewAI  多 Agent 架构的自动化科技新闻简报生成系统
> 
点击这个！直接看！公网地址：https://lilyyyyyy778.github.io/iidaily-tech-briefing/
> 
## 系统架构

```
确定性采集          内容整理 Agent        写作 Agent          质检 Agent
(Serper 搜索)  ->   (Collector)     ->   (Writer)     ->   (Checker)
      \                                                          /
       \------------------  Python 渲染   -----------------/
```



## 技术栈

- Agent 框架: CrewAI 
- LLM: DeepSeek-V4(通过环境变量配置)
- 搜索: Serper API
- 部署: GitHub Actions -> GitHub Pages


