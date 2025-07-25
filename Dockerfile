# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /api

# Copy the project files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your application runs on
EXPOSE 8501

# Set the entry point for the container
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8501"]
