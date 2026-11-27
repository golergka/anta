FROM node:24.15.0-bookworm-slim AS node
FROM python:3.12-slim-bookworm AS worker
RUN useradd --uid 10001 --create-home agent && install -d -m 1777 /private/tmp
ENV PYTHONDONTWRITEBYTECODE=1
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/npm
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && apt-get update && apt-get install -y --no-install-recommends git ripgrep \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g --no-audit --no-fund @openai/codex@0.144.1
COPY worker.py /opt/worker.py
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
ENV HOME=/home/agent CODEX_HOME=/home/agent/.codex
USER agent
ENTRYPOINT ["python", "/opt/worker.py"]
