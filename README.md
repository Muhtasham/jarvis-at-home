# Jarvis at home 

> Mom, can we have Jarvis at home?  
> We have Jarvis at home.  
> Jarvis at home:

## Introduction

Jarvis is a virtual assistant that can help you with your daily tasks, navigate your browser, and perform various actions on the web on your behalf.

For example you can send email to your friend, or schedule a meeting with your colleagues, based on screenshot of the text.

## Flow of the App

1. **Image Input**: Provide an image to the system, along with optional text.
2. **Visual Language Model (VLM)**: Process the image using the VLM.
3. **Command Generation**: 
   - Generate a command via function calling, with pydantic models. 
   - Option to enable local browsing or online browsing directly at the FastAPI endpoint.
4. **Send Command**: Send the generated command to the MultiOn API.
5. **Action Execution**: Perform the required actions based on the command.
6. **Task Verification**: Verify that the task is completed successfully.
7. **Response**: Return the response.

## VLM Architecture

SOTA open VLM is [InternVL-1.5](https://huggingface.co/spaces/opencompass/open_vlm_leaderboard), which is *22B*, for practical deployment and being GPU poor and considering fast inference for small batch sizes, I choose `moondream2` which is a model can answer real-world questions about images. 

It's tiny by today's models, with only *1.6B* parameters it was 2x faster than `MiniCPM-V-2`. Not to mention that enables it to run on a variety of devices, including mobile phones and edge devices.

Although `MiniCPM-V-2` gave very detailed answers and supported high-Resolution images at Any Aspect Ratio for example 1.8 million pixel (e.g., 1344x1344) images at any aspect ratio, the brevity and accuracy of `moondream2` despite supporting only (378x378) images was enough for the task. You can refer to `notebooks/starter_deepqa.ipynb` for quick comparison.

Other viable altertives under 4B params would be `MiniCPM-V-2`, `PaliGemma-3B-mix-448`, and `DeepSeek-VL-1.3B`. 
For the best openVLM model regardless of size, `MiniCPM-Llama3-V-2_5` is the best choice, according to the [vision-arena](https://huggingface.co/spaces/WildVision/vision-arena) which is better proxy for real-world performance than the leaderboard.

## Deployment

I chose to deploy on [huggingface spaces](https://huggingface.co/spaces/muhtasham/agent) T4 GPU to convenience, 
Notice that the endpoint will shut down after 15 minutes of inactivity, so you will need to refresh the page to keep the [endpoint](https://huggingface.co/spaces/muhtasham/agent) alive.

One could also use serverless gpus like ones from modal labs, or the endpoints offered by fal.ai, for example my sample request took 0.50 seconds and will cost `~$ 0.00029`. For $1 I could run this model with the same options approximately [`3507 times`](https://fal.ai/models/fal-ai/moondream/batched/playground)


## Setup

Create a virtual environment and install the dependencies:

```bash
conda create -n jarvis python=3.10
conda activate jarvis
pip install -r requirements.txt
```

Set the `MULTION_API_KEY` and `OPENAI_API_KEY` environment variable in .env file.

## Run

Run the UI with:

```bash
python gradio_app.py
```

The UI will be available at http://localhost:7860 in your browser.

## Future directions

Future directions would be to use proper inference server to have high througput, and also consider fully on device deployment for privacy. Also fine-tuning llama3-8b on this conversational web navigation [dataset](https://huggingface.co/datasets/McGill-NLP/WebLINX) is a good idea.