# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create directories for uploads
RUN mkdir -p /app/uploads/docs /app/uploads/images /app/static/fonts

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# Run app.py when the container launches
CMD ["python", "app.py"]