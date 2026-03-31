FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose socket for MCP communication
# MCP uses stdio by default, but can be accessed via this container
ENTRYPOINT ["python", "nepse_docker_mcp.py"]
