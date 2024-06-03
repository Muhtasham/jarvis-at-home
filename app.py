from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.responses import JSONResponse
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
from openai import AsyncOpenAI
from pydantic import BaseModel

import io
import os
import multion
import torch
import instructor
import openai

from multion.client import MultiOn

multion = MultiOn(api_key=os.environ.get("MULTION_API_KEY"))

app = FastAPI()

device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
model_id = "vikhyatk/moondream2"
revision = "2024-05-20"
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True, revision=revision).to(device)
tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)

client = instructor.from_openai(AsyncOpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
))

class MultiOnInputBrowse(BaseModel):
    """
    A model for handling user commands that involve browsing actions.

    Attributes:
        cmd (str): The command to execute. Example: "post 'hello world - I love multion' on twitter".
        url (str): The URL where the action should be performed. Example: "https://twitter.com".
        local (bool): Flag indicating whether the action should be performed locally. Default is True.
    """
    cmd: str
    url: str
    local: bool = True

class MultiOnInputSession(BaseModel):
    """
    A model for handling session-based browsing actions.

    Attributes:
        cmd (str): The command to execute. Example: "Please post 'Hi from MultiOn Agent API. '".
        url (str): The URL for the session. Example: "https://twitter.com".
        local (bool): Flag indicating whether the session should be local. Default is True.
    """
    cmd: str
    url: str 
    local: bool = True

@app.post("/process-image/")
async def process_image(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are supported.")
    
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data))

    try:
        enc_image = model.encode_image(image)
        description = model.answer_question(enc_image, "Describe this image.", tokenizer)
        return {"description": description}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-input/")
async def process_input(text: str = Form(...), file: UploadFile = File(None)):
    if file is not None:
        try:
            image_response = await process_image(file)
            image_description = image_response["description"]
        except HTTPException as e:
            raise e
    else:
        image_description = None

    # Process the text and optionally include the image description
    # Example: Concatenate text and image description
    if image_description:
        processed_text = f"{text} [Image Description: {image_description}]"
    else:
        processed_text = text
    
    response = await generate_command(processed_text)

    try:
        multion.browse(
            cmd=response.cmd,
            url=response.url,
            local=response.local
        )

        print(response.message)
        return JSONResponse(content=response.message)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mution API error: {str(e)}")


async def generate_command(content: str) -> MultiOnInputBrowse:
    try:
        response = await openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
            response_model=MultiOnInputBrowse
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")