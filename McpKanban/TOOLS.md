# MCP Tools JSON Guide

Each tool returns JSON in the format:

```json
{
  "ok": true,
  "data": {}
}
```

On error:

```json
{
  "ok": false,
  "error": {
    "type": "ErrorType",
    "message": "Human-friendly message"
  }
}
```

## ensure_project_board

Input:

```json
{
  "root_page_id": "ROOT_PAGE_ID",
  "project_name": "Project Kanban"
}
```

Output:

```json
{
  "ok": true,
  "data": {
    "created": true,
    "database_id": "DATABASE_ID",
    "data_source_id": "DATA_SOURCE_ID",
    "board_view_id": "BOARD_VIEW_ID",
    "board_view_created": true,
    "board_view_error": null,
    "note": null,
    "statuses": ["Backlog", "Ready", "In Progress", "In Review", "Done"],
    "default_status": "Backlog"
  }
}
```

## get_project_context

Input:

```json
{
  "root_page_id": "ROOT_PAGE_ID",
  "project_name": "Project Kanban"
}
```

Output:

```json
{
  "ok": true,
  "data": {
    "root_page_id": "ROOT_PAGE_ID",
    "database_id": "DATABASE_ID",
    "data_source_id": "DATA_SOURCE_ID",
    "board_view_id": "BOARD_VIEW_ID",
    "project_name": "Project Kanban",
    "statuses": ["Backlog", "Ready", "In Progress", "In Review", "Done"],
    "summary": {
      "total_issues": 2,
      "by_status": {
        "Backlog": 1,
        "Ready": 0,
        "In Progress": 1,
        "In Review": 0,
        "Done": 0
      }
    },
    "kanban": {
      "Backlog": [
        {
          "id": "PAGE_ID",
          "title": "Implement login",
          "status": "Backlog",
          "priority": "High",
          "description": "Initial auth flow",
          "external_id": "AUTH-001",
          "url": "https://www.notion.so/...",
          "created_time": "2026-05-16T10:00:00.000Z",
          "last_edited_time": "2026-05-16T10:00:00.000Z"
        }
      ],
      "Ready": [],
      "In Progress": [],
      "In Review": [],
      "Done": []
    }
  }
}
```

## list_issues

Input:

```json
{
  "data_source_id": "DATA_SOURCE_ID",
  "status": "Backlog",
  "include_blocks": false,
  "limit": 100
}
```

Output:

```json
{
  "ok": true,
  "data": {
    "data_source_id": "DATA_SOURCE_ID",
    "count": 1,
    "issues": [
      {
        "id": "PAGE_ID",
        "title": "Implement login",
        "status": "Backlog",
        "priority": "High",
        "description": "Initial auth flow",
        "external_id": "AUTH-001",
        "url": "https://www.notion.so/...",
        "created_time": "2026-05-16T10:00:00.000Z",
        "last_edited_time": "2026-05-16T10:00:00.000Z"
      }
    ]
  }
}
```

## get_issue

Input:

```json
{
  "page_id": "PAGE_ID",
  "include_blocks": true
}
```

Output:

```json
{
  "ok": true,
  "data": {
    "id": "PAGE_ID",
    "title": "Implement login",
    "status": "Backlog",
    "priority": "High",
    "description": "Initial auth flow",
    "external_id": "AUTH-001",
    "url": "https://www.notion.so/...",
    "created_time": "2026-05-16T10:00:00.000Z",
    "last_edited_time": "2026-05-16T10:00:00.000Z",
    "blocks": [
      {
        "id": "BLOCK_ID",
        "type": "heading_2",
        "has_children": false,
        "created_time": "2026-05-16T10:00:00.000Z",
        "last_edited_time": "2026-05-16T10:00:00.000Z",
        "text": "Context"
      }
    ]
  }
}
```

## create_issue

Input:

```json
{
  "data_source_id": "DATA_SOURCE_ID",
  "title": "Implement login",
  "status": "Backlog",
  "priority": "High",
  "description": "Initial auth flow",
  "external_id": "AUTH-001",
  "details_markdown": "## Context\n- [ ] Create UI\n- [ ] Integrate"
}
```

Output:

```json
{
  "ok": true,
  "data": {
    "created": true,
    "issue": {
      "id": "PAGE_ID",
      "title": "Implement login",
      "status": "Backlog",
      "priority": "High",
      "description": "Initial auth flow",
      "external_id": "AUTH-001",
      "url": "https://www.notion.so/...",
      "created_time": "2026-05-16T10:00:00.000Z",
      "last_edited_time": "2026-05-16T10:00:00.000Z"
    }
  }
}
```

## update_issue

Input:

```json
{
  "page_id": "PAGE_ID",
  "status": "In Progress",
  "description": "Now in progress"
}
```

Output:

```json
{
  "ok": true,
  "data": {
    "id": "PAGE_ID",
    "title": "Implement login",
    "status": "In Progress",
    "priority": "High",
    "description": "Now in progress",
    "external_id": "AUTH-001",
    "url": "https://www.notion.so/...",
    "created_time": "2026-05-16T10:00:00.000Z",
    "last_edited_time": "2026-05-16T10:05:00.000Z"
  }
}
```

## move_issue_status

Input:

```json
{
  "page_id": "PAGE_ID",
  "status": "Done"
}
```

Output:

```json
{
  "ok": true,
  "data": {
    "id": "PAGE_ID",
    "title": "Implement login",
    "status": "Done",
    "priority": "High",
    "description": "Initial auth flow",
    "external_id": "AUTH-001",
    "url": "https://www.notion.so/...",
    "created_time": "2026-05-16T10:00:00.000Z",
    "last_edited_time": "2026-05-16T10:10:00.000Z"
  }
}
```

## append_issue_content

Input:

```json
{
  "page_id": "PAGE_ID",
  "markdown": "## Notes\n- [x] Done"
}
```

Output:

```json
{
  "ok": true,
  "data": {
    "page_id": "PAGE_ID",
    "appended": 2,
    "result": {
      "object": "list",
      "results": []
    }
  }
}
```

## get_status_options

Input:

```json
{
  "data_source_id": "DATA_SOURCE_ID"
}
```

Output:

```json
{
  "ok": true,
  "data": {
    "data_source_id": "DATA_SOURCE_ID",
    "status_property": "Status",
    "options": ["Backlog", "Ready", "In Progress", "In Review", "Done"]
  }
}
```
