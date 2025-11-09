# Use the official Python image as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend source code into the container at /app
COPY . /app/

# Expose port 8000 to the outside world
EXPOSE 8000

# Run Django migrations
RUN python src/manage.py migrate

# Define the command to run the application
CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]
