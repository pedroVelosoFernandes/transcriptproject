from __future__ import annotations

import os
import traceback
from typing import Any, Dict

from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP


from schemas.kanban import (
    BoardRef,
    IssueContentAppendInput,
    IssueCreateInput,
    IssueGetInput,
    IssueListInput,
    IssueMoveInput,
    IssueUpdateInput,
)
from services.notion_kanban_service import NotionKanbanService

load_dotenv()

mcp = FastMCP("Notion Kanban MCP",host="0.0.0.0", json_response=True, stateless_http=True)


def _debug_enabled() -> bool:
    return os.getenv("DEBUG", "false").lower() == "true"


def _ok(data: Any) -> Dict[str, Any]:
    return {"ok": True, "data": data}


def _fail(exc: Exception) -> Dict[str, Any]:
    error = {
        "type": exc.__class__.__name__,
        "message": str(exc),
    }
    if _debug_enabled():
        error["traceback"] = traceback.format_exc()
    return {"ok": False, "error": error}


def _get_service() -> NotionKanbanService:
    notion_token = os.getenv("NOTION_TOKEN")
    if not notion_token:
        raise ValueError("NOTION_TOKEN environment variable is not set")
    notion_version = os.getenv("NOTION_VERSION", "2026-03-11")
    return NotionKanbanService(notion_token=notion_token, notion_version=notion_version)


@mcp.tool()
def ensure_project_board(input: BoardRef) -> Dict[str, Any]:
    """Ensure a project Kanban exists under the given root page.

    Input:
    - root_page_id: Notion page id that will contain the project database.
    - project_name: Database title to find or create under the root page.
    Output: ok/data with database_id, data_source_id, board_view_id, created.
    """
    try:
        service = _get_service()
        data = service.ensure_project_board(
            root_page_id=input.root_page_id,
            project_name=input.project_name,
            statuses=["Backlog", "Ready", "In Progress", "In Review", "Done"],
            default_status="Backlog",
        )
        return _ok(data)
    except Exception as exc:  # noqa: BLE001
        return _fail(exc)


@mcp.tool()
def get_project_context(input: BoardRef) -> Dict[str, Any]:
    """Return a compact kanban summary grouped by status for a project.

    Input:
    - root_page_id: Notion page id that contains the project database.
    - project_name: Database title used to locate the kanban board.
    Output: ok/data with summary totals and kanban grouped by status.
    """
    try:
        service = _get_service()
        data = service.get_project_context(
            root_page_id=input.root_page_id,
            project_name=input.project_name,
        )
        return _ok(data)
    except Exception as exc:  # noqa: BLE001
        return _fail(exc)


@mcp.tool()
def list_issues(input: IssueListInput) -> Dict[str, Any]:
    """List issues from a data source with optional status filtering.

    Input:
    - data_source_id: Notion data source id where the issues live.
    - status: Optional status filter (e.g., Backlog).
    - include_blocks: When true, includes issue blocks in the response.
    - limit: Max number of issues to return (default 100).
    Output: ok/data with issues list and count.
    """
    try:
        service = _get_service()
        data = service.list_issues(
            data_source_id=input.data_source_id,
            status=input.status.value if input.status else None,
            include_blocks=input.include_blocks,
            limit=input.limit,
        )
        return _ok(data)
    except Exception as exc:  # noqa: BLE001
        return _fail(exc)


@mcp.tool()
def get_issue(input: IssueGetInput) -> Dict[str, Any]:
    """Fetch a single issue by page id, optionally including blocks.

    Input:
    - page_id: Notion page id of the issue.
    - include_blocks: When true, includes issue blocks in the response.
    Output: ok/data with issue fields and optional blocks.
    """
    try:
        service = _get_service()
        data = service.get_issue(
            page_id=input.page_id,
            include_blocks=input.include_blocks,
        )
        return _ok(data)
    except Exception as exc:  # noqa: BLE001
        return _fail(exc)


