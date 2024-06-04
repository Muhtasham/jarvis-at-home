# read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# you will also find guides on how best to write your Dockerfile

FROM tiangolo/uvicorn-gunicorn:python3.10-slim

# Set the working directory
WORKDIR /app

# Copy the contents of the current directory to /app in the container
COPY . .

# List the contents of the working directory to debug
RUN ls -la

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install requirements.txt 
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Expose the port the app runs on
EXPOSE 7860

# Start the FastAPI app on port 7860
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "7860"]
