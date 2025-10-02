# Use an official Python runtime as a parent image
FROM python:3.11.6-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Set the default command to run when the container starts
# Use waitress to serve the Flask app
CMD ["waitress-serve", "--host=0.0.0.0", "--port=8080", "app:app"]



# docker build -t autocollect-web .
# docker run --rm -p 8080:8080 -v "%cd%/shared_links:/app/shared_links" autocollect-web
# docker run --rm -p 8080:8080 -v "/d/Projects/AutoCollectItem/shared_links:/app/shared_links" autocollect-web
