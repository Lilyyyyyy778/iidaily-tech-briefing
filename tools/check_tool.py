"""链接有效性与内容完整性质检工具。"""
import json

import requests
from crewai.tools import BaseTool

from tools.briefing_utils import parse_briefings

USER_AGENT = "Mozilla/5.0 (compatible; DailyTechBriefing/1.0)"


def check_link(url):
    """检查单个链接，返回 ``(是否可用, 失败原因)``。"""
    if not url:
        return False, "缺少链接"
    if not url.startswith(("http://", "https://")):
        return False, "链接格式错误"

    headers = {"User-Agent": USER_AGENT}
    last_status = "无法访问"
    for method in ("head", "get"):
        try:
            response = getattr(requests, method)(
                url, headers=headers, timeout=8, allow_redirects=True
            )
            if response.status_code < 400:
                return True, ""
            last_status = response.status_code
        except Exception:
            continue
    return False, f"链接异常({last_status})"


class CheckTool(BaseTool):
    name: str = "check_links"
    description: str = "检查简报中的新闻链接有效性与内容完整性，返回 JSON 质检报告"

    def _run(self, briefings_str: str = "{}") -> str:
        briefings = parse_briefings(briefings_str)
        issues = []
        total = 0
        valid = 0

        for items in briefings.values():
            for item in items:
                total += 1
                if not item.get("summary"):
                    issues.append(f"[{item['title']}] 缺少摘要")
                ok, reason = check_link(item.get("link"))
                if ok:
                    valid += 1
                else:
                    issues.append(f"[{item['title']}] {reason}")

        report = {
            "total": total,
            "valid_links": valid,
            "issues": issues,
            "passed": total > 0 and not issues,
        }
        return json.dumps(report, ensure_ascii=False)


check_tool = CheckTool()
