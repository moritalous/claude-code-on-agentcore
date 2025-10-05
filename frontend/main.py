import json
import uuid

import boto3
import streamlit as st

client = boto3.client("bedrock-agentcore", region_name="us-west-2")


def write_message(message):
    match message["type"]:
        case "SystemMessage":
            with st.chat_message("assistant"):
                st.json(message, expanded=2)
        case "AssistantMessage":
            with st.chat_message("assistant"):
                st.json(message, expanded=2)
        case "UserMessage":
            with st.chat_message("user"):
                st.json(message, expanded=2)
        case "ResultMessage":
            with st.chat_message("user"):
                st.write(message["message"]["result"])
                st.json(message, expanded=False)


agent_runtime_arn = st.text_input("Agent Runtime ARN")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if prompt := st.chat_input():
    with st.chat_message("user"):
        st.write(prompt)

    response = client.invoke_agent_runtime(
        agentRuntimeArn=agent_runtime_arn,
        runtimeSessionId=st.session_state.session_id,
        payload=json.dumps({"prompt": prompt}, ensure_ascii=False),
        qualifier="DEFAULT",
    )

    for line in response["response"].iter_lines():
        if line:
            body = line.decode("utf-8")
            body = line[6:]  # 先頭の`data: `を除去
            body = json.loads(body)

            write_message(body)
