import json
from dataclasses import asdict

from bedrock_agentcore import BedrockAgentCoreApp
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from claude_agent_sdk.types import SystemPromptPreset

app = BedrockAgentCoreApp()

with open(".mcp.json", mode="rt") as f:
    mcp_json = json.load(f)

options = ClaudeAgentOptions(
    system_prompt=SystemPromptPreset(type="preset", preset="claude_code"),
    permission_mode="bypassPermissions",
    mcp_servers=mcp_json["mcpServers"],
    disallowed_tools=["WebFetch"],
    user="claude",
    env={"HOME": "/home/claude"},
)


@app.entrypoint
async def handler(event):
    prompt = event.get("prompt")

    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt=prompt)

        async for message in client.receive_response():
            yield {
                "type": type(message).__name__,
                "message": asdict(message),
            }


if __name__ == "__main__":
    app.run()
