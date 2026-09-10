import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from tools.briefing_utils import count_items, merge_briefings, parse_briefings
from tools.html_tool import render_html
from tools.search_tool import collect_news


def build_crew(target_date, raw_news):
    """构建「采集 -> 写作 -> 质检」的多 Agent 流水线。"""
    from crewai import Crew, Process

    from agents.checker import CheckerAgent
    from agents.collector import CollectorAgent
    from agents.writer import WriterAgent

    collector = CollectorAgent()
    writer = WriterAgent()
    checker = CheckerAgent()

    collect_task = collector.create_task(target_date, raw_news=raw_news)
    write_task = writer.create_task(target_date, context=[collect_task])
    check_task = checker.create_task(target_date, context=[write_task])

    crew = Crew(
        agents=[collector.agent, writer.agent, checker.agent],
        tasks=[collect_task, write_task, check_task],
        process=Process.sequential,
        verbose=True,
    )
    return crew, collect_task, write_task


def _task_raw(task):
    """安全地读取某个 Task 的原始输出文本。"""
    output = getattr(task, "output", None)
    if output is None:
        return ""
    return getattr(output, "raw", "") or ""


def collect_briefings(target_date, raw_news):
    """优先采用 AI Agent 的整理结果；失败或缺失时回退到确定性采集数据。"""
    candidates = []

    if settings.LLM is None:
        print("[warn] 未启用 AI Agent（缺少 DEEPSEEK_API_KEY），直接使用兜底采集数据。")
    else:
        try:
            crew, collect_task, write_task = build_crew(target_date, raw_news)
            crew.kickoff()
            for task in (write_task, collect_task):
                raw = _task_raw(task)
                if raw:
                    candidates.append(raw)
        except Exception as exc:
            print(f"[warn] AI Agent 流程失败，将使用兜底数据：{exc}")

    parsed = [parse_briefings(raw) for raw in candidates]
    parsed = [data for data in parsed if count_items(data) > 0]
    if not parsed:
        return raw_news

    best = max(parsed, key=count_items)
    # 用原始采集结果补齐 AI 遗漏的分类 / 条目，保证内容完整
    return merge_briefings(best, raw_news)


def save_result(html_content):
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    for filename in (settings.HTML_FILE, settings.INDEX_FILE):
        path = os.path.join(settings.OUTPUT_DIR, filename)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(html_content)
        print(f"已保存：{path}")


def run_daily_briefing(target_date=None):
    if not target_date:
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"开始生成 {target_date} 的科技简报...")

    raw_news = {}
    try:
        raw_news = collect_news(target_date)
        print(f"预采集完成，共 {count_items(raw_news)} 条候选新闻。")
    except Exception as exc:
        print(f"[warn] 预采集失败：{exc}")

    briefings = raw_news
    try:
        briefings = collect_briefings(target_date, raw_news)
    except Exception as exc:
        print(f"[warn] AI 整理失败，使用预采集数据：{exc}")

    html_content = render_html(briefings, target_date)
    save_result(html_content)
    print(f"任务完成，共生成 {count_items(briefings)} 条新闻。")
    return True


if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_daily_briefing(date_arg)
