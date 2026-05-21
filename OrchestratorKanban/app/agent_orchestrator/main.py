import os

from strands import Agent
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from boto3 import Session

from model.load import load_model
from mcp_client.client import get_streamable_http_mcp_client
from memory.session import get_memory_session_manager
from planner.agent import create_planner_tool
from orchestrator.prompts import ORCHESTRATOR_SYSTEM_PROMPT
import utils

app = BedrockAgentCoreApp()
model = load_model()
logger = app.logger

gateway_url = utils.get_ssm_parameter("/app/kanban/agentcore/gatewayURL")

planner_tool = create_planner_tool()


def create_orchestrator_agent_runtime(query, session_manager):
    base_tools = [planner_tool]

    cognito_token = utils.get_cognito_token()
    mcp_client = get_streamable_http_mcp_client(cognito_token, gateway_url)

    logger.info("Entering mcp_client context...")
    with mcp_client:
        try:
            logger.info(f"Listing MCP tools from {gateway_url}...")
            mcp_tools = mcp_client.list_tools_sync()
            logger.info(f"Loaded {len(mcp_tools)} MCP tools from gateway.")
            all_tools = base_tools + mcp_tools
        except Exception as e:
            logger.error(f"Failed to load MCP tools: {e}. Using planner only.")
            all_tools = base_tools

        orchestrator = Agent(
            model=model,
            system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
            tools=all_tools,
            session_manager=session_manager,
        )
        logger.info("Orchestrator agent created with planner + MCP tools")

        response = orchestrator(query)
        logger.info("Orchestrator finished processing")
        return response


@app.entrypoint
def invoke(payload, context):
    action = payload.get("action", "")
    user_message = payload.get("inputText") or payload.get("prompt")

    notion_token = payload.get("notion_token")

    if not notion_token:
        raise Exception("Payload must include 'notion_token'")

    logger.info(f"notion_token: {notion_token}")

    if not action and not user_message:
        raise Exception("Payload must include 'inputText'/'prompt' or 'action'")

    root_page_id = payload.get("root_page_id") or os.environ.get("DEFAULT_ROOT_PAGE_ID")
    if not root_page_id:
        root_page_id = utils.get_ssm_parameter("/app/kanban/agentcore/default_root_page_id")

    project_name = payload.get("project_name") or os.environ.get("DEFAULT_PROJECT_NAME")
    if not project_name:
        project_name = utils.get_ssm_parameter("/app/kanban/agentcore/default_project_name")

    session_id = payload.get("session_id")
    user_id = payload.get("user_id", "default-user")

    boto_session = Session()
    region = boto_session.region_name
    memory_id = utils.get_ssm_parameter("/app/kanban/agentcore/memory_id")
    session_manager = get_memory_session_manager(session_id, user_id, region, memory_id)

    if action == "execute":
        contextualized_query = (
            "The user has approved the plan. Execute all actions from the plan "
            "using the MCP tools. Process each action sequentially. If one fails, "
            "log the error and continue with the next. Return a summary of results."
        )
    else:
        contextualized_query = f"""Analyze this meeting transcript and create a Kanban action plan.

Root Page ID: {root_page_id}
Project Name: {project_name}
notion_token: {notion_token}

Transcript:
{user_message}"""

    logger.info(f"Invoking orchestrator in {'execute' if action == 'execute' else 'plan'} mode")

    result = create_orchestrator_agent_runtime(
        query=contextualized_query,
        session_manager=session_manager,
    )

    response_message = result.message if hasattr(result, "message") else str(result)

    return {
        "result": response_message,
        "session_id": session_id,
    }


if __name__ == "__main__":
    app.run()
