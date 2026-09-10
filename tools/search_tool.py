"""Serper 搜索封装。

既可作为 CrewAI 工具被 Agent 调用，也可被普通 Python 代码直接调用，
用于确定性的新闻采集（AI Agent 不可用时的兜底数据源）。
"""
import json
import os
from datetime import datetime, timedelta

import requests
from crewai.tools import BaseTool

from config.settings import settings

SERPER_URL = "https://google.serper.dev/search"


def _resolve_date(date=None):
    return date or (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


def search_news(query, date=None, num=10):
    """调用 Serper 搜索新闻，返回结构化列表；任何异常都返回空列表。"""
    date = _resolve_date(date)
    api_key = settings.SERPER_API_KEY or os.getenv("SERPER_API_KEY", "")
    if not api_key:
        print("[warn] 未配置 SERPER_API_KEY，跳过搜索。")
        return []

    payload = {"q": f"{query} {date}", "gl": "cn", "hl": "zh-cn", "num": num}
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}

    try:
        response = requests.post(
            SERPER_URL,
            headers=headers,
            json=payload,
            timeout=settings.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        print(f"[warn] 搜索 '{query}' 失败：{exc}")
        return []

    news = []
    seen = set()
    for item in (data.get("news") or []) + (data.get("organic") or []):
        title = (item.get("title") or "").strip()
        link = (item.get("link") or item.get("url") or "").strip()
        if not title or not link or link in seen:
            continue
        seen.add(link)
        news.append(
            {
                "title": title,
                "summary": (item.get("snippet") or item.get("description") or "").strip(),
                "source": (item.get("source") or item.get("site") or "").strip() or "未知来源",
                "link": link,
            }
        )
    return news


def collect_news(date=None):
    """按预置分类确定性地采集新闻，返回 ``{分类: [新闻]}``。"""
    date = _resolve_date(date)
    limit = settings.MAX_ITEMS_PER_CATEGORY
    briefings = {}
    for category in settings.CATEGORIES:
        query = settings.CATEGORY_QUERIES.get(category, category)
        items = search_news(query, date=date, num=limit * 2)[:limit]
        if items:
            briefings[category] = items
    return briefings


class SearchTool(BaseTool):
    name: str = "search_tech_news"
    description: str = "按关键词搜索当天科技新闻，返回 JSON 数组（字段：title/summary/source/link）"

    def _run(self, query: str = "科技新闻", date: str = "") -> str:
        items = search_news(query, date=_resolve_date(date or None))
        return json.dumps(items, ensure_ascii=False)


search_tool = SearchTool()
