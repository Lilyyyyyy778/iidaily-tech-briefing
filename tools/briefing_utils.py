"""简报数据解析与归一化工具。

这一层完全不依赖大模型，负责把「任意形态」的上游输出
（dict / list / JSON 文本 / Python repr / Markdown 代码块）统一成
``{分类: [ {title, summary, source, link}, ... ]}`` 结构，
让下游的 HTML 渲染与质检都能稳定工作。
"""
import ast
import json
import re

from config.settings import settings

DEFAULT_CATEGORY = "行业动态"

_TITLE_KEYS = ("title", "标题", "name", "headline")
_SUMMARY_KEYS = ("summary", "摘要", "desc", "description", "snippet", "content", "简介")
_SOURCE_KEYS = ("source", "来源", "site", "media", "publisher")
_LINK_KEYS = ("link", "url", "链接", "href", "source_url")
_CATEGORY_KEYS = ("category", "分类", "type", "section")

_WRAPPER_KEYS = ("briefings", "data", "news", "categories", "result", "results")


def _first_value(data, keys, default=""):
    for key in keys:
        value = data.get(key)
        if value:
            return value
    return default


def normalize_item(raw):
    """把单条新闻归一化为统一结构；缺少标题的条目直接丢弃。"""
    if not isinstance(raw, dict):
        return None

    title = str(_first_value(raw, _TITLE_KEYS, "")).strip()
    if not title:
        return None

    link = str(_first_value(raw, _LINK_KEYS, "")).strip()
    if link and not link.startswith(("http://", "https://")):
        link = ""

    summary = str(_first_value(raw, _SUMMARY_KEYS, "")).strip()
    source = str(_first_value(raw, _SOURCE_KEYS, "")).strip() or "未知来源"

    return {"title": title, "summary": summary, "source": source, "link": link}


def normalize_category(name):
    """把模型给出的分类名对齐到预置分类。"""
    name = str(name or "").strip()
    if not name:
        return DEFAULT_CATEGORY
    for category in settings.CATEGORIES:
        if name == category or category in name or name in category:
            return category
    return name


def _dedupe(briefings):
    """按链接/标题去重，并限制每个分类的条目数量。"""
    seen = set()
    result = {}
    limit = settings.MAX_ITEMS_PER_CATEGORY
    for category, items in briefings.items():
        kept = []
        for item in items:
            key = item["link"] or item["title"]
            if key in seen:
                continue
            seen.add(key)
            kept.append(item)
            if len(kept) >= limit:
                break
        if kept:
            result[category] = kept
    return result


def _normalize_briefings(data):
    briefings = {}

    if isinstance(data, dict):
        # 常见的外层包装，例如 {"briefings": {...}}
        for wrapper in _WRAPPER_KEYS:
            inner = data.get(wrapper)
            if isinstance(inner, (dict, list)):
                nested = _normalize_briefings(inner)
                if nested:
                    return nested

        for raw_category, raw_items in data.items():
            category = normalize_category(raw_category)
            if isinstance(raw_items, dict):
                if any(k in raw_items for k in _TITLE_KEYS):
                    raw_items = [raw_items]
                else:
                    raw_items = next(
                        (v for v in raw_items.values() if isinstance(v, list)), []
                    )
            if not isinstance(raw_items, list):
                continue
            for raw_item in raw_items:
                item = normalize_item(raw_item)
                if item:
                    briefings.setdefault(category, []).append(item)

    elif isinstance(data, list):
        for raw_item in data:
            item = normalize_item(raw_item)
            if not item:
                continue
            category = DEFAULT_CATEGORY
            if isinstance(raw_item, dict):
                category = normalize_category(
                    _first_value(raw_item, _CATEGORY_KEYS, DEFAULT_CATEGORY)
                )
            briefings.setdefault(category, []).append(item)

    return _dedupe(briefings)


def _extract_json_substring(text):
    """从混杂文本里提取第一个括号平衡的 JSON 片段。"""
    for opener, closer in (("{", "}"), ("[", "]")):
        start = text.find(opener)
        if start == -1:
            continue
        depth = 0
        in_string = False
        escaped = False
        for index in range(start, len(text)):
            char = text[index]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == opener:
                depth += 1
            elif char == closer:
                depth -= 1
                if depth == 0:
                    return text[start : index + 1]
    return ""


def parse_briefings(raw):
    """解析任意形态的简报数据，失败时返回空字典（绝不抛异常）。"""
    if raw is None:
        return {}
    if isinstance(raw, (dict, list)):
        return _normalize_briefings(raw)
    if not isinstance(raw, str):
        return {}

    text = raw.strip()
    if not text:
        return {}

    candidates = []
    code_block = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if code_block:
        candidates.append(code_block.group(1).strip())
    candidates.append(text)
    extracted = _extract_json_substring(text)
    if extracted:
        candidates.append(extracted)

    for candidate in candidates:
        for loader in (json.loads, ast.literal_eval):
            try:
                data = loader(candidate)
            except Exception:
                continue
            if isinstance(data, (dict, list)):
                briefings = _normalize_briefings(data)
                if briefings:
                    return briefings
    return {}


def count_items(briefings):
    if not briefings:
        return 0
    return sum(len(items) for items in briefings.values())


def merge_briefings(primary, secondary):
    """以 primary 为主，用 secondary 补齐缺失的新闻（按链接/标题去重）。"""
    result = {category: list(items) for category, items in (primary or {}).items()}
    for category, items in (secondary or {}).items():
        bucket = result.setdefault(category, [])
        existing = {item["link"] or item["title"] for item in bucket}
        for item in items:
            key = item["link"] or item["title"]
            if key in existing:
                continue
            existing.add(key)
            bucket.append(item)
    return _dedupe(result)
