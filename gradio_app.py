from rich import print
import gradio as gr
import requests

def echo(message, history):
    file_paths = message.get("files", [])
    text = message.get("text", "")
    
    print(f"Received message: {text}")
    print(f"Received files: {file_paths}")
    
    # Prepare the data for the POST request
    data = {'text': text}
    files = {'file': (file_paths[0], open(file_paths[0], 'rb'))} if file_paths else None

    try:
        # Send the POST request to the FastAPI endpoint
        response = requests.post("https://muhtasham-agent.hf.space/process-input/", data=data, files=files)

        # Handle the response from the FastAPI endpoint
        if response.status_code == 200:
            response_json = response.json()
            print(response_json)
            if "response" in response_json:
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