@mcp.tool()
def create_issue(input: IssueCreateInput) -> Dict[str, Any]:
    """Create an issue in a data source, idempotent by External ID.

    Input:
    - data_source_id: Notion data source id where the issue will be created.
    - title: Issue title (mapped to the Name property).
    - status: Issue status value (must match the Status options).
    - priority: Issue priority value (must match the Priority options).
    - description: Short description text.
    - external_id: Optional idempotency key stored in External ID.
    - details_markdown: Optional markdown converted to blocks inside the issue.
    - assignee_ids: Optional list of Notion user IDs to assign.
    - reviewer_ids: Optional list of Notion user IDs as reviewers.
    Output: ok/data with created flag and issue.
    """
    try:
        service = _get_service()
        data = service.create_issue(
            data_source_id=input.data_source_id,
            title=input.title,
            status=input.status.value,
            priority=input.priority.value,
            description=input.description,
            external_id=input.external_id,
            details_markdown=input.details_markdown,
            assignee_ids=input.assignee_ids,
            reviewer_ids=input.reviewer_ids,
        )
        return _ok(data)
    except Exception as exc:  # noqa: BLE001
        return _fail(exc)


@mcp.tool()
def update_issue(input: IssueUpdateInput) -> Dict[str, Any]:
    """Update an issue properties by page id.

    Input:
    - page_id: Notion page id of the issue to update.
    - title: New title, if changing the Name property.
    - status: New status value.
    - priority: New priority value.
    - description: New description value.
    - external_id: New external id stored in External ID.
    - assignee_ids: List of Notion user IDs to assign.
    - reviewer_ids: List of Notion user IDs as reviewers.
    Output: ok/data with updated issue fields.
    """
    try:
        service = _get_service()
        data = service.update_issue(
            page_id=input.page_id,
            title=input.title,
            status=input.status.value if input.status else None,
            priority=input.priority.value if input.priority else None,
            description=input.description,
            external_id=input.external_id,
            assignee_ids=input.assignee_ids,
            reviewer_ids=input.reviewer_ids,
        )
        return _ok(data)
    except Exception as exc:  # noqa: BLE001
        return _fail(exc)


@mcp.tool()
def move_issue_status(input: IssueMoveInput) -> Dict[str, Any]:
    """Move an issue between statuses by updating its Status property.

    Input:
    - page_id: Notion page id of the issue to move.
    - status: Target status value.
    Output: ok/data with updated issue fields.
    """
    try:
        service = _get_service()
        data = service.move_issue(
            page_id=input.page_id,
            status=input.status.value,
        )
        return _ok(data)
    except Exception as exc:  # noqa: BLE001
        return _fail(exc)


@mcp.tool()
def append_issue_content(input: IssueContentAppendInput) -> Dict[str, Any]:
    """Append markdown content to an issue page as Notion blocks.

    Input:
    - page_id: Notion page id of the issue to append content to.
    - markdown: Markdown text to append as Notion blocks.
    Output: ok/data with appended count.
    """
    try:
        service = _get_service()
        data = service.append_issue_content(
            page_id=input.page_id,
            markdown=input.markdown,
        )
        return _ok(data)
    except Exception as exc:  # noqa: BLE001
        return _fail(exc)


@mcp.tool()
def get_status_options(data_source_id: str) -> Dict[str, Any]:
    """Return available status options for a data source.

    Input:
    - data_source_id: Notion data source id to read status options from.
    Output: ok/data with status options list.
    """
    try:
        service = _get_service()
        data = service.get_status_options(data_source_id=data_source_id)
        return _ok(data)
    except Exception as exc:  # noqa: BLE001
        return _fail(exc)


@mcp.tool()
def list_workspace_members() -> Dict[str, Any]:
    """List all people (non-bot) members in the Notion workspace.

    Use this to resolve user names to Notion user IDs for assignee/reviewer fields.
    Output: ok/data with count and members list (id, name, email, avatar_url).
    """
    try:
        service = _get_service()
        data = service.list_workspace_members()
        return _ok(data)
    except Exception as exc:  # noqa: BLE001
        return _fail(exc)


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
