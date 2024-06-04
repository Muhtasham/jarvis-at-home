import multion
import gradio as gr
import requests
import os 

from rich import print
from multion.client import MultiOn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

multion = MultiOn(api_key=os.environ.get("MULTION_API_KEY"))
print("MultiOn API key loaded")


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
        response = requests.post("https://muhtasham-agent.hf.space/process-input/", data=data, files=files)

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
    examples=[{"text": "hello"}, {"text": "hola"}, {"text": "merhaba"}],
    title="MultiOn Bot",
    multimodal=True,
)
demo.launch()
