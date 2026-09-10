"""确定性的 HTML 简报渲染器 + CrewAI 工具封装。

页面渲染完全由 Python 完成（不经过大模型），因此无论上游 Agent 输出什么，
最终写入 output/index.html 并部署到 GitHub Pages 的一定是结构完整的 HTML。
"""
import html
from datetime import datetime

from crewai.tools import BaseTool

from config.settings import settings
from tools.briefing_utils import parse_briefings

BADGE_MAP = {
    "AI": "badge-ai",
    "产品发布": "badge-product",
    "行业动态": "badge-industry",
    "融资并购": "badge-funding",
    "技术趋势": "badge-tech",
}


def _escape(value):
    return html.escape(str(value if value is not None else ""), quote=True)


def _ordered_categories(briefings):
    ordered = [c for c in settings.CATEGORIES if briefings.get(c)]
    ordered += [c for c in briefings if c not in settings.CATEGORIES and briefings.get(c)]
    return ordered


def _render_card(item):
    title = _escape(item.get("title") or "无标题")
    summary = _escape(item.get("summary") or "").replace("\n", "<br>")
    source = _escape(item.get("source") or "未知来源")
    link = item.get("link") or ""

    if link:
        action = (
            f'<a class="card-link" href="{_escape(link)}" target="_blank" '
            f'rel="noopener noreferrer">阅读原文 &rarr;</a>'
        )
    else:
        action = '<span class="card-link is-disabled">暂无链接</span>'

    summary_html = ""
    if summary:
        summary_html = f'\n                <p class="card-summary">{summary}</p>'

    return (
        '\n            <article class="card">'
        f'\n                <h3 class="card-title">{title}</h3>{summary_html}'
        '\n                <div class="card-meta">'
        f'\n                    <span class="card-source">{source}</span>'
        f'\n                    {action}'
        '\n                </div>'
        '\n            </article>'
    )


def _render_categories(briefings):
    sections = []
    for category in _ordered_categories(briefings):
        items = briefings[category]
        badge = BADGE_MAP.get(category, "badge-default")
        cards = "".join(_render_card(item) for item in items)
        sections.append(
            '\n        <section class="category">'
            '\n            <h2 class="category-title">'
            f'\n                <span class="badge {badge}">{_escape(category)}</span>'
            f'\n                <span class="category-count">{len(items)} 条</span>'
            '\n            </h2>'
            f'{cards}'
            '\n        </section>'
        )
    if not sections:
        sections.append(
            '\n        <div class="empty">'
            '\n            <p>今日暂无可展示的科技新闻。</p>'
            '\n            <p class="empty-hint">可能是搜索接口暂时不可用，请稍后重试。</p>'
            '\n        </div>'
        )
    return "".join(sections)


STYLE = """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
            background: #f5f6fa;
            color: #222;
            line-height: 1.6;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            padding: 48px 20px;
            text-align: center;
        }
        .header h1 { font-size: 2.4em; margin-bottom: 10px; letter-spacing: 2px; }
        .header .date { opacity: 0.95; font-size: 1.1em; }
        .header .subtitle { opacity: 0.85; font-size: 0.9em; margin-top: 8px; }
        .container { max-width: 1100px; margin: 0 auto; padding: 24px 20px 0; }
        .category { margin-bottom: 34px; }
        .category-title {
            display: flex; align-items: center; gap: 10px;
            font-size: 1.25em; color: #333; margin-bottom: 14px;
        }
        .category-count { font-size: 0.75em; color: #9aa1ad; font-weight: normal; }
        .card {
            background: #fff; border-radius: 12px; padding: 20px;
            margin-bottom: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .card:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.12); }
        .card-title { font-size: 1.12em; color: #1f2937; margin-bottom: 8px; font-weight: 600; }
        .card-summary { color: #5b6472; font-size: 0.95em; margin-bottom: 12px; }
        .card-meta {
            display: flex; justify-content: space-between; align-items: center;
            font-size: 0.85em; color: #9aa1ad; gap: 12px; flex-wrap: wrap;
        }
        .card-source { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 60%; }
        .card-link { color: #667eea; text-decoration: none; white-space: nowrap; }
        .card-link:hover { text-decoration: underline; }
        .card-link.is-disabled { color: #c0c4cc; }
        .badge {
            display: inline-block; padding: 4px 14px; border-radius: 20px;
            font-size: 0.95em; color: #fff;
        }
        .badge-ai { background: #1976d2; }
        .badge-product { background: #7b1fa2; }
        .badge-industry { background: #388e3c; }
        .badge-funding { background: #f57c00; }
        .badge-tech { background: #c2185b; }
        .badge-default { background: #607d8b; }
        .empty { text-align: center; padding: 80px 20px; color: #666; }
        .empty-hint { color: #999; font-size: 0.9em; margin-top: 8px; }
        .footer { text-align: center; padding: 40px 20px; color: #9aa1ad; font-size: 0.85em; }
        @media (max-width: 768px) {
            .header { padding: 34px 16px; }
            .header h1 { font-size: 1.7em; }
            .container { padding: 16px 12px 0; }
            .card { padding: 16px; }
            .card-source { max-width: 100%; }
        }
"""


def render_html(briefings, date=""):
    """把简报数据渲染成完整的 HTML 文档（永远返回合法 HTML）。"""
    briefings = briefings or {}
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    total = sum(len(items) for items in briefings.values())
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>每日科技简报 - {_escape(date)}</title>
<style>{STYLE}</style>
</head>
<body>
    <header class="header">
        <h1>每日科技简报</h1>
        <p class="date">{_escape(date)}</p>
        <p class="subtitle">由 AI Agent 自动生成 · 共 {total} 条</p>
    </header>
    <main class="container">{_render_categories(briefings)}
    </main>
    <footer class="footer">
        <p>Generated by Daily Tech Briefing AI Agent · {generated_at}</p>
    </footer>
</body>
</html>
"""


class HTMLTool(BaseTool):
    name: str = "generate_html"
    description: str = "将按分类分组的新闻数据（JSON）渲染为完整的响应式 HTML 简报页面"

    def _run(self, briefings_str: str = "{}", date: str = "") -> str:
        return render_html(parse_briefings(briefings_str), date)

    def generate(self, briefings=None, date="", briefings_str=None) -> str:
        """兼容旧调用方式：html_tool.generate(date=...)"""
        if briefings is None:
            briefings = parse_briefings(briefings_str) if briefings_str else {}
        elif isinstance(briefings, str):
            briefings = parse_briefings(briefings)
        return render_html(briefings, date)


html_tool = HTMLTool()

