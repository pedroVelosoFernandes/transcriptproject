from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional


def paginate(method, limit: Optional[int] = None, **kwargs) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    start_cursor = None

    while True:
        params = dict(kwargs)
        if start_cursor:
            params["start_cursor"] = start_cursor

        response = method(**params)
        page_results = response.get("results", [])
        results.extend(page_results)

        if limit is not None and len(results) >= limit:
            return results[:limit]

        if not response.get("has_more"):
            break

        start_cursor = response.get("next_cursor")

    return results


def rich_text_to_plain_text(items: Iterable[Dict[str, Any]] | None) -> str:
    if not items:
        return ""
    return "".join(item.get("plain_text", "") for item in items)


def extract_property(prop: Dict[str, Any]) -> Any:
    prop_type = prop.get("type")

    if prop_type == "title":
        return rich_text_to_plain_text(prop.get("title", []))

    if prop_type == "rich_text":
        return rich_text_to_plain_text(prop.get("rich_text", []))

    if prop_type == "status":
        status = prop.get("status")
        return status.get("name") if status else None

    if prop_type == "select":
        select = prop.get("select")
        return select.get("name") if select else None

    if prop_type == "multi_select":
        return [item.get("name") for item in prop.get("multi_select", [])]

    if prop_type == "date":
        date = prop.get("date")
        if not date:
            return None
        return {
            "start": date.get("start"),
            "end": date.get("end"),
            "time_zone": date.get("time_zone"),
        }

    if prop_type == "people":
        return [
            {
                "id": person.get("id"),
                "name": person.get("name"),
                "type": person.get("type"),
            }
            for person in prop.get("people", [])
        ]

    if prop_type == "relation":
        return [rel.get("id") for rel in prop.get("relation", [])]

    if prop_type == "checkbox":
        return prop.get("checkbox")

    if prop_type == "number":
        return prop.get("number")

    if prop_type == "url":
        return prop.get("url")

    if prop_type == "email":
        return prop.get("email")

    if prop_type == "phone_number":
        return prop.get("phone_number")

    if prop_type == "created_time":
        return prop.get("created_time")

    if prop_type == "last_edited_time":
        return prop.get("last_edited_time")

    if prop_type == "created_by":
        user = prop.get("created_by")
        return user.get("id") if user else None

    if prop_type == "last_edited_by":
        user = prop.get("last_edited_by")
        return user.get("id") if user else None

    if prop_type == "files":
        return [
            {
                "name": f.get("name"),
                "type": f.get("type"),
                "url": f.get(f.get("type"), {}).get("url"),
            }
            for f in prop.get("files", [])
        ]

    if prop_type == "formula":
        formula = prop.get("formula", {})
        formula_type = formula.get("type")
        return formula.get(formula_type)

    if prop_type == "rollup":
        return prop.get("rollup")

    return prop


def extract_page_properties(page: Dict[str, Any]) -> Dict[str, Any]:
    return {
        name: extract_property(prop)
        for name, prop in page.get("properties", {}).items()
    }


def block_to_simple(block: Dict[str, Any]) -> Dict[str, Any]:
    block_type = block.get("type")
    data = block.get(block_type, {}) if block_type else {}

    simple: Dict[str, Any] = {
        "id": block.get("id"),
        "type": block_type,
        "has_children": block.get("has_children", False),
        "created_time": block.get("created_time"),
        "last_edited_time": block.get("last_edited_time"),
    }

    if isinstance(data, dict):
        if "rich_text" in data:
            simple["text"] = rich_text_to_plain_text(data.get("rich_text", []))

        if block_type == "to_do":
            simple["checked"] = data.get("checked")

        if block_type in {"image", "video", "file", "pdf", "audio"}:
            file_type = data.get("type")
            simple["file"] = {
                "type": file_type,
                "url": data.get(file_type, {}).get("url") if file_type else None,
            }

        if block_type == "bookmark":
            simple["url"] = data.get("url")

        if block_type == "code":
            simple["language"] = data.get("language")

    return simple


def get_block_children_recursive(notion, block_id: str) -> List[Dict[str, Any]]:
    children = paginate(
        notion.blocks.children.list,
        block_id=block_id,
        page_size=100,
    )

    output: List[Dict[str, Any]] = []

    for child in children:
        simple = block_to_simple(child)
        if child.get("has_children"):
            simple["children"] = get_block_children_recursive(notion, child["id"])
        output.append(simple)

    return output


def rich_text(content: str) -> List[Dict[str, Any]]:
    return [
        {
            "type": "text",
            "text": {
                "content": content,
            },
        }
    ]


def paragraph_block(text: str) -> Dict[str, Any]:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": rich_text(text),
        },
    }


def heading_2_block(text: str) -> Dict[str, Any]:
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": rich_text(text),
        },
    }


def heading_3_block(text: str) -> Dict[str, Any]:
    return {
        "object": "block",
        "type": "heading_3",
        "heading_3": {
            "rich_text": rich_text(text),
        },
    }


def todo_block(text: str, checked: bool = False) -> Dict[str, Any]:
    return {
        "object": "block",
        "type": "to_do",
        "to_do": {
            "rich_text": rich_text(text),
            "checked": checked,
        },
    }


def bulleted_list_block(text: str) -> Dict[str, Any]:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": rich_text(text),
        },
    }


def markdown_to_blocks(markdown: str) -> List[Dict[str, Any]]:
    if not markdown:
        return []

    blocks: List[Dict[str, Any]] = []
    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue

        if line.startswith("## "):
            blocks.append(heading_2_block(line[3:]))
            continue

        if line.startswith("### "):
            blocks.append(heading_3_block(line[4:]))
            continue

        if line.startswith("- [ ] "):
            blocks.append(todo_block(line[6:], checked=False))
            continue

        if line.startswith("- [x] "):
            blocks.append(todo_block(line[6:], checked=True))
            continue

        if line.startswith("- "):
            blocks.append(bulleted_list_block(line[2:]))
            continue

        blocks.append(paragraph_block(line))

    return blocks
