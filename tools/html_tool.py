"""确定性的 HTML 简报渲染器 + CrewAI 工具封装。

页面渲染完全由 Python 完成（不经过大模型），因此无论上游 Agent 输出什么，
最终写入 output/index.html 并部署到 GitHub Pages 的一定是结构完整的 HTML。
"""
import html
from datetime import datetime

from crewai.tools import BaseTool

from config.settings import settings
from tools.briefing_utils import parse_briefings

# 每个分类的主题色与图标
CATEGORY_THEME = {
    "AI": {"color": "#6366f1", "emoji": "🤖"},
    "产品发布": {"color": "#a855f7", "emoji": "🚀"},
    "行业动态": {"color": "#0ea5e9", "emoji": "📰"},
    "融资并购": {"color": "#f59e0b", "emoji": "💰"},
    "技术趋势": {"color": "#f43f5e", "emoji": "🧭"},
}
DEFAULT_THEME = {"color": "#64748b", "emoji": "✨"}


def _escape(value):
    return html.escape(str(value if value is not None else ""), quote=True)


def _theme(category):
    return CATEGORY_THEME.get(category, DEFAULT_THEME)


def _sections(briefings):
    """返回 [(锚点ID, 分类名, 条目列表), ...]，预置分类优先、其余置后。"""
    ordered = [c for c in settings.CATEGORIES if briefings.get(c)]
    ordered += [c for c in briefings if c not in settings.CATEGORIES and briefings.get(c)]
    return [
        (f"cat-{index}", category, briefings[category])
        for index, category in enumerate(ordered)
    ]


def _render_toc(briefings):
    links = []
    for anchor, category, items in _sections(briefings):
        theme = _theme(category)
        links.append(
            f'<a class="toc-link" href="#{anchor}" style="--accent:{theme["color"]}">'
            f'<span class="cat-dot"></span>{_escape(category)}<em>{len(items)}</em></a>'
        )
    if not links:
        return ""
    return (
        '\n    <nav class="toc" aria-label="分类导航">'
        + "".join(links)
        + "</nav>"
    )


def _render_card(item, category):
    theme = _theme(category)
    title = _escape(item.get("title") or "无标题")
    summary = _escape(item.get("summary") or "").replace("\n", "<br>")
    source = _escape(item.get("source") or "未知来源")
    link = item.get("link") or ""

    summary_html = ""
    if summary:
        summary_html = f'\n                    <p class="card-summary">{summary}</p>'

    if link:
        action = (
            f'<a class="card-link" href="{_escape(link)}" target="_blank" '
            f'rel="noopener noreferrer">阅读原文 <span class="arrow">&rarr;</span></a>'
        )
    else:
        action = '<span class="card-link is-disabled">暂无链接</span>'

    return (
        f'\n                <article class="card" style="--accent:{theme["color"]}">'
        f'\n                    <h3 class="card-title">{title}</h3>{summary_html}'
        '\n                    <div class="card-meta">'
        '\n                        <span class="card-source">'
        f'<span class="source-dot"></span>{source}</span>'
        f'\n                        {action}'
        '\n                    </div>'
        '\n                </article>'
    )


def _render_categories(briefings):
    sections = []
    for anchor, category, items in _sections(briefings):
        theme = _theme(category)
        cards = "".join(_render_card(item, category) for item in items)
        sections.append(
            f'\n            <section class="category" id="{anchor}">'
            '\n                <div class="category-head">'
            f'\n                    <span class="cat-icon" style="--accent:{theme["color"]}">'
            f'{theme["emoji"]}</span>'
            f'\n                    <h2 class="category-title">{_escape(category)}</h2>'
            f'\n                    <span class="category-count">{len(items)} 条</span>'
            '\n                </div>'
            f'\n                <div class="cards">{cards}'
            '\n                </div>'
            '\n            </section>'
        )
    if not sections:
        sections.append(
            '\n            <div class="empty">'
            '\n                <p>今日暂无可展示的科技新闻。</p>'
            '\n                <p class="empty-hint">可能是搜索接口暂时不可用，请稍后重试。</p>'
            '\n            </div>'
        )
    return "".join(sections)


