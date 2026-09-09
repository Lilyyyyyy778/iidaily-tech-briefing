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
    <p>本次简报生成成功，但结果不是完整 HTML，请检查上游数据结构是否为按分类分组的 JSON 对象。</p>
</body>
</html>"""

    output_path = os.path.join(settings.OUTPUT_DIR, settings.HTML_FILE)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    index_path = os.path.join(settings.OUTPUT_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"已保存至: {output_path}")
