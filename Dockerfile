# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Install dependencies
# Install dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc

# Set the working directory in the container
WORKDIR /app

# Copy the Flask application code into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the Flask app will run on
EXPOSE 5000

# Set the environment variable for Flask
ENV FLASK_APP=app.app:my_app

# Command to run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
