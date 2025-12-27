import base64
import json
from dataclasses import asdict
from pathlib import Path

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from claude_agent_sdk import ClaudeAgentOptions, query

app = BedrockAgentCoreApp()

session_id = None


@app.entrypoint
async def invocations(payload, context):
    global session_id

    prompt = payload.get("prompt", "")
    input_files = payload.get("files", [])
    # session_id = payload.get("sessionId", "")

    # Save input files (overwrite if same name exists)
    input_dir = Path("/work/input")
    for file in input_files:
        filepath = input_dir / file["filename"]
        filepath.write_bytes(base64.b64decode(file["bytes"]))

    # Create system prompt
    file_list = list(input_dir.glob("*"))
    files_info = ", ".join(f.name for f in file_list) if file_list else "empty"
    system_prompt = (
        f"Input files are available in the '/work/input' directory ({files_info}). "
        "When creating files, save them to the '/work/output' directory."
    )

    async for message in query(
        # Sample prompt:
        # Create a simple Word document with a title 'Test Document' and one paragraph saying 'This is a test.' using docx-js",
        prompt=prompt,
        options=ClaudeAgentOptions(
            allowed_tools=[
                "Read",
                "Edit",
                "Bash",
                "Skill",
                "mcp__aws-knowledge-mcp-server__aws___get_regional_availability",
                "mcp__aws-knowledge-mcp-server__aws___list_regions",
                "mcp__aws-knowledge-mcp-server__aws___read_documentation",
                "mcp__aws-knowledge-mcp-server__aws___recommend",
                "mcp__aws-knowledge-mcp-server__aws___search_documentation",
            ],
            disallowed_tools=["WebFetch"],
            permission_mode="acceptEdits",
            setting_sources=["project"],
            system_prompt=system_prompt,
            resume=session_id,  # Support multi-turn conversations
        ),
    ):
        data = {"type": message.__class__.__name__, **asdict(message)}
        yield {"message": json.dumps(data, ensure_ascii=False)}

        if hasattr(message, "session_id"):
            session_id = message.session_id

    output_files = []
    output_dir = Path("/work/output")

    for filepath in output_dir.glob("*"):
        if filepath.is_file():
            output_files.append(
                {
                    "filename": filepath.name,
                    "bytes": base64.b64encode(filepath.read_bytes()).decode(),
                }
            )

    if output_files:
        yield {"output": {"files": output_files}}


if __name__ == "__main__":
    app.run()
