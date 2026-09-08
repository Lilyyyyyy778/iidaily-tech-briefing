from crewai.tools import BaseTool
import requests

class CheckTool(BaseTool):
    name: str = "check_links"
    description: str = "检查新闻链接的有效性和内容质量"

    def _run(self, briefings_str: str = "{}") -> str:
        import json
        try:
            briefings = json.loads(briefings_str.replace("'", '"'))
        except:
            return "解析失败"

        issues = []
        total = 0
        valid = 0

        for category, items in briefings.items():
            for item in items:
                total += 1
                link = item.get("link", "")

                if not link:
                    issues.append(f"[{item.get('title', '未知')}] 缺少链接")
                    continue

                if not link.startswith(("http://", "https://")):
                    issues.append(f"[{item.get('title', '未知')}] 链接格式错误")
                    continue

                try:
                    resp = requests.head(link, timeout=5, allow_redirects=True)
                    if resp.status_code == 200:
                        valid += 1
                    else:
                        issues.append(f"[{item.get('title', '未知')}] 链接异常({resp.status_code})")
                except:
                    issues.append(f"[{item.get('title', '未知')}] 链接无法访问")

        result = {
            "total": total,
            "valid": valid,
            "issues": issues,
            "passed": len(issues) == 0
        }
        return str(result)

check_tool = CheckTool()
