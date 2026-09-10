import json

from crewai import Agent, Task

from config.settings import settings
from tools.search_tool import search_tool


class CollectorAgent:
    def __init__(self):
        self.agent = Agent(
            role="资深科技记者",
            goal="搜集并整理当天最新、最重要的科技新闻",
            backstory=(
                "你是一位经验丰富的科技记者，擅长从海量信息中筛选有价值的科技新闻。\n"
                "你关注 AI、产品发布、行业动态、融资并购、技术趋势等领域，"
                "会确保新闻的时效性、去重和来源可靠，并把结果整理成严格的结构化数据。"
            ),
            tools=[search_tool],
            llm=settings.LLM,
            verbose=True,
        )

    def create_task(self, date, raw_news=None):
        if raw_news:
            source_hint = (
                "以下是系统预抓取的候选新闻（JSON），请以此为主要素材进行筛选、去重、分类与整理：\n"
                f"{json.dumps(raw_news, ensure_ascii=False)}"
            )
            tool_hint = "候选新闻已经提供，请直接整理，不要重复调用搜索工具。"
        else:
            source_hint = "请调用 search_tech_news 工具，分别针对下面 5 个分类搜索新闻。"
            tool_hint = ""

        return Task(
            description=f"""
            整理 {date} 的科技新闻，覆盖分类：AI、产品发布、行业动态、融资并购、技术趋势。

            要求：
            1. 每条新闻必须包含 title、summary、source、link 四个字段；
            2. summary 用中文概括，控制在 100 字以内；
            3. 同一事件只保留最权威来源，link 必须是可直接访问的 http/https 地址；
            4. 每个分类保留 3-6 条最有价值的新闻。

            {source_hint}
            {tool_hint}

            输出要求：只输出一个 JSON 对象，键为分类名、值为新闻数组，
            不要输出任何解释文字，也不要用 Markdown 代码块包裹。
            """,
            agent=self.agent,
            expected_output=(
                '按分类分组的 JSON，例如 {"AI": [{"title": "标题", "summary": "摘要", '
                '"source": "来源", "link": "https://..."}]}'
            ),
        )
