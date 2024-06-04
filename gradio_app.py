import multion
import gradio as gr
import requests
import time
import os 

from rich import print
from multion.client import MultiOn
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables from .env file
load_dotenv()

multion = MultiOn(api_key=os.environ.get("MULTION_API_KEY"))
print("MultiOn API key loaded")

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
            print(f"Attempt {retries + 1} failed: {e}")
            retries += 1
            time.sleep(delay)
    raise Exception(f"Failed after {max_retries} attempts")

def echo(message, history):
    file_paths = message.get("files", [])
    text = message.get("text", "")
    
    print(f"Received message: {text}")
    print(f"Received files: {file_paths}")
    
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
        response = post_with_retry("https://muhtasham-agent.hf.space/process-input/", data=data, files=files)

        # Handle the response from the FastAPI endpoint
        if response.status_code == 200:
            response_json = response.json()
            print(response_json)
            if "response" in response_json:
                if response_json["response"] == "This command is for local browsing":
                    # Make the secondary call based on the received command
                    command = response_json["command"]
                    try:
                        response = multion.sessions.create(
                        url=command["url"],
                        local=True
                        )
                        session_id = response.session_id
                        print(response.message)

                        while response.status == 'CONTINUE':
                            response = multion.sessions.step(
                                session_id = session_id,
                                cmd=command["cmd"],
                                url=command["url"],
                            )
                            user_facing_response = response.message
                            print(user_facing_response)
                            

                        response = multion.sessions.close(session_id=session_id)
                        print("close_session_response: ", response)

                        return user_facing_response
                    
                    except Exception as e:
                        print(f"Error in secondary call: {e}")
                        return {"error": str(e)}
                else:
                    return response_json["response"]
            else:
                return {"error": "Invalid response format from FastAPI endpoint"}
        else:
            return {"error": "Failed to process input"}
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

demo = gr.ChatInterface(
    fn=echo,
    title="MultiOn Bot",
    multimodal=True
)

demo.launch()
