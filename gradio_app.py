import multion
import gradio as gr
import requests
import time
import os 

from loguru import logger
from multion.client import MultiOn
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables from .env file
load_dotenv()

multion = MultiOn(api_key=os.environ.get("MULTION_API_KEY"))
logger.info("MultiOn API key loaded")

def post_with_retry(url: str, data: Dict[str, Any], files: Dict[str, Any], max_retries: int = 3, delay: int = 2) -> requests.Response:
    """
    Send a POST request to the specified URL with retries on failure.

    Parameters:
    - url (str): The URL to send the POST request to.
    - data (dict): The data to include in the POST request.
    - files (dict): The files to include in the POST request.
    - max_retries (int, optional): The maximum number of retries. Default is 3.
    - delay (int, optional): The delay in seconds between retries. Default is 2.

    Returns:
    - response (requests.Response): The response object from the successful POST request.

    Raises:
    - Exception: If all retries fail, an exception is raised indicating the failure.
    """
    retries = 0
    while retries < max_retries:
        try:
            response = requests.post(url, data=data, files=files)
            response.raise_for_status()  # Raise an error for bad status codes
            return response
        except requests.exceptions.RequestException as e:
            logger.info(f"Attempt {retries + 1} failed: {e}")
            retries += 1
            time.sleep(delay)
    raise Exception(f"Failed after {max_retries} attempts")

def echo(message, history):
    file_paths = message.get("files", [])
    text = message.get("text", "")
    
    logger.info(f"Received message: {text}")
    logger.info(f"Received files: {file_paths}")
    
    # Prepare the data for the POST request
    data = {'text': text, 'online': 'true'}  # Ensure 'online' is sent as a string
    files = None
    
    if file_paths:
        # Determine the MIME type based on file extension
        mime_type = 'application/octet-stream'  # Default to a generic binary type
        ext = os.path.splitext(file_paths[0])[1].lower()
        if ext == '.png':
            mime_type = 'image/png'
        elif ext == '.jpeg' or ext == '.jpg':
            mime_type = 'image/jpeg'
        
        files = {
            'file': (
                os.path.basename(file_paths[0]), 
                open(file_paths[0], 'rb'),
                mime_type
            )
        }

    try:
        # Send the POST request to the FastAPI endpoint
        fast_api_response = post_with_retry("https://muhtasham-agent.hf.space/process-input/", data=data, files=files)

        # Handle the response from the FastAPI endpoint
        if fast_api_response.status_code == 200:
            response_json = fast_api_response.json()
            logger.info(response_json)
            if "response" in response_json:
                if response_json["response"] == "This command is for local browsing":
                    # Make the secondary call based on the received command
                    command = response_json["command"]
                    try:
                        logger.info(f"Calling MultiOn API locally in Step mode: {command}")
                        response = multion.sessions.create(
                        url=command["url"],
                        local=True
                        )
                        session_id = response.session_id
                        logger.info(f"Session created: {session_id}")

                        logger.info(f"Response message so far: {response.message}")
                        logger.info(f"Status so far: {response.status}")

                        logger.info("Stepping through the session")
                        
                        while response.status == 'CONTINUE':
                            response = multion.sessions.step(
                                session_id = session_id,
                                cmd=command["cmd"],
                                url=command["url"],
                            )
                        
                        logger.info(f"Status after exiting the loop: {response.status}")
                        user_facing_response = response.message
                        logger.info(f"User facing response: {user_facing_response}")
                        logger.info("Closing the session")
                        response = multion.sessions.close(session_id=session_id)
                        logger.info("Close_session_response: ", response)

                        return user_facing_response
                    
                    except Exception as e:
                        logger.info(f"Error in session call: {e}")
                        try:
                            logger.info(f"Calling MultiOn API locally in Browse mode: {command}")
                            response = multion.browse(
                            cmd=command["cmd"],
                            url=command["url"],
                            local=True
                            )
                            return response
                        except Exception as e:
                            logger.info(f"Error in browse call: {e}")
                            return {"error": str(e)}
                else:
                    return response_json["response"]
            else:
                return {"error": "Invalid response format from FastAPI endpoint"}
        else:
            return {"error": "Failed to process input"}
    except Exception as e:
        logger.info(f"Error: {e}")
        return {"error": str(e)}

demo = gr.ChatInterface(
    fn=echo,
    title="MultiOn Bot",
    multimodal=True
)

demo.launch()
