# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app
COPY .env /app/.env
# Copy requirements.txt first for better caching of dependencies
COPY requirements.txt requirements.txt

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application to the container
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Ensure Flask listens on all available interfaces, not just localhost
ENV FLASK_RUN_HOST=0.0.0.0

# Command to run the application
CMD ["python", "app.py"]


