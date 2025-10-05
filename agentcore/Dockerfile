FROM node:lts-bookworm-slim

# Install `cURL` and `Wget`
RUN apt-get update && apt-get install -y curl wget && rm -rf /var/lib/apt/lists/*

# Install `gh`
RUN mkdir -p -m 755 /etc/apt/keyrings && \
    wget -nv -O /tmp/githubcli-archive-keyring.gpg https://cli.github.com/packages/githubcli-archive-keyring.gpg && \
    cat /tmp/githubcli-archive-keyring.gpg | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null && \
    chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg && \
    mkdir -p -m 755 /etc/apt/sources.list.d && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && \
    apt-get install -y gh && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash claude

USER claude
WORKDIR /workspace

ENV UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DOCKER_CONTAINER=1 \
    CLAUDE_CODE_USE_BEDROCK=1 \
    AWS_REGION=us-west-2 \
    PATH="/home/claude/.npm-global/bin:/home/claude/.local/bin:$PATH"

RUN mkdir ~/.npm-global && \
    npm config set prefix '~/.npm-global' && \
    npm install -g @anthropic-ai/claude-code

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

COPY pyproject.toml .
RUN uv sync

COPY main.py .mcp.json .

EXPOSE 8080

CMD ["uv", "run", "main.py"]
