from crewai import Agent
from config.settings import settings
from tools.check_tool import check_tool

class CheckerAgent:
    def __init__(self):
        self.agent = Agent(
            role="质量控制专家",
            goal="确保生成的简报内容准确、链接有效、排版正确",
            backstory="""
            你是一位严格的质量控制专家，对细节有极高的要求。
            你会逐一验证每条新闻的链接是否可访问，内容是否完整，排版是否美观。
            发现问题时会明确指出并要求修复。
            """,
            tools=[check_tool],
            llm=settings.LLM,
            verbose=True
        )

    def create_task(self, date):
        from crewai import Task
        return Task(
            description=f"""
            对生成的 {date} 科技简报进行质量检查：

            检查项：
            1. 链接有效性：所有原文链接是否能正常访问（HTTP 200）
            2. 内容完整性：每条新闻是否有标题、摘要、来源
            3. 内容质量：摘要是否有实质内容
            4. 分类准确性：新闻是否被正确分类
            5. 排版检查：HTML结构是否完整，样式是否正确

            使用 check_links 工具检测链接有效性。
            输出格式：
            - 总体评价：通过/需修改
            - 问题列表（如有）
            - 修改建议（如有）
            """,
            agent=self.agent,
            expected_output="质检报告（JSON格式）"
        )
