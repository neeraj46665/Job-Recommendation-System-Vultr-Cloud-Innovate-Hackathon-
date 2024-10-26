# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt first for better caching of dependencies
COPY requirements.txt requirements.txt

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application to the container
COPY . .

# Create the .env file inside the container with the API key passed from GitHub Actions
ARG COHERE_API_KEY
ARG VULTR_CLOUD_INFERENCE_API_KEY 
# Create .env file with the API keys
RUN echo "COHERE_API_KEY=${COHERE_API_KEY}" >> /app/.env && \
    echo "VULTR_CLOUD_INFERENCE_API_KEY=\"${VULTR_CLOUD_INFERENCE_API_KEY}\"" >> /app/.env

# Expose the port the app runs on
EXPOSE 5000

# Ensure Flask listens on all available interfaces, not just localhost
ENV FLASK_RUN_HOST=0.0.0.0

# Command to run the application
CMD ["python", "app.py"]
