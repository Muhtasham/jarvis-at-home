import gradio as gr
import requests


def echo(message, history):
    file_paths = message.get("files", [])
    text = message.get("text", "")
    
    # Prepare the data for the POST request
    data = {'text': text}
    files = {'file': open(file_paths[0], 'rb')} if file_paths else None

    # Send the POST request to the FastAPI endpoint
    response = requests.post("http://localhost:8000/process-input/", data=data, files=files)

    # Handle the response from the FastAPI endpoint
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to process input"}


demo = gr.ChatInterface(
    fn=echo,
    examples=[{"text": "hello"}, {"text": "hola"}, {"text": "merhaba"}],
    title="MultiOm Bot",
    multimodal=True,
)
demo.launch()