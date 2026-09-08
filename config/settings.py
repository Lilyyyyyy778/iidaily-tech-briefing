import os
from crewai import LLM
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    OUTPUT_DIR = "output"
    HTML_FILE = "daily-tech-briefing.html"
    CATEGORIES = ["AI", "产品发布", "行业动态", "融资并购", "技术趋势"]

    if not DEEPSEEK_API_KEY:
        raise RuntimeError("缺少 DEEPSEEK_API_KEY，请在项目根目录的 .env 文件中配置")

    LLM = LLM(
        model="deepseek/deepseek-chat",
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        temperature=0.2,
    )

settings = Settings()
