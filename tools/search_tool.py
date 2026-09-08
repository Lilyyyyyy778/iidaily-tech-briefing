from crewai.tools import BaseTool
from datetime import datetime, timedelta
import requests

class SearchTool(BaseTool):
    name: str = "search_tech_news"
    description: str = "搜索当天科技新闻，覆盖AI、产品发布、行业动态、融资并购、技术趋势等领域"

    def _run(self, query: str = "科技新闻", date: str = None) -> str:
        if not date:
            date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        api_key = self._get_api_key()
        url = "https://google.serper.dev/search"

        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }

        data = {
            "q": f"{query} {date}",
            "gl": "cn",
            "hl": "zh-cn",
            "num": 10
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=15)
            results = response.json()

            news_list = []
            for item in results.get("organic", []):
                news_list.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "date": date,
                    "source": item.get("source", "未知")
                })

            return str(news_list)
        except Exception as e:
            return f"搜索失败: {e}"

    def _get_api_key(self):
        import os
        return os.getenv("SERPER_API_KEY", "")

search_tool = SearchTool()
