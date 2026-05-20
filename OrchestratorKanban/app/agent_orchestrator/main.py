from strands import Agent, tool
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from model.load import load_model
from mcp_client.client import get_streamable_http_mcp_client
from memory.session import get_memory_session_manager
import utils
from boto3 import Session

# ============================================================================
# AGENTCORE APP INITIALIZATION
# ============================================================================

app = BedrockAgentCoreApp()
model = load_model()

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logger = app.logger

# ============================================================================
# CONFIGURATION HELPERS
# ============================================================================

token = utils.get_cognito_token()

gateway_url = utils.get_ssm_parameter("/app/kanban/agentcore/gatewayURL")
mcp_client = get_streamable_http_mcp_client(token, gateway_url)

# ============================================================================
# ORCHESTRATOR AGENT CREATION
# ============================================================================

def create_orchestrator_agent_runtime(
    query,
    session_manager
):
    """Create the orchestrator agent for """

    orchestrator_system_prompt = """
"""

    contextualized_query = f"""User Query: {query}"""

    base_tools = [

    ]
    logger.info("Entering mcp_client context...")
    with mcp_client:
        try:
            logger.info(f"Listing MCP tools from {gateway_url}...")
            mcp_tools = mcp_client.list_tools_sync()
            logger.info("Done listing MCP tools.")
            all_tools = base_tools + mcp_tools
            
            logger.info(f"Added {len(mcp_tools)} MCP tools from Gateway. Total tools: {len(all_tools)}")
            
            orchestrator = Agent(
                model=model,
                system_prompt=orchestrator_system_prompt,
                tools=all_tools,
                session_manager=session_manager
            )
            logger.info("Orchestrator agent created successfully with memory and MCP tools")
            
            response = orchestrator(contextualized_query)
            logger.info("Orchestrator successfully processed query")
            
            return response
            
        except Exception as e:
            logger.error(f"Error with MCP tools: {str(e)}")
            logger.info("Falling back to base tools only")
            
            orchestrator = Agent(
                model=model,
                system_prompt=orchestrator_system_prompt,
                tools=base_tools,
                session_manager=session_manager
            )
            logger.info("Orchestrator agent created successfully with memory (fallback mode)")
            
            response = orchestrator(contextualized_query)
            logger.info("Orchestrator successfully processed query (fallback)")
            
            return response
    

# ============================================================================
# AGENTCORE RUNTIME ENTRYPOINT
# ============================================================================
@app.entrypoint
def invoke(payload, context):
    """
    """

    user_message = payload.get("inputText") or payload.get("prompt")
    if not user_message:
        raise Exception("Payload must include 'inputText' or 'prompt' parameter")
    
    # user_id = payload.get("user_id")
    # if not user_id:
    #     raise Exception("Payload must include 'user_id' parameter")
    
    # session_id = context.session_id
    # if not session_id:
    #     raise Exception("Context must include 'session_id'")
    session_id = getattr(context, 'session_id', 'default-session')
    user_id = getattr(context, 'user_id', 'default-user')
    
    boto_session = Session()
    region = boto_session.region_name

    # Create memory session manager for this user/session
    memory_id = utils.get_ssm_parameter("/app/kanban/agentcore/memory_id")
    session_manager = get_memory_session_manager(session_id, user_id, region, memory_id)

    try:
        logger.info("Creating orchestrator agent")
        result = create_orchestrator_agent_runtime(
            query=user_message,
            session_manager=session_manager,
        )
        
        response_message = result.message if hasattr(result, 'message') else str(result)
        
        logger.info("Orchestrator successfully processed request")
        
        return {
            "result": response_message,
            "session_id": session_id,
        }
        
    except Exception as e:
        logger.error(f"Error in orchestrator processing: {str(e)}")
        raise



if __name__ == "__main__":
    app.run()


# ============================================================================
 