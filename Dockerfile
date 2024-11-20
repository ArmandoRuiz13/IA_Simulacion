# Use the official Python image from the Docker Hub
FROM  python:3.12.7-alpine3.20

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install necessary build tools
RUN apk add --no-cache gcc g++ musl-dev

# Install any dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Expose port 5000 for the application
EXPOSE 5000

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app.py"]
