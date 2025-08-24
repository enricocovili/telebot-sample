# Use the official uv image for faster builds
FROM ghcr.io/astral-sh/uv:python3.13-alpine

# install ssh
RUN apk add --no-cache openssh-client

# Set working directory
WORKDIR /app

# Copy uv configuration files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy the rest of the application code
COPY . .

# Set the Python path to use uv's virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Run the application
CMD ["uv", "run", "GinoProsciutto/main.py"]
