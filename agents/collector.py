from crewai import Agent
from config.settings import settings
from tools.search_tool import search_tool

class CollectorAgent:
    def __init__(self):
        self.agent = Agent(
            role="资深科技记者",
            goal="从互联网抓取当天最新、最重要的科技新闻",
            backstory="""
            你是一位经验丰富的科技记者，擅长从海量信息中筛选有价值的科技新闻。
            你关注AI、产品发布、行业动态、融资并购、技术趋势等领域。
            你会确保新闻的时效性和来源可靠性。
            """,
            tools=[search_tool],
            llm=settings.LLM,
            verbose=True
        )

    def create_task(self, date):
        from crewai import Task
        return Task(
            description=f"""
            搜索并收集 {date} 的科技新闻，覆盖以下维度：
            1. AI/人工智能最新进展
            2. 科技产品发布
            3. 互联网行业动态
            4. 融资并购信息
            5. 技术趋势和开源动态

            要求：
            - 每条新闻必须包含：标题、摘要（100字以内）、来源、链接
            - 去重：同一事件只保留最权威来源
            - 优先选择知名科技媒体
            - 必须输出按分类分组的 JSON 对象，格式如下：
              {{
                "AI": [...],
                "产品发布": [...],
                "行业动态": [...],
                "融资并购": [...],
                "技术趋势": [...]
              }}

            使用 search_tech_news 工具搜索新闻，返回结构化数据。
            """,
            agent=self.agent,
            expected_output="按分类分组的新闻JSON对象"
        )
