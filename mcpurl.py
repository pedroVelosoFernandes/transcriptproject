def transform_url(arn):
    encoded_arn = arn.replace(':', '%3A').replace('/', '%2F')
    mcp_url = f"https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
    return mcp_url

if __name__ == "__main__":
    arn = "arn:aws:bedrock-agentcore:us-east-1:631510543425:runtime/McpKanban_mcp_notion-fqxbZC8Hzs"
    print(transform_url(arn))

#https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3Aaws%3Abedrock-agentcore%3Aus-east-1%3A631510543425%3Aruntime%2FMcpKanban_mcp_notion-fqxbZC8Hzs/invocations?qualifier=DEFAULT