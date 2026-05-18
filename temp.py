def transform_url(arn):
    encoded_arn = arn.replace(':', '%3A').replace('/', '%2F')
    mcp_url = f"https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
    return mcp_url

if __name__ == "__main__":
    arn = "arn:aws:bedrock-agentcore:us-east-1:631510543425:runtime/MeetingToKanban_notion_mcp-tVkG1I4KZ3"
    print(transform_url(arn))