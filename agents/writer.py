from crewai import Agent, Task

from config.settings import settings


class WriterAgent:
    def __init__(self):
        self.agent = Agent(
            role="科技简报主编",
            goal="把采集到的原始新闻整理成结构清晰、摘要精炼的简报数据",
            backstory=(
                "你是一位资深科技媒体主编，擅长把零散新闻归纳成简洁易读的简报。\n"
                "你只做编辑与润色，不会编造事实，也不会改动任何原始链接。"
            ),
            llm=settings.LLM,
            verbose=True,
        )

    def create_task(self, date, context=None):
        return Task(
            description=f"""
            基于上一步采集到的新闻数据，整理并润色出 {date} 的最终科技简报。

            要求：
            1. 保持原有分类（AI、产品发布、行业动态、融资并购、技术趋势）；
            2. 每条新闻输出 title、summary、source、link 四个字段，其中
               summary 用中文重写为 100 字以内的精炼摘要，link 必须与原始数据完全一致；
            3. 删除重复、无价值或缺少链接的条目。

            输出要求：只输出一个 JSON 对象，键为分类名、值为新闻数组，
            不要输出任何解释文字，也不要用 Markdown 代码块包裹。
            """,
            agent=self.agent,
            expected_output="按分类分组的 JSON 对象（每条包含 title/summary/source/link）",
            context=context or [],
        )
