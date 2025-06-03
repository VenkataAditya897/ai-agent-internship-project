# Use the official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Set working directory inside the container
WORKDIR /app

# Copy dependency file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory
COPY . /app/

# Expose the port Flask runs on (default 5000)
EXPOSE 5000

# Run the Flask app
CMD ["python", "run.py"]
