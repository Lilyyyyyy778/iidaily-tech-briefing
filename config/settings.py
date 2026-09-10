import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek/deepseek-chat")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")

    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
    HTML_FILE = os.getenv("HTML_FILE", "daily-tech-briefing.html")
    INDEX_FILE = "index.html"

    CATEGORIES = ["AI", "产品发布", "行业动态", "融资并购", "技术趋势"]

    # 每个分类的搜索关键词，用于确定性采集（也是 AI Agent 失联时的兜底数据源）
    CATEGORY_QUERIES = {
        "AI": "人工智能 大模型 最新进展",
        "产品发布": "科技公司 新品发布",
        "行业动态": "互联网 科技 行业动态",
        "融资并购": "科技公司 融资 并购",
        "技术趋势": "技术趋势 开源项目",
    }

    MAX_ITEMS_PER_CATEGORY = int(os.getenv("MAX_ITEMS_PER_CATEGORY", "6"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "20"))

    def build_llm(self):
        """仅在配置了 DEEPSEEK_API_KEY 时构建 LLM；缺失时返回 None，走兜底流程。"""
        if not self.DEEPSEEK_API_KEY:
            print("[warn] 未配置 DEEPSEEK_API_KEY，将跳过 AI Agent，直接使用兜底采集流程。")
            return None
        from crewai import LLM

        return LLM(
            model=self.DEEPSEEK_MODEL,
            api_key=self.DEEPSEEK_API_KEY,
            base_url=self.DEEPSEEK_BASE_URL,
            temperature=0.2,
        )


settings = Settings()
settings.LLM = settings.build_llm()
