from __future__ import annotations

from typing import Any, Dict, List, Optional

from notion_client import Client

from utils.notion_helpers import (
    extract_page_properties,
    get_block_children_recursive,
    markdown_to_blocks,
    paginate,
    rich_text,
    rich_text_to_plain_text,
)


class NotionKanbanService:
    def __init__(self, notion_token: str, notion_version: str = "2026-03-11") -> None:
        self.notion = Client(
            auth=notion_token,
            notion_version=notion_version,
        )

    def ensure_project_board(
        self,
        root_page_id: str,
        project_name: str,
        statuses: List[str],
        default_status: str,
    ) -> Dict[str, Any]:
        existing_database_id = self._find_child_database_id(root_page_id, project_name)

        if existing_database_id:
            database = self.notion.databases.retrieve(database_id=existing_database_id)
            data_source_id = self._get_data_source_id(database)
            board_view_id = self._try_get_board_view_id(existing_database_id, data_source_id)
            return {
                "created": False,
                "database_id": existing_database_id,
                "data_source_id": data_source_id,
                "board_view_id": board_view_id,
                "board_view_created": False,
                "statuses": statuses,
                "default_status": default_status,
            }

        create_response = self.notion.databases.create(
            parent={
                "type": "page_id",
                "page_id": root_page_id,
            },
            title=rich_text(project_name),
            is_inline=True,
            initial_data_source={
                "title": rich_text("Issues Source"),
                "properties": {
                    "Name": {"title": {}},
                    "Status": {
                        "status": {
                            "options": [
                                {"name": status_name}
                                for status_name in statuses
                            ]
                        }
                    },
                    "Priority": {
                        "select": {
                            "options": [
                                {"name": "Low"},
                                {"name": "Medium"},
                                {"name": "High"},
                            ]
                        }
                    },
                    "Description": {"rich_text": {}},
                    "External ID": {"rich_text": {}},
                },
            },
        )

        database_id = create_response["id"]
        database = self.notion.databases.retrieve(database_id=database_id)
        data_source_id = self._get_data_source_id(database)

        board_view_id = None
        board_view_created = False
        board_view_error = None
        note = None

        try:
            board_view = self._create_board_view(database_id, data_source_id)
            board_view_id = board_view.get("id")
            board_view_created = bool(board_view_id)
        except Exception as exc:  # noqa: BLE001
            board_view_error = str(exc)
            note = (
                "Database and data source were created successfully, "
                "but board view creation failed or is unsupported by the current API."
            )

        return {
            "created": True,
            "database_id": database_id,
            "data_source_id": data_source_id,
            "board_view_id": board_view_id,
            "board_view_created": board_view_created,
            "board_view_error": board_view_error,
            "note": note,
            "statuses": statuses,
            "default_status": default_status,
        }

    def get_project_context(self, root_page_id: str, project_name: str) -> Dict[str, Any]:
        statuses = ["Backlog", "Ready", "In Progress", "In Review", "Done"]
        ensure_result = self.ensure_project_board(
            root_page_id=root_page_id,
            project_name=project_name,
            statuses=statuses,
            default_status="Backlog",
        )

        data_source_id = ensure_result["data_source_id"]
        issues = self.list_issues(data_source_id, status=None, include_blocks=False, limit=100)[
            "issues"
        ]

        kanban = {status: [] for status in statuses}
        for issue in issues:
            issue_status = issue.get("status") or "Backlog"
            if issue_status not in kanban:
                kanban[issue_status] = []
            kanban[issue_status].append(issue)

        summary = {
            "total_issues": len(issues),
            "by_status": {status: len(kanban.get(status, [])) for status in kanban},
        }

        return {
            "root_page_id": root_page_id,
            "database_id": ensure_result["database_id"],
            "data_source_id": data_source_id,
            "board_view_id": ensure_result.get("board_view_id"),
            "project_name": project_name,
            "statuses": statuses,
            "summary": summary,
            "kanban": kanban,
        }

    def list_issues(
        self,
        data_source_id: str,
        status: Optional[str] = None,
        include_blocks: bool = False,
        limit: int = 100,
    ) -> Dict[str, Any]:
        filter_payload = None
        if status:
            filter_payload = {
                "property": "Status",
                "status": {"equals": status},
            }

        results = self._query_data_source(
            data_source_id=data_source_id,
            filter_payload=filter_payload,
            limit=limit,
        )

        issues: List[Dict[str, Any]] = []
        for page in results:
            issue = self._compact_issue(page)
            if include_blocks:
                issue["blocks"] = get_block_children_recursive(self.notion, page["id"])
            issues.append(issue)

        return {
            "data_source_id": data_source_id,
            "count": len(issues),
            "issues": issues,
        }

    def get_issue(self, page_id: str, include_blocks: bool = True) -> Dict[str, Any]:
        page = self.notion.pages.retrieve(page_id=page_id)
        issue = self._compact_issue(page)
        if include_blocks:
            issue["blocks"] = get_block_children_recursive(self.notion, page_id)
        return issue

    def create_issue(
        self,
        data_source_id: str,
        title: str,
        status: str,
        priority: str,
        description: str = "",
        external_id: Optional[str] = None,
        details_markdown: Optional[str] = None,
    ) -> Dict[str, Any]:
        if external_id:
            existing = self._find_issue_by_external_id(data_source_id, external_id)
            if existing:
                return {
                    "created": False,
                    "issue": self._compact_issue(existing),
                }

        properties = {
            "Name": {"title": rich_text(title)},
            "Status": {"status": {"name": status}},
            "Priority": {"select": {"name": priority}},
            "Description": {"rich_text": rich_text(description)},
        }

        if external_id:
            properties["External ID"] = {"rich_text": rich_text(external_id)}

        body: Dict[str, Any] = {
            "parent": {"type": "data_source_id", "data_source_id": data_source_id},
            "properties": properties,
        }

        if details_markdown:
            children = markdown_to_blocks(details_markdown)
            if children:
                body["children"] = children

        page = self.notion.pages.create(**body)
        return {
            "created": True,
            "issue": self._compact_issue(page),
        }

    def update_issue(
        self,
        page_id: str,
        title: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        description: Optional[str] = None,
        external_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if title is not None:
            properties["Name"] = {"title": rich_text(title)}

        if status is not None:
            properties["Status"] = {"status": {"name": status}}

        if priority is not None:
            properties["Priority"] = {"select": {"name": priority}}

        if description is not None:
            properties["Description"] = {"rich_text": rich_text(description)}

        if external_id is not None:
            properties["External ID"] = {"rich_text": rich_text(external_id)}

        if not properties:
            raise ValueError("No properties provided to update.")

        page = self.notion.pages.update(page_id=page_id, properties=properties)
        return self._compact_issue(page)

    def move_issue(self, page_id: str, status: str) -> Dict[str, Any]:
        return self.update_issue(page_id=page_id, status=status)

    def append_issue_content(self, page_id: str, markdown: str) -> Dict[str, Any]:
        children = markdown_to_blocks(markdown)
        if not children:
            return {"page_id": page_id, "appended": 0}

        response = self.notion.blocks.children.append(
            block_id=page_id,
            children=children,
        )
        return {
            "page_id": page_id,
            "appended": len(children),
            "result": response,
        }

    def get_status_options(self, data_source_id: str) -> Dict[str, Any]:
        data_source = self.notion.data_sources.retrieve(data_source_id=data_source_id)
        status_property = self._find_property_by_type(data_source, "status")
        options = []
        if status_property:
            options = data_source["properties"][status_property]["status"].get("options", [])
        return {
            "data_source_id": data_source_id,
            "status_property": status_property,
            "options": [opt.get("name") for opt in options],
        }

    def _compact_issue(self, page: Dict[str, Any]) -> Dict[str, Any]:
        props = extract_page_properties(page)
        return {
            "id": page.get("id"),
            "title": props.get("Name"),
            "status": props.get("Status"),
            "priority": props.get("Priority"),
            "description": props.get("Description"),
            "external_id": props.get("External ID"),
            "url": page.get("url"),
            "created_time": page.get("created_time"),
            "last_edited_time": page.get("last_edited_time"),
        }

    def _find_child_database_id(self, root_page_id: str, project_name: str) -> Optional[str]:
        children = paginate(
            self.notion.blocks.children.list,
            block_id=root_page_id,
            page_size=100,
        )

        for block in children:
            if block.get("type") != "child_database":
                continue
            title = block.get("child_database", {}).get("title", "")
            if title.strip().lower() == project_name.strip().lower():
                return block.get("id")

        return None

    def _get_data_source_id(self, database: Dict[str, Any]) -> str:
        data_sources = database.get("data_sources", [])
        if not data_sources:
            raise RuntimeError("Database has no data_sources.")
        return data_sources[0]["id"]

    def _find_property_by_type(self, data_source: Dict[str, Any], prop_type: str) -> Optional[str]:
        for name, prop in data_source.get("properties", {}).items():
            if prop.get("type") == prop_type:
                return name
        return None

    def _query_data_source(
        self,
        data_source_id: str,
        filter_payload: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        kwargs: Dict[str, Any] = {
            "data_source_id": data_source_id,
            "page_size": min(limit, 100),
        }

        if filter_payload:
            kwargs["filter"] = filter_payload

        return paginate(self.notion.data_sources.query, limit=limit, **kwargs)

    def _find_issue_by_external_id(
        self, data_source_id: str, external_id: str
    ) -> Optional[Dict[str, Any]]:
        filter_payload = {
            "property": "External ID",
            "rich_text": {"equals": external_id},
        }

        results = self._query_data_source(
            data_source_id=data_source_id,
            filter_payload=filter_payload,
            limit=1,
        )
        return results[0] if results else None

    def _raw_request(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.notion.request(
            path=path,
            method=method,
            body=body or {},
        )

    def _create_board_view(self, database_id: str, data_source_id: str) -> Dict[str, Any]:
        body = {
            "database_id": database_id,
            "data_source_id": data_source_id,
            "name": "Board",
            "type": "board",
        }
        return self._raw_request(method="post", path="views", body=body)

    def _try_get_board_view_id(
        self, database_id: str, data_source_id: str
    ) -> Optional[str]:
        try:
            response = self._raw_request(
                method="get",
                path="views",
                body={"database_id": database_id, "data_source_id": data_source_id},
            )
            results = response.get("results", []) if isinstance(response, dict) else []
            for view in results:
                if view.get("type") == "board":
                    return view.get("id")
        except Exception:  # noqa: BLE001
            return None
        return None
