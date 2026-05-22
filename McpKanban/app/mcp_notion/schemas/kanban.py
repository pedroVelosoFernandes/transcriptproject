from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class IssueStatus(str, Enum):
    backlog = "Backlog"
    ready = "Ready"
    in_progress = "In Progress"
    in_review = "In Review"
    done = "Done"


class IssuePriority(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


class BoardRef(BaseModel):
    root_page_id: str = Field(..., description="Notion root page id")
    project_name: str = Field(..., description="Project name / database title")


class IssueListInput(BaseModel):
    data_source_id: str
    status: Optional[IssueStatus] = None
    include_blocks: bool = False
    limit: int = 100


class IssueGetInput(BaseModel):
    page_id: str
    include_blocks: bool = True


class IssueCreateInput(BaseModel):
    data_source_id: str
    title: str
    status: IssueStatus = IssueStatus.backlog
    priority: IssuePriority = IssuePriority.medium
    description: str = ""
    external_id: Optional[str] = None
    details_markdown: Optional[str] = None
    assignee_ids: Optional[list[str]] = Field(None, description="List of Notion user IDs to assign")
    reviewer_ids: Optional[list[str]] = Field(None, description="List of Notion user IDs as reviewers")


class IssueUpdateInput(BaseModel):
    page_id: str
    title: Optional[str] = None
    status: Optional[IssueStatus] = None
    priority: Optional[IssuePriority] = None
    description: Optional[str] = None
    external_id: Optional[str] = None
    assignee_ids: Optional[list[str]] = Field(None, description="List of Notion user IDs to assign")
    reviewer_ids: Optional[list[str]] = Field(None, description="List of Notion user IDs as reviewers")


class IssueMoveInput(BaseModel):
    page_id: str
    status: IssueStatus


class IssueContentAppendInput(BaseModel):
    page_id: str
    markdown: str
