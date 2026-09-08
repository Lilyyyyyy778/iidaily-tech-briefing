from crewai import Agent
from config.settings import settings
from tools.html_tool import html_tool

class WriterAgent:
    def __init__(self):
        self.agent = Agent(
            role="前端开发专家",
            goal="将新闻内容转化为美观的响应式HTML简报页面",
            backstory="""
            你是一位资深前端开发工程师，擅长信息可视化和用户体验设计。
            你能将枯燥的新闻列表转化为清晰、美观、易读的卡片式布局。
            你注重移动端适配和交互细节。
            """,
            tools=[html_tool],
            llm=settings.LLM,
            verbose=True
        )

    def create_task(self, date):
        from crewai import Task
        return Task(
            description=f"""
            基于收集到的新闻数据，生成 {date} 的科技简报HTML页面。

            要求：
            1. 按分类展示：AI、产品发布、行业动态、融资并购、技术趋势
            2. 每条新闻用卡片展示：标题 + 摘要 + 来源 + 原文链接
            3. 添加分类标签和视觉区分
            4. 响应式设计，适配手机和电脑
            5. 顶部显示生成时间和"AI自动生成"标识

            使用 generate_html 工具生成HTML页面。
            """,
            agent=self.agent,
            expected_output="完整的HTML字符串"
        )
