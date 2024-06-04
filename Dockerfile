# Use the official Python 3.10 slim image as the base image
FROM tiangolo/uvicorn-gunicorn:python3.10-slim

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user

# Switch to the "user" user
USER user

# Set home to the user's home directory
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR $HOME/app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy the current directory contents into the container at $HOME/app
COPY --chown=user . $HOME/app

# Set the working directory
WORKDIR /app

# List the contents of the working directory to debug
RUN ls -la

# Install the dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Expose the port the app runs on
EXPOSE 7860

# Start the FastAPI app on port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
