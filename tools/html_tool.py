from crewai.tools import BaseTool
from datetime import datetime
import json

class HTMLTool(BaseTool):
    name: str = "generate_html"
    description: str = "将新闻数据生成为响应式HTML简报页面"

    def _run(self, briefings_str: str = "{}", date: str = "") -> str:
        try:
            briefings = json.loads(briefings_str.replace("'", '"'))
        except Exception:
            briefings = {}

        if isinstance(briefings, list):
            briefings = self._group_list_by_category(briefings)

        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        return self._generate_html(briefings, date)

    def _group_list_by_category(self, items):
        grouped = {
            "AI": [],
            "产品发布": [],
            "行业动态": [],
            "融资并购": [],
            "技术趋势": []
        }

        if not isinstance(items, list):
            return grouped

        for item in items:
            if not isinstance(item, dict):
                continue
            category = item.get("category", "技术趋势")
            if category not in grouped:
                category = "技术趋势"
            grouped[category].append(item)

        return grouped

    def _generate_html(self, briefings, date):
        if isinstance(briefings, list):
            briefings = self._group_list_by_category(briefings)
        if not isinstance(briefings, dict):
            briefings = {}

        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日科技简报 - {date}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f5f5;
            margin: 0;
            line-height: 1.6;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .category {{
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .card-title {{
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        .card-summary {{
            color: #666;
            margin-bottom: 10px;
        }}
        .card-link {{
            color: #667eea;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>每日科技简报</h1>
        <div>{date}</div>
    </div>
    <div class="container">
        {self._generate_categories(briefings)}
    </div>
</body>
</html>"""

    def _generate_categories(self, briefings):
        if isinstance(briefings, list):
            briefings = self._group_list_by_category(briefings)
        if not isinstance(briefings, dict):
            return ""

        badge_map = {
            "AI": "AI",
            "产品发布": "产品发布",
            "行业动态": "行业动态",
            "融资并购": "融资并购",
            "技术趋势": "技术趋势"
        }

        html = ""
        for category, items in briefings.items():
            if not isinstance(items, list) or not items:
                continue
            html += f'<div class="category"><h2>{badge_map.get(category, category)}</h2>'
            for item in items:
                if not isinstance(item, dict):
                    continue
                html += f'''
                <div class="card">
                    <div class="card-title">{item.get("title", "无标题")}</div>
                    <div class="card-summary">{item.get("summary", "暂无摘要")}</div>
                    <div><a class="card-link" href="{item.get("link", "#")}" target="_blank">阅读原文</a></div>
                </div>
                '''
            html += "</div>"
        return html

html_tool = HTMLTool()
