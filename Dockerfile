# read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# you will also find guides on how best to write your Dockerfile

# Use the official Python 3.10 slim image as the base image
FROM tiangolo/uvicorn-gunicorn:python3.10-slim

# Install necessary tools
USER root
RUN apt-get update && apt-get install -y wget tar

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user

# Create necessary directories and set permissions
RUN mkdir -p /home/user/.cache && chown -R user:user /home/user/.cache
RUN mkdir -p /home/user/.local && chown -R user:user /home/user/.local

# Switch to the "user" user
USER user

# Set home to the user's home directory
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR /home/user/app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy the current directory contents into the container at /home/user/app
COPY --chown=user . .

# List the contents of the working directory to debug
RUN ls -la

# Install the dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Expose the port the app runs on
EXPOSE 7860

# Start the FastAPI app on port 7860
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "7860"]
