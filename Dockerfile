# Dockerfile
# ----------
# Production-ready container definition for the SmartSACCO application.

# Use an official, lightweight Python runtime as the base image
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files 
# and to ensure output is printed directly to the terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker's build cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Make the startup script executable
RUN chmod +x start.sh

# Expose the ports used by our services (8000 for API, 8501 for Streamlit)
EXPOSE 8000 8501

# Define the default command to run when the container starts
CMD ["./start.sh"]