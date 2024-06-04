from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
from openai import AsyncOpenAI
from pydantic import BaseModel
from fastapi.logger import logger

import io
import os
import multion
import torch
import instructor
import openai

from multion.client import MultiOn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

multion = MultiOn(api_key=os.environ.get("MULTION_API_KEY"))
logger.info("MultiOn API key loaded")

app = FastAPI()

device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
logger.info(f"Device: {device}")

model_id = "vikhyatk/moondream2"
revision = "2024-05-20"
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True, revision=revision).to(device)
logger.info(f"Model loaded: {model_id} to {device}")
model = torch.compile(model)
logger.info(f"Model compiled: {model_id} to {device}")
tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)
logger.info(f"Tokenizer loaded: {model_id}")

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

async def process_image_file(file: UploadFile) -> str:
    """
    Process an uploaded image file and generate a description using the model.

    Args:
        file (UploadFile): The uploaded image file.

    Raises:
        HTTPException: If the file type is not JPEG or PNG, or if there is an error processing the image.

    Returns:
        str: The description of the image.
    """
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are supported.")
    
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data))

    try:
        enc_image = model.encode_image(image)
        description = model.answer_question(enc_image, "Describe this image.", tokenizer)
        return description
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-input/")
async def process_input(text: str = Form(...), file: UploadFile = File(None)):
    if file is not None:
        try:
            logger.info("Processing image file")
            image_description = await process_image_file(file)
            logger.info(f"Image description: {image_description}")
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
    
    logger.info(f"Processed text: {processed_text}")
    command = await generate_command(processed_text)
    logger.info(f"Command generated: {command.message}")

    try:
        logger.info("Calling MultiOn API")
        response = multion.browse(
            cmd=command.cmd,
            url=command.url,
            local=command.local
        )
        logger.info(f"Response received: {response.message}")
        return JSONResponse(content={"response": response.message, "command": command.model_dump()})

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