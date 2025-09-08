FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install build dependencies (keep these if needed for other packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml uv.lock ./

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
# Set piwheels as an extra index for package resolution
ENV UV_EXTRA_INDEX_URL=https://www.piwheels.org/simple

# Add environment variables for ARM optimization
ENV OPENBLAS_CORETYPE=ARMV8
ENV OPENBLAS_NUM_THREADS=1
ENV OMP_NUM_THREADS=1

# Sync dependencies using piwheels
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY ./app ./app
COPY ./main.py ./
COPY ./.streamlit/ ./.streamlit/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/collector"
ENV PYTHONUNBUFFERED=1

CMD ["streamlit", "run", "main.py"]