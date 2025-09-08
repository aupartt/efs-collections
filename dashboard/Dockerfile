FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_EXTRA_INDEX_URL=https://www.piwheels.org/simple

# Add environment variables for ARM optimization
ENV OPENBLAS_CORETYPE=ARMV8
ENV OPENBLAS_NUM_THREADS=1
ENV OMP_NUM_THREADS=1

# Copy the ROOT pyproject.toml and uv.lock (workspace configuration)
COPY pyproject.toml uv.lock ./
COPY ./dashboard/pyproject.toml ./dashboard/

# Sync dependencies using the workspace configuration
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package dashboard --no-install-project --no-dev

# Copy the dashboard package to the expected location
COPY ./dashboard ./dashboard


ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

CMD ["streamlit", "run", "dashboard/main.py"]