FROM python:3.12-slim-bookworm AS base
RUN useradd --uid 10001 --create-home agent && install -d -o agent -g agent /relay
ENV PYTHONDONTWRITEBYTECODE=1

FROM base AS relay
COPY relay.py smoke_responses.py /opt/
USER agent
ENTRYPOINT ["python", "/opt/relay.py"]

FROM node:24.15.0-bookworm-slim AS node
FROM base AS worker
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/npm
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && apt-get update && apt-get install -y --no-install-recommends git ripgrep \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g --no-audit --no-fund @openai/codex@0.144.1 \
    && pip install --no-cache-dir https://github.com/golergka/coloph-agent-runtime/releases/download/v0.3.0/coloph_agent_runtime-0.3.0-py3-none-any.whl
COPY worker.py /opt/worker.py
COPY --chown=agent:agent codex.toml /home/agent/.codex/config.toml
COPY anta-source /opt/anta-source
WORKDIR /workspace
COPY starter/package*.json ./
RUN npm ci --no-audit --no-fund
COPY anta.tgz /opt/anta.tgz
RUN npm install --no-audit --no-fund /opt/anta.tgz
COPY starter/index.html starter/tsconfig.json starter/vite.config.mjs ./
COPY starter/src ./src
RUN chown agent:agent /workspace && chown -R agent:agent /workspace/src \
    && chown agent:agent /workspace/index.html /workspace/tsconfig.json /workspace/vite.config.mjs /workspace/package*.json
RUN chown agent:agent /home/agent/.codex
ENV HOME=/home/agent CODEX_HOME=/home/agent/.codex
USER agent
ENTRYPOINT ["python", "/opt/worker.py"]
