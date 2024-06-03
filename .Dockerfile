FROM tiangolo/uvicorn-gunicorn:python3.10-slim

# Copy the current directory contents into the container at /app
COPY . /app

# Set the working directory to /app
WORKDIR /app

# Install requirements.txt 
RUN pip install --no-cache-dir --upgrade -r /requirements.txt

# Expose the port the app runs on
EXPOSE 7860

# Start the FastAPI app on port 7860
CMD ["fastapi", "run", "app.py", "--host", "0.0.0.0", "--port", "7860"]
