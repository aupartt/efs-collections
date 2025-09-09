FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

ENV UV_EXTRA_INDEX_URL=https://www.piwheels.org/simple

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package dashboard --no-install-project --no-dev

COPY ./dashboard ./dashboard

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

CMD ["streamlit", "run", "dashboard/main.py"]
