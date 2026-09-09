from crewai.tools import BaseTool
from datetime import datetime
import json


class HTMLTool(BaseTool):
    name: str = "generate_html"
    description: str = "将新闻数据生成为响应式HTML简报页面"

    def _run(self, briefings_str: str = "{}", date: str = "") -> str:
        briefings = self._parse_briefings(briefings_str)

        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        return self._generate_html(briefings, date)

    def _parse_briefings(self, briefings_str):
        """
        兼容以下输入：
        - JSON 字符串
        - Python dict 的字符串形式
        - list
        - dict
        - 其他异常值
        """
        if briefings_str is None:
            return {}

        if isinstance(briefings_str, dict):
            return briefings_str

        if isinstance(briefings_str, list):
            return self._group_list_by_category(briefings_str)

        if not isinstance(briefings_str, str):
            return {}

        text = briefings_str.strip()
        if not text:
            return {}

        try:
            briefings = json.loads(text)
        except Exception:
            try:
                briefings = json.loads(text.replace("'", '"'))
            except Exception:
                return {}

        if isinstance(briefings, list):
            return self._group_list_by_category(briefings)

        if isinstance(briefings, dict):
            return briefings

        return {}

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

        categories_html = self._generate_categories(briefings)

        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日科技简报 - {date}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f5f5;
            line-height: 1.6;
            color: #222;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header .date {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .category {{
            margin-bottom: 30px;
        }}
        .category-title {{
            font-size: 1.5em;
            color: #333;
            margin-bottom: 15px;
            padding-left: 15px;
            border-left: 4px solid #667eea;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        }}
        .card-title {{
            font-size: 1.15em;
            font-weight: 700;
            color: #222;
            margin-bottom: 8px;
        }}
        .card-summary {{
            color: #555;
            margin-bottom: 10px;
        }}
        .card-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            font-size: 0.92em;
            color: #888;
            flex-wrap: wrap;
        }}
        .card-link {{
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }}
        .card-link:hover {{
            text-decoration: underline;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            margin-right: 8px;
            vertical-align: middle;
        }}
        .badge-ai {{ background: #e3f2fd; color: #1976d2; }}
        .badge-product {{ background: #f3e5f5; color: #7b1fa2; }}
        .badge-industry {{ background: #e8f5e9; color: #388e3c; }}
        .badge-funding {{ background: #fff3e0; color: #f57c00; }}
        .badge-tech {{ background: #fce4ec; color: #c2185b; }}
        .empty {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            color: #666;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .footer {{
            text-align: center;
            padding: 40px 20px;
            color: #999;
            font-size: 0.9em;
        }}
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 1.8em; }}
            .container {{ padding: 10px; }}
            .card {{ padding: 15px; }}
            .card-meta {{ flex-direction: column; align-items: flex-start; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>每日科技简报</h1>
        <div class="date">{date}</div>
        <div style="margin-top: 10px; font-size: 0.9em;">由 AI Agent 自动生成</div>
    </div>
    <div class="container">
        {categories_html if categories_html else '<div class="empty">暂无可展示内容，请检查上游采集结果。</div>'}
    </div>
    <div class="footer">
        <p>Generated by Daily Tech Briefing AI Agent | {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
    </div>
</body>
</html>"""

    def _generate_categories(self, briefings):
        if isinstance(briefings, list):
            briefings = self._group_list_by_category(briefings)

        if not isinstance(briefings, dict):
            return ""

        badge_map = {
            "AI": "badge-ai",
            "产品发布": "badge-product",
            "行业动态": "badge-industry",
            "融资并购": "badge-funding",
            "技术趋势": "badge-tech"
        }

        category_order = ["AI", "产品发布", "行业动态", "融资并购", "技术趋势"]
        html = ""

        for category in category_order:
            items = briefings.get(category, [])
            if not isinstance(items, list) or not items:
                continue

            badge_class = badge_map.get(category, "badge-tech")
            html += '<div class="category">\n'
            html += f'<h2 class="category-title"><span class="badge {badge_class}">{category}</span></h2>\n'

            for item in items:
                if not isinstance(item, dict):
                    continue

                title = str(item.get("title", "无标题"))
                summary = str(item.get("summary", "暂无摘要"))
                source = str(item.get("source", "未知来源"))
                link = str(item.get("link", "#"))

                html += '<div class="card">\n'
                html += f'<div class="card-title">{title}</div>\n'
                html += f'<div class="card-summary">{summary}</div>\n'
                html += '<div class="card-meta">\n'
                html += f'<span>{source}</span>\n'
                html += f'<a href="{link}" target="_blank" class="card-link">阅读原文 &rarr;</a>\n'
                html += '</div>\n'
                html += '</div>\n'

            html += '</div>\n'

        return html


html_tool = HTMLTool()
