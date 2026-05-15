from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"


class DefaultStatus(str, Enum):
    BACKLOG = "Backlog"
    READY = "Ready"
    IN_PROGRESS = "In Progress"
    IN_REVIEW = "In Review"
    DONE = "Done"


class CreatePageInput(BaseModel):
    parent_id: str = Field(description="The parent page ID where the new page will be created")
    title: str = Field(description="Title of the new page")
    content: str = Field(default="", description="Content of the page in markdown")


class CreateKanbanInput(BaseModel):
    parent_id: str = Field(description="The parent page ID where the kanban database will be created")
    title: str = Field(default="Project Kanban", description="Title of the kanban board")


class CreateStatusInput(BaseModel):
    database_id: str = Field(description="The database ID to add the status to")
    status_name: str = Field(description="Name of the new status")
    color: str = Field(default="default", description="Color for the status (blue, green, red, yellow, orange, purple, pink, gray, default)")


class CreateIssueInput(BaseModel):
    database_id: str = Field(description="The kanban database ID")
    name: str = Field(description="Issue title")
    description: str = Field(default="", description="Issue description")
    assignee: Optional[str] = Field(default=None, description="Person assigned to the issue")
    reviewer: Optional[str] = Field(default=None, description="Person reviewing the issue")
    milestone: Optional[str] = Field(default=None, description="Milestone/sprint for the issue")
    priority: Priority = Field(default=Priority.MEDIUM, description="Issue priority")
    status: DefaultStatus = Field(default=DefaultStatus.BACKLOG, description="Initial status")


class EditIssueInput(BaseModel):
    page_id: str = Field(description="The issue page ID to edit")
    name: Optional[str] = Field(default=None, description="New issue title")
    description: Optional[str] = Field(default=None, description="New issue description")
    assignee: Optional[str] = Field(default=None, description="New assignee")
    reviewer: Optional[str] = Field(default=None, description="New reviewer")
    milestone: Optional[str] = Field(default=None, description="New milestone")
    priority: Optional[Priority] = Field(default=None, description="New priority")
    status: Optional[str] = Field(default=None, description="New status")


class RemoveIssueInput(BaseModel):
    page_id: str = Field(description="The issue page ID to archive/remove")


class GetIssueInput(BaseModel):
    page_id: str = Field(description="The issue page ID to retrieve")
