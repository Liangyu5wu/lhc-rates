# syntax=docker/dockerfile:1
# Development container. The build context is docker/; the repository is
# mounted at /work at run time and is never copied into the image.

# Stage 1: Python and uv. `make lock` runs uv here, so the first lock needs no lock.
FROM python:3.14-slim AS tools
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /usr/local/bin/
ENV UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Stage 2: Node. `make lock` runs npm here, to write package-lock.json.
FROM node:22-slim AS node-tools
WORKDIR /deps

# Stage 3: the frontend libraries, exactly as package-lock.json records them.
FROM node-tools AS frontend
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund \
    || { echo "docker/package-lock.json does not match docker/package.json: run 'make lock', then commit both files." >&2; exit 1; }

# Stage 4: the image you work in.
FROM tools AS final
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH=/opt/venv/bin:$PATH \
    PYTHONPATH=/work/src \
    VENDOR_DIR=/opt/vendor
WORKDIR /deps
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project \
    || { echo "docker/uv.lock does not match docker/pyproject.toml: run 'make lock', then commit both files." >&2; exit 1; }
# Outside /work, which the repository mount would hide.
COPY --from=frontend /deps/node_modules/plotly.js-dist-min/plotly.min.js /opt/vendor/plotly.min.js
WORKDIR /work
# 0.0.0.0 inside the container only; compose publishes the port on 127.0.0.1.
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
