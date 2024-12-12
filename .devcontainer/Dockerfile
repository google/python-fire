FROM python:3.10-slim

# Set the working directory
WORKDIR /workspace

# Install Python packages
COPY requirements.txt /workspace/
RUN pip install --no-cache-dir -r requirements.txt
