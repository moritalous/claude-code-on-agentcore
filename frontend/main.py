import base64
import json
import uuid

import boto3
import httpx
import streamlit as st

st.title("Chat with Claude Agent SDK")

with st.container(border=True):
    LOCALMODE = st.checkbox("Localmode", value=False)

    if LOCALMODE:
        local_endpoint = st.text_input(
            "Endpoint", value="http://localhost:8080/invocations", disabled=True
        )
    else:
        agent_runtime_arn = st.text_input("Agent runtime ARN")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])


if input := st.chat_input(accept_file=True):
    prompt = input["text"]
    files = input["files"]

    with st.chat_message("user"):
        st.write(prompt)

    request_files = [{"filename": f.name, "bytes": f.getvalue()} for f in files]

    request_body = {
        "prompt": prompt,
        "files": request_files,
    }

    def process_streaming_response(stream_iter):
        status = st.status("processing...", expanded=True)
        for chunk in stream_iter:
            if chunk:
                event = json.loads(chunk[6:])
                if "message" in event and event["message"]:
                    message = json.loads(event["message"])
                    if message["type"] == "ResultMessage":
                        status.update(state="complete", expanded=False)
                        with st.chat_message("assistant"):
                            st.write(message["result"])
                        st.session_state["messages"].append(
                            {"role": "user", "content": prompt}
                        )
                        st.session_state["messages"].append(
                            {"role": "assistant", "content": message["result"]}
                        )
                    else:
                        with status.expander(message["type"], expanded=False):
                            st.json(message)
                if "output" in event and event["output"]:
                    st.session_state["output"] = event["output"]

    if LOCALMODE:
        with httpx.stream(
            method="POST",
            url=local_endpoint,
            headers={
                "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": st.session_state.session_id
            },
            timeout=httpx.Timeout(timeout=120.0),
            json=request_body,
        ) as stream:
            process_streaming_response(stream.iter_lines())
    else:
        client = boto3.client("bedrock-agentcore")
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_runtime_arn,
            runtimeSessionId=st.session_state.session_id,
            payload=json.dumps(request_body).encode(),
        )

        process_streaming_response(response["response"].iter_lines(chunk_size=10))


if "output" in st.session_state:
    output = st.session_state["output"]
    files = output["files"]

    for file in files:
        st.download_button(
            file["filename"],
            data=base64.b64decode(file["bytes"]),
            file_name=file["filename"],
        )
