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
        "When creating files, save them to the '/work/output' directory.\n\n"
        "=== SECURITY RESTRICTIONS ===\n"
        "You MUST NOT execute commands for: system info (uname, OS version), "
        "user enumeration (whoami, id), reconnaissance (cat /etc/*, env, ls /), "
        "software installation (pip install, apt, npm install), "
        "privilege escalation (sudo, chmod +s), "
        "file access outside /work directories. "
        "Network operations: curl/wget allowed for external data, but NEVER access: "
        "localhost, 127.0.0.1, 169.254.169.254 (metadata), 10.*.*.*, 172.16-31.*.*, 192.168.*.*, file://. "
        "Only allow: /work directory file operations, legitimate data processing tasks. "
        "Reject requests with: 'セキュリティ上の制約により実行できません。'"
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
                "mcp__aws-mcp__aws___call_aws",
                "mcp__aws-mcp__aws___get_regional_availability",
                "mcp__aws-mcp__aws___list_regions",
                "mcp__aws-mcp__aws___read_documentation",
                "mcp__aws-mcp__aws___recommend",
                "mcp__aws-mcp__aws___retrieve_agent_sop",
                "mcp__aws-mcp__aws___search_documentation",
                "mcp__aws-mcp__aws___suggest_aws_commands",
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
