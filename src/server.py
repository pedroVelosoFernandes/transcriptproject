import os
import json
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from notion_service import NotionService
from models import (
    CreatePageInput,
    CreateKanbanInput,
    CreateStatusInput,
    CreateIssueInput,
    EditIssueInput,
    RemoveIssueInput,
    GetIssueInput,
)

load_dotenv()

mcp = FastMCP(
    "Notion Kanban MCP",
)


def get_notion_service() -> NotionService:
    api_key = os.getenv("NOTION_API_KEY")
    if not api_key:
        raise ValueError("NOTION_API_KEY environment variable is not set")
    return NotionService(api_key)


@mcp.tool()
def create_page(input: CreatePageInput) -> str:
    """Create a new Notion page under a parent page."""
    service = get_notion_service()
    result = service.create_page(
        parent_id=input.parent_id,
        title=input.title,
        content=input.content,
    )
    return json.dumps({"id": result["id"], "url": result.get("url", "")}, indent=2)


@mcp.tool()
def create_kanban(input: CreateKanbanInput) -> str:
    """Create a kanban board (Notion database) with default statuses: Backlog, Ready, In Progress, In Review, Done. Includes properties for Priority, Assignee, Reviewer, Milestone, and Description."""
    service = get_notion_service()
    result = service.create_kanban(
        parent_id=input.parent_id,
        title=input.title,
    )
    return json.dumps({"id": result["id"], "url": result.get("url", ""), "title": input.title}, indent=2)


@mcp.tool()
def create_status(input: CreateStatusInput) -> str:
    """Add a new status option to an existing kanban database's Status property."""
    service = get_notion_service()
    result = service.create_status(
        database_id=input.database_id,
        status_name=input.status_name,
        color=input.color,
    )
    if "message" in result:
        return json.dumps({"message": result["message"]}, indent=2)
    return json.dumps({"id": result["id"], "status_added": input.status_name}, indent=2)


@mcp.tool()
def create_issue(input: CreateIssueInput) -> str:
    """Create a new issue in the kanban board with assignee, reviewer, priority, milestone, and status."""
    service = get_notion_service()
    result = service.create_issue(
        database_id=input.database_id,
        name=input.name,
        description=input.description,
        assignee=input.assignee,
        reviewer=input.reviewer,
        milestone=input.milestone,
        priority=input.priority.value,
        status=input.status.value,
    )
    return json.dumps({"id": result["id"], "url": result.get("url", ""), "name": input.name}, indent=2)


@mcp.tool()
def edit_issue(input: EditIssueInput) -> str:
    """Edit an existing issue's properties (name, description, assignee, reviewer, milestone, priority, status)."""
    service = get_notion_service()
    result = service.edit_issue(
        page_id=input.page_id,
        name=input.name,
        description=input.description,
        assignee=input.assignee,
        reviewer=input.reviewer,
        milestone=input.milestone,
        priority=input.priority.value if input.priority else None,
        status=input.status,
    )
    if "message" in result:
        return json.dumps({"message": result["message"]}, indent=2)
    return json.dumps({"id": result["id"], "url": result.get("url", ""), "updated": True}, indent=2)


@mcp.tool()
def remove_issue(input: RemoveIssueInput) -> str:
    """Archive/remove an issue from the kanban board."""
    service = get_notion_service()
    result = service.remove_issue(page_id=input.page_id)
    return json.dumps({"id": result["id"], "archived": True}, indent=2)


@mcp.tool()
def get_issue(input: GetIssueInput) -> str:
    """Get full details of an issue including status, priority, assignee, reviewer, milestone, and description."""
    service = get_notion_service()
    result = service.get_issue(page_id=input.page_id)
    return json.dumps(result, indent=2)


def main():
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
