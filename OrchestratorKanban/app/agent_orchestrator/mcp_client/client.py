import os
import logging
from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp.mcp_client import MCPClient

logger = logging.getLogger(__name__)

# ExaAI provides information about code through web searches, crawling and code context searches through their platform. Requires no authentication

def get_streamable_http_mcp_client(token: str, gateway_url: str) -> MCPClient:
    """Returns an MCP Client compatible with Strands"""
    # to use an MCP server that supports bearer authentication, add headers={"Authorization": f"Bearer {access_token}"}
    return MCPClient(lambda: streamablehttp_client(
        gateway_url,
        headers={"Authorization": f"Bearer {token}"}
    ))

if __name__ == "__main__":
    from utils import get_cognito_token, get_ssm_parameter
    
    token = get_cognito_token()
    gateway_url = get_ssm_parameter("/app/kanban/agentcore/gatewayURL")
    print(gateway_url)
    print(token)
    def create_streamable_http_transport():
        return streamablehttp_client(
            gateway_url,
            headers={"Authorization": f"Bearer {token}"}
        )

    mcp_client = MCPClient(create_streamable_http_transport)


    with mcp_client:
        tools = mcp_client.list_tools_sync()
        print(f"Tools available from MCP: {len(tools)}")
