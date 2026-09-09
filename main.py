import os
import sys
from datetime import datetime, timedelta
from crewai import Crew, Process

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from agents.collector import CollectorAgent
from agents.writer import WriterAgent
from agents.checker import CheckerAgent

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
    html_content = str(result)

    if not html_content.strip().startswith("<!DOCTYPE"):
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日科技简报 - {date}</title>
</head>
<body>
    <h1>每日科技简报</h1>
    <p>本次简报已生成，但 HTML 输出格式异常，请检查上游数据。</p>
</body>
</html>"""

    output_path = os.path.join(settings.OUTPUT_DIR, settings.HTML_FILE)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    index_path = os.path.join(settings.OUTPUT_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"已保存至: {output_path}")

if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    success = run_daily_briefing(date_arg)
    sys.exit(0 if success else 1)
