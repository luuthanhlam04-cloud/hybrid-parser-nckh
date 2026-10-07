# Use Python 3.11 slim image for minimal footprint
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv for lightning-fast package management
# Copy binary and install it system-wide for reproducible builds
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Enable uv's pip compatibility mode for seamless integration
ENV UV_INSTALL_MODE=copy

# Configure sentence-transformers cache directory for model persistence
# Models are downloaded once and cached to avoid repeated downloads (~80MB for all-MiniLM-L6-v2)
ENV TRANSFORMERS_CACHE=/app/.cache/models
ENV HF_HOME=/app/.cache/models

# Support for environment variables (API keys will be passed at runtime)
# Example: docker run -e GEMINI_API_KEY=your_key rag-baseline

# Create cache directory with proper permissions
RUN mkdir -p /app/.cache/models

# Copy project dependencies
COPY pyproject.toml ./

# Install dependencies using uv (faster than pip, deterministic builds)
# --system installs to system Python, --no-dev skips dev dependencies for production
RUN uv pip install --system --no-dev .

# Copy application code
COPY . .

# Default command - runs the CLI interface
# Can be overridden for running tests: docker run rag-baseline python -m pytest tests/
CMD ["python", "src/main.py"]
