from __future__ import annotations

from enum import Enum
from typing import Literal, Optional, Union

from pydantic import BaseModel


class Priority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class IssueStatus(str, Enum):
    BACKLOG = "Backlog"
    READY = "Ready"
    IN_PROGRESS = "In Progress"
    IN_REVIEW = "In Review"
    DONE = "Done"


class CreateAction(BaseModel):
    action: Literal["create"] = "create"
    title: str
    status: IssueStatus
    priority: Priority
    description: str
    details_markdown: Optional[str] = None
    external_id: str
    assignee_ids: Optional[list[str]] = None
    reviewer_ids: Optional[list[str]] = None


class UpdateAction(BaseModel):
    action: Literal["update"] = "update"
    page_id: str
    title: Optional[str] = None
    status: Optional[IssueStatus] = None
    priority: Optional[Priority] = None
    description: Optional[str] = None
    assignee_ids: Optional[list[str]] = None
    reviewer_ids: Optional[list[str]] = None


class MoveStatusAction(BaseModel):
    action: Literal["move_status"] = "move_status"
    page_id: str
    new_status: IssueStatus


class AppendContentAction(BaseModel):
    action: Literal["append_content"] = "append_content"
    page_id: str
    markdown: str


class KanbanPlan(BaseModel):
    summary: str
    meeting_context: str
    actions: list[Union[CreateAction, UpdateAction, MoveStatusAction, AppendContentAction]]