STYLE = """
:root {
    --bg: #f4f6fb;
    --card: #ffffff;
    --text: #1b2130;
    --muted: #6b7385;
    --line: #e8ebf3;
    --accent: #6366f1;
    --shadow: 0 1px 2px rgba(16, 24, 40, .04), 0 8px 24px rgba(16, 24, 40, .06);
    --shadow-hover: 0 2px 4px rgba(16, 24, 40, .06), 0 16px 40px rgba(16, 24, 40, .14);
    --radius: 16px;
}
@media (prefers-color-scheme: dark) {
    :root {
        --bg: #0b0e14;
        --card: #151a23;
        --text: #e7ebf3;
        --muted: #98a1b3;
        --line: #232a36;
        --shadow: 0 1px 2px rgba(0, 0, 0, .5), 0 8px 24px rgba(0, 0, 0, .35);
        --shadow-hover: 0 2px 4px rgba(0, 0, 0, .5), 0 16px 40px rgba(0, 0, 0, .55);
    }
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
        "PingFang SC", "HarmonyOS Sans SC", "Microsoft YaHei", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.65;
    -webkit-font-smoothing: antialiased;
}
/* ---------- 顶部 Hero ---------- */
.hero {
    position: relative;
    padding: 66px 20px 78px;
    text-align: center;
    color: #fff;
    overflow: hidden;
    background:
        radial-gradient(1200px 420px at 50% -180px, rgba(255, 255, 255, .35) 0%, transparent 70%),
        linear-gradient(135deg, #4338ca 0%, #6d28d9 55%, #9333ea 100%);
}
.hero::after {
    content: "";
    position: absolute;
    inset: 0;
    background-image: radial-gradient(rgba(255, 255, 255, .16) 1px, transparent 1px);
    background-size: 22px 22px;
    opacity: .55;
    pointer-events: none;
}
.hero-inner { position: relative; z-index: 1; max-width: 820px; margin: 0 auto; }
.hero-kicker {
    font-size: .72em; letter-spacing: .34em; text-transform: uppercase;
    opacity: .82; margin-bottom: 14px;
}
.hero h1 {
    font-size: clamp(1.9rem, 5vw, 2.9rem);
    font-weight: 800; letter-spacing: .06em;
    text-shadow: 0 2px 20px rgba(0, 0, 0, .18);
}
.hero-pills { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; margin-top: 20px; }
.pill {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 7px 16px; border-radius: 999px; font-size: .86em;
    background: rgba(255, 255, 255, .15);
    border: 1px solid rgba(255, 255, 255, .26);
    backdrop-filter: blur(6px);
}
.pill-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #a5f3fc; box-shadow: 0 0 10px #67e8f9;
}
.hero-note { margin-top: 18px; font-size: .84em; opacity: .8; }
/* ---------- 分类导航 ---------- */
.toc {
    display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;
    max-width: 1040px;
    margin: -26px auto 0;
    padding: 16px;
    position: relative; z-index: 2;
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
}
.toc-link {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 8px 14px; border-radius: 999px;
    font-size: .88em; font-weight: 600; color: var(--text);
    text-decoration: none;
    background: var(--bg);
    border: 1px solid var(--line);
    transition: transform .18s ease, border-color .18s ease;
}
.toc-link:hover { transform: translateY(-2px); border-color: var(--accent); }
.toc-link em { font-style: normal; font-size: .82em; color: var(--muted); }
.cat-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--accent); flex: none; }
/* ---------- 主体容器 ---------- */
.container { max-width: 1040px; margin: 0 auto; padding: 40px 20px 0; }
.category { margin-bottom: 44px; scroll-margin-top: 20px; }
.category-head { display: flex; align-items: center; gap: 12px; margin-bottom: 18px; }
.cat-icon {
    display: grid; place-items: center;
    width: 40px; height: 40px; border-radius: 12px; font-size: 1.05em;
    background: var(--card); border: 1px solid var(--line); box-shadow: var(--shadow);
}
.category-title { font-size: 1.24em; font-weight: 700; letter-spacing: .02em; white-space: nowrap; }
.category-count {
    font-size: .76em; font-weight: 600; color: var(--muted);
    padding: 3px 11px; border-radius: 999px;
    background: var(--card); border: 1px solid var(--line); white-space: nowrap;
}
.category-head::after { content: ""; flex: 1; height: 1px; background: var(--line); }
/* ---------- 新闻卡片 ---------- */
.cards { display: grid; gap: 14px; }
.card {
    position: relative; overflow: hidden;
    padding: 20px 22px;
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
}
.card::before {
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
    background: var(--accent); opacity: .85;
}
.card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-hover);
    border-color: var(--accent);
}
.card-title {
    font-size: 1.06em; font-weight: 700; line-height: 1.5;
    margin-bottom: 8px; padding-left: 6px;
}
.card-summary { color: var(--muted); font-size: .94em; margin-bottom: 14px; padding-left: 6px; }
.card-meta {
    display: flex; justify-content: space-between; align-items: center;
    gap: 12px; flex-wrap: wrap; font-size: .82em; padding-left: 6px;
}
.card-source {
    display: inline-flex; align-items: center; gap: 7px; color: var(--muted);
    max-width: 62%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.source-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); flex: none; }
.card-link { color: var(--accent); font-weight: 600; text-decoration: none; white-space: nowrap; }
.card-link:hover { text-decoration: underline; }
.card-link .arrow { display: inline-block; transition: transform .18s ease; }
.card-link:hover .arrow { transform: translateX(3px); }
.card-link.is-disabled { color: var(--muted); font-weight: 500; }
/* ---------- 空状态 / 页脚 ---------- */
.empty {
    text-align: center; padding: 90px 20px; color: var(--muted);
    background: var(--card); border: 1px dashed var(--line); border-radius: var(--radius);
}
.empty-hint { font-size: .88em; opacity: .8; margin-top: 8px; }
.footer { text-align: center; padding: 48px 20px 56px; color: var(--muted); font-size: .82em; }
.footer-time { margin-top: 6px; opacity: .75; }
/* ---------- 入场动画 ---------- */
@media (prefers-reduced-motion: no-preference) {
    .card { animation: rise .45s ease both; }
    @keyframes rise {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: none; }
    }
}
/* ---------- 移动端适配 ---------- */
@media (max-width: 640px) {
    .hero { padding: 48px 16px 62px; }
    .toc { margin-top: -20px; padding: 12px; gap: 8px; }
    .container { padding: 28px 14px 0; }
    .category { margin-bottom: 34px; }
    .card { padding: 17px 18px; }
    .card-source { max-width: 100%; }
    .category-count { display: none; }
}

"""


def render_html(briefings, date=""):
    """把简报数据渲染成完整的 HTML 文档（永远返回合法 HTML）。"""
    briefings = briefings or {}
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    total = sum(len(items) for items in briefings.values())
    section_count = len(_sections(briefings))
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="color-scheme" content="light dark">
<title>每日科技简报 - {_escape(date)}</title>
<style>{STYLE}</style>
</head>
<body>
    <header class="hero">
        <div class="hero-inner">
            <p class="hero-kicker">Daily Tech Briefing</p>
            <h1>每日科技简报</h1>
            <div class="hero-pills">
                <span class="pill"><span class="pill-dot"></span>{_escape(date)}</span>
                <span class="pill">{total} 条 · {section_count} 个板块</span>
            </div>
            <p class="hero-note">由 AI Agent 自动采集 · 整理 · 质检</p>
        </div>
    </header>{_render_toc(briefings)}
    <main class="container">{_render_categories(briefings)}
    </main>
    <footer class="footer">
        <p>由 Daily Tech Briefing AI Agent 自动生成</p>
        <p class="footer-time">{generated_at}</p>
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

