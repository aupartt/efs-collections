# Start with a suitable base image
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set the working directory for the entire project
WORKDIR /app

# Copy the entire monorepo structure
# This includes all pyproject.toml and uv.lock files
COPY pyproject.toml uv.lock ./

# Set environment variables for UV
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Use a single UV command to sync all workspace members and their dependencies
# Use --workspace to indicate UV should treat this as a monorepo
# --no-dev to avoid installing dev dependencies in the final image
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY ./app ./app
COPY ./main.py ./
COPY ./.streamlit/ ./.streamlit/

# Set the PATH and PYTHONPATH for the application
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/collector"
ENV PYTHONUNBUFFERED=1

# Use the installed cli.py as the entrypoint
# The entrypoint should now be to the main application's CLI module, which is inside the 'collector' folder
CMD ["streamlit", "run", "main.py"]