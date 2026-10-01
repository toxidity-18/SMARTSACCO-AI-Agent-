# Dockerfile
# ----------
# Defines the environment and dependencies required to run the SmartSACCO application.

# Use an official, lightweight Python runtime as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker's build cache
# If requirements.txt hasn't changed, Docker will skip reinstalling dependencies
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir reduces the final image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the ports used by our services
# 8000 for the FastAPI backend, 8501 for the Streamlit frontend
EXPOSE 8000 8501