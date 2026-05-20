import os

from dotenv import load_dotenv

import utils

load_dotenv()

utils.put_ssm_parameter("/app/kanban/agentcore/user_pool_id", os.getenv("KANBAN_USER_POOL_ID", "my-domain-wtcl4o17"))
utils.put_ssm_parameter("/app/kanban/agentcore/client_id", os.getenv("KANBAN_CLIENT_ID", "42lqalo5vsb6ofoboq0dgvfb4i"))
utils.put_ssm_parameter("/app/kanban/agentcore/client_secret", os.getenv("KANBAN_CLIENT_SECRET", "aunpt83og1e6g8blgbt0tkg671d9hb6bb5vi5n2n2rl2nph9mp9"))
utils.put_ssm_parameter("/app/kanban/agentcore/gatewayURL", os.getenv("KANBAN_GATEWAY_URL", "https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3Aaws%3Abedrock-agentcore%3Aus-east-1%3A631510543425%3Aruntime%2FMcpKanban_mcp_notion-fqxbZC8Hzs/invocations?qualifier=DEFAULT"))
utils.put_ssm_parameter("/app/kanban/agentcore/memory_id", os.getenv("KANBAN_MEMORY_ID", "OrchestratorKanban_agent_orchestratorMemory-wuGgvYFve9"))
utils.put_ssm_parameter("/app/kanban/agentcore/username", os.getenv("KANBAN_USERNAME", "agent-user-kjg5z4"))
utils.put_ssm_parameter("/app/kanban/agentcore/default_root_page_id", os.getenv("KANBAN_DEFAULT_ROOT_PAGE_ID", "de5e7909de8142a79f1b07ddce89cedf"))
utils.put_ssm_parameter("/app/kanban/agentcore/default_project_name", os.getenv("KANBAN_DEFAULT_PROJECT_NAME", "Project Kanban"))