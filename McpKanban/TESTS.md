# MCP Tool Test Commands

These are example AgentCore commands for the new MCP tools. Replace placeholder IDs with real values.

## ensure_project_board

```bash
agentcore dev call-tool --tool ensure_project_board --input '{"input": {"root_page_id": "de5e7909de8142a79f1b07ddce89cedf", "project_name": "Project Kanban"}}'
```
ensure_project_board {"input": {"root_page_id": "de5e7909de8142a79f1b07ddce89cedf", "project_name": "Project Kanban"}}
## get_project_context

```bash
agentcore dev call-tool --tool get_project_context --input '{"input": {"root_page_id": "de5e7909de8142a79f1b07ddce89cedf", "project_name": "Project Kanban"}}'
```

## list_issues

```bash
agentcore dev call-tool --tool list_issues --input '{"input": {"data_source_id": "a7440b1a-7b46-4cde-b099-68c02f729b5d", "status": "Done", "include_blocks": true, "limit": 100}}'
```

## get_issue

```bash
agentcore dev call-tool --tool get_issue --input '{"input": {"page_id": "PAGE_ID", "include_blocks": true}}'
```

## create_issue

```bash
agentcore dev call-tool --tool create_issue --input '{"input": {"data_source_id": "DATA_SOURCE_ID", "title": "Implement login", "status": "Backlog", "priority": "High", "description": "Initial auth flow", "external_id": "AUTH-001", "details_markdown": "## Context\n- [ ] Create UI\n- [ ] Integrate"}}'
```

## update_issue

```bash
agentcore dev call-tool --tool update_issue --input '{"input": {"page_id": "PAGE_ID", "status": "In Progress", "description": "Now in progress"}}'
```

## move_issue_status

```bash
agentcore dev call-tool --tool move_issue_status --input '{"input": {"page_id": "PAGE_ID", "status": "Done"}}'
```

## append_issue_content

```bash
agentcore dev call-tool --tool append_issue_content --input '{"input": {"page_id": "PAGE_ID", "markdown": "## Notes\n- [x] Done"}}'
```

## get_status_options

```bash
agentcore dev call-tool --tool get_status_options --input '{"input": {"data_source_id": "DATA_SOURCE_ID"}}'
```
