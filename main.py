import os
import sys
import json
from datetime import datetime, timedelta
from crewai import Crew, Process

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from agents.collector import CollectorAgent
from agents.writer import WriterAgent
from agents.checker import CheckerAgent
from tools.html_tool import html_tool


def run_daily_briefing(target_date=None):
    if not target_date:
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"开始生成 {target_date} 的科技简报...")

    collector = CollectorAgent()
    writer = WriterAgent()
    checker = CheckerAgent()

    collect_task = collector.create_task(target_date)
    write_task = writer.create_task(target_date)
    check_task = checker.create_task(target_date)

    crew = Crew(
        agents=[collector.agent, writer.agent, checker.agent],
        tasks=[collect_task, write_task, check_task],
        process=Process.sequential,
        verbose=True
    )

    try:
        result = crew.kickoff()
        print("任务完成！")
        save_result(result, target_date)
        return True
    except Exception as e:
        print(f"任务失败: {e}")
        return False


def save_result(result, date):
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)

    html_content = _extract_html_content(result, date)

    if not html_content:
        html_content = f"""<!DOCTYPE html>
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
            padding: 40px 20px;
            color: #222;
        }}
        .wrap {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 32px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }}
        h1 {{
            margin-bottom: 16px;
        }}
        p {{
            line-height: 1.7;
            color: #555;
        }}
        code {{
            background: #f3f3f3;
            padding: 2px 6px;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="wrap">
        <h1>每日科技简报</h1>
        <p>本次简报已生成，但结果不是完整 HTML。</p>
        <p>请检查上游采集/写作/质检任务输出是否为按分类分组的 JSON 对象。</p>
        <p>生成日期：<code>{date}</code></p>
    </div>
</body>
</html>"""

    output_path = os.path.join(settings.OUTPUT_DIR, settings.HTML_FILE)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    index_path = os.path.join(settings.OUTPUT_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"已保存至: {output_path}")


def _is_html(content):
    if not isinstance(content, str):
        return False
    stripped = content.strip().lower()
    return stripped.startswith("<!doctype") or stripped.startswith("<html")


def _to_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _extract_html_content(result, date):
    candidates = [_to_text(result)]

    raw = _to_text(getattr(result, "raw", ""))
    if raw:
        candidates.append(raw)

    tasks_output = getattr(result, "tasks_output", None)
    if isinstance(tasks_output, list):
        for task_output in tasks_output:
            task_raw = _to_text(getattr(task_output, "raw", ""))
            if task_raw:
                candidates.append(task_raw)
            task_text = _to_text(task_output)
            if task_text:
                candidates.append(task_text)

    for text in candidates:
        if _is_html(text):
            return text

    for text in candidates:
        parsed = html_tool._parse_briefings(text)
        if isinstance(parsed, dict) and any(isinstance(v, list) for v in parsed.values()):
            return html_tool._generate_html(parsed, date)

        try:
            parsed_json = json.loads(text)
        except Exception:
            continue
        if isinstance(parsed_json, dict):
            return html_tool._generate_html(parsed_json, date)

    return ""


if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    success = run_daily_briefing(date_arg)
    sys.exit(0 if success else 1)
