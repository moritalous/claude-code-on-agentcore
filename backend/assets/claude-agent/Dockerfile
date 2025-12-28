FROM --platform=linux/arm64 ghcr.io/astral-sh/uv:python3.13-trixie

RUN apt-get update && apt-get install -y \
    pandoc \
    libreoffice \
    poppler-utils \
    curl \
    nodejs \
    npm \
    fonts-noto-cjk \
    fonts-ipafont \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 appuser && useradd -u 1000 -g 1000 -m appuser

RUN mkdir -p /work && chown -R 1000:1000 /work

USER appuser

RUN mkdir -p /work/input /work/output

RUN mkdir ~/.npm-global
RUN npm config set prefix '~/.npm-global'

ENV PATH=~/.npm-global/bin:$PATH\
    NODE_PATH=/home/appuser/.npm-global/lib/node_modules

RUN npm install -g \
    @anthropic-ai/claude-code \
    pptxgenjs \
    playwright \
    react-icons \
    react \
    react-dom \
    sharp \
    docx

ENV CLAUDE_CODE_USE_BEDROCK=1\
    ANTHROPIC_MODEL=haiku \
    ANTHROPIC_DEFAULT_SONNET_MODEL=global.anthropic.claude-sonnet-4-5-20250929-v1:0\
    ANTHROPIC_DEFAULT_HAIKU_MODEL=global.anthropic.claude-haiku-4-5-20251001-v1:0 \
    CLAUDE_CODE_SUBAGENT_MODEL=haiku \
    MAX_THINKING_TOKENS=1024 \
    MCP_TIMEOUT=600000 \
    MCP_TOOL_TIMEOUT=600000

WORKDIR /app
COPY --chown=1000:1000 app/pyproject.toml app/uv.lock ./
RUN uv sync --frozen

COPY --chown=1000:1000 app/.claude ./.claude
COPY --chown=1000:1000 app/.mcp.json app/main.py ./

CMD ["uv", "run", "opentelemetry-instrument", "python", "main.py"]
