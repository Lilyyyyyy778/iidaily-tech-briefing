from crewai import Agent, Task

from config.settings import settings
from tools.check_tool import check_tool


class CheckerAgent:
    def __init__(self):
        self.agent = Agent(
            role="质量控制专家",
            goal="确保简报内容准确、链接有效、结构完整",
            backstory=(
                "你是一位严格的质量控制专家，对细节有极高的要求。\n"
                "你会验证每条新闻的链接是否可访问、字段是否完整，并明确指出问题。"
            ),
            tools=[check_tool],
            llm=settings.LLM,
            verbose=True,
        )

    def create_task(self, date, context=None):
        return Task(
            description=f"""
            对上一步整理好的 {date} 科技简报数据进行质量检查：

            1. 调用 check_links 工具检查所有原文链接是否可访问；
            2. 检查每条新闻是否包含 title、summary、source、link；
            3. 检查分类是否合理、是否存在重复条目。

            输出要求：输出一份简短的中文质检报告，包含
            「总体评价（通过/需修改）」「问题列表」「修改建议」三部分。
            """,
            agent=self.agent,
            expected_output="中文质检报告",
            context=context or [],
        )
