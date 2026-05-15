from notion_client import Client
from typing import Optional


class NotionService:
    def __init__(self, api_key: str):
        self.client = Client(auth=api_key)

    def create_page(self, parent_id: str, title: str, content: str = "") -> dict:
        """Create a new page under the given parent page."""
        children = []
        if content:
            # Split content into paragraphs and create blocks
            paragraphs = content.split("\n")
            for para in paragraphs:
                if para.strip():
                    children.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": para}}]
                        }
                    })

        response = self.client.pages.create(
            parent={"page_id": parent_id},
            properties={
                "title": [{"text": {"content": title}}]
            },
            children=children
        )
        return response

    def create_kanban(self, parent_id: str, title: str = "Project Kanban") -> dict:
        """Create a kanban-style database with default statuses and issue properties."""
        statuses = [
            {"name": "Backlog", "color": "default"},
            {"name": "Ready", "color": "blue"},
            {"name": "In Progress", "color": "yellow"},
            {"name": "In Review", "color": "orange"},
            {"name": "Done", "color": "green"},
        ]

        properties = {
            "Name": {"title": {}},
            "Status": {
                "select": {
                    "options": statuses
                }
            },
            "Priority": {
                "select": {
                    "options": [
                        {"name": "Low", "color": "gray"},
                        {"name": "Medium", "color": "blue"},
                        {"name": "High", "color": "orange"},
                        {"name": "Urgent", "color": "red"},
                    ]
                }
            },
            "Assignee": {"rich_text": {}},
            "Reviewer": {"rich_text": {}},
            "Milestone": {"rich_text": {}},
            "Description": {"rich_text": {}},
        }

        response = self.client.databases.create(
            parent={"type": "page_id", "page_id": parent_id},
            title=[{"type": "text", "text": {"content": title}}],
            properties=properties,
            is_inline=True
        )
        return response

    def create_status(self, database_id: str, status_name: str, color: str = "default") -> dict:
        """Add a new status option to a kanban database's Status select property."""
        # First, get existing database to read current options
        db = self.client.databases.retrieve(database_id=database_id)
        existing_options = db["properties"]["Status"]["select"]["options"]

        # Check if status already exists
        for opt in existing_options:
            if opt["name"].lower() == status_name.lower():
                return {"message": f"Status '{status_name}' already exists", "database": db}

        # Add new status
        existing_options.append({"name": status_name, "color": color})

        response = self.client.databases.update(
            database_id=database_id,
            properties={
                "Status": {
                    "select": {
                        "options": existing_options
                    }
                }
            }
        )
        return response

    def create_issue(
        self,
        database_id: str,
        name: str,
        description: str = "",
        assignee: Optional[str] = None,
        reviewer: Optional[str] = None,
        milestone: Optional[str] = None,
        priority: str = "Medium",
        status: str = "Backlog",
    ) -> dict:
        """Create a new issue (page) in the kanban database."""
        properties = {
            "Name": {"title": [{"text": {"content": name}}]},
            "Status": {"select": {"name": status}},
            "Priority": {"select": {"name": priority}},
        }

        if assignee:
            properties["Assignee"] = {"rich_text": [{"text": {"content": assignee}}]}
        if reviewer:
            properties["Reviewer"] = {"rich_text": [{"text": {"content": reviewer}}]}
        if milestone:
            properties["Milestone"] = {"rich_text": [{"text": {"content": milestone}}]}
        if description:
            properties["Description"] = {"rich_text": [{"text": {"content": description}}]}

        response = self.client.pages.create(
            parent={"database_id": database_id},
            properties=properties,
        )
        return response

    def edit_issue(
        self,
        page_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        assignee: Optional[str] = None,
        reviewer: Optional[str] = None,
        milestone: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
    ) -> dict:
        """Edit an existing issue's properties."""
        properties = {}

        if name is not None:
            properties["Name"] = {"title": [{"text": {"content": name}}]}
        if status is not None:
            properties["Status"] = {"select": {"name": status}}
        if priority is not None:
            properties["Priority"] = {"select": {"name": priority}}
        if assignee is not None:
            properties["Assignee"] = {"rich_text": [{"text": {"content": assignee}}]}
        if reviewer is not None:
            properties["Reviewer"] = {"rich_text": [{"text": {"content": reviewer}}]}
        if milestone is not None:
            properties["Milestone"] = {"rich_text": [{"text": {"content": milestone}}]}
        if description is not None:
            properties["Description"] = {"rich_text": [{"text": {"content": description}}]}

        if not properties:
            return {"message": "No fields to update"}

        response = self.client.pages.update(
            page_id=page_id,
            properties=properties,
        )
        return response

    def remove_issue(self, page_id: str) -> dict:
        """Archive (soft-delete) an issue by setting archived=True."""
        response = self.client.pages.update(
            page_id=page_id,
            archived=True,
        )
        return response

    def get_issue(self, page_id: str) -> dict:
        """Retrieve an issue's full details."""
        response = self.client.pages.retrieve(page_id=page_id)

        # Parse into a cleaner format
        props = response.get("properties", {})

        def get_title(prop):
            title_arr = prop.get("title", [])
            return title_arr[0]["text"]["content"] if title_arr else ""

        def get_rich_text(prop):
            rt_arr = prop.get("rich_text", [])
            return rt_arr[0]["text"]["content"] if rt_arr else ""

        def get_select(prop):
            sel = prop.get("select")
            return sel["name"] if sel else ""

        parsed = {
            "id": response["id"],
            "url": response.get("url", ""),
            "created_time": response.get("created_time", ""),
            "last_edited_time": response.get("last_edited_time", ""),
            "archived": response.get("archived", False),
            "name": get_title(props.get("Name", {})),
            "status": get_select(props.get("Status", {})),
            "priority": get_select(props.get("Priority", {})),
            "assignee": get_rich_text(props.get("Assignee", {})),
            "reviewer": get_rich_text(props.get("Reviewer", {})),
            "milestone": get_rich_text(props.get("Milestone", {})),
            "description": get_rich_text(props.get("Description", {})),
        }
        return parsed
