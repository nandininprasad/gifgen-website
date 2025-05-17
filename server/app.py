
# Imports
import os
import base64
from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from generate import generate_gif
from diffusers import AutoencoderKLWan, WanImageToVideoPipeline
from diffusers.utils import export_to_video, load_image
from transformers import CLIPVisionModel, BitsAndBytesConfig
from PIL import Image
import io
from pathlib import Path
from typing import Union
from moviepy import VideoFileClip
import numpy as np
import torch

# Get the api
load_dotenv()
open_ai_api_key = os.environ["OPEN_AI_API_KEY"]

if not open_ai_api_key:
    print("Error: OPEN_AI_API_KEY not found in environment variables.")
    raise Exception("Open ai key not found")

client = OpenAI(api_key=open_ai_api_key)

app = Flask(__name__)
CORS(app)

LOG_PATH = "./logs"
UPLOAD_FOLDER = "uploads"
GIF_OUTPUT_FOLDER = "generated_gifs"
MP4_OUTPUT_FOLDER = "generated_mp4s"

if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

if not os.path.exists(GIF_OUTPUT_FOLDER):
    os.mkdir(GIF_OUTPUT_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['LOG_PATH'] = LOG_PATH
app.config['GIF_OUTPUT_FOLDER'] = GIF_OUTPUT_FOLDER
app.config['MP4_OUTPUT_FOLDER'] = MP4_OUTPUT_FOLDER

def pillow_to_data_url(img: Image.Image, fmt: str = "PNG") -> str:
    """
    Convert a Pillow image to a Base-64 Data URL.

    Parameters
    ----------
    img  : PIL.Image
    fmt  : str  ── Output format (e.g. "PNG", "JPEG").

    Returns
    -------
    str  ── 'data:image/<fmt>;base64,<bytes…>' ready for web APIs.
    """
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/{fmt.lower()};base64,{b64}"


def data_url_to_pillow(data_url: str) -> Image.Image:
    """
    Convert a Base-64 Data URL back to a Pillow image.

    Parameters
    ----------
    data_url : str  ── Must start with 'data:image/' and contain ';base64,'.

    Returns
    -------
    PIL.Image  ── In-memory image object.
    """
    header, b64 = data_url.split(",", 1)
    raw = base64.b64decode(b64)
    return Image.open(io.BytesIO(raw))


# Load pipeline into memory
def load_model_into_VRAM():
    model_id = "Wan-AI/Wan2.1-I2V-14B-480P-Diffusers"

    image_encoder = CLIPVisionModel.from_pretrained(
    model_id, subfolder="image_encoder", torch_dtype=torch.float32
)
    vae = AutoencoderKLWan.from_pretrained(model_id, subfolder="vae", torch_dtype=torch.float32)
    pipe = WanImageToVideoPipeline.from_pretrained(
    model_id, vae=vae, image_encoder=image_encoder, torch_dtype=torch.bfloat16,
)

    pipe.to("cuda")
    return pipe

pipe = load_model_into_VRAM()

@app.route("/api/generate_gif", methods=["POST"])
def process_request():
    """
    This api receives the request to generate a GIF
    It expects a request with :
    id: unique id identified
    image: optional png file to serve as the first frame of the GIF
    text: A text prompt to condition the generation of the GIF
    style: A string selection that adds a style description to the prompt
    """
    print("POST request received")
    
        
    request_data = request.get_json()
    text_prompt = request_data["text_prompt"]
    style_string = request_data["style_string"]
    image_data_url = request_data["image"]


    if image is None:
        image = Image.open("assets/blackImg.png")
        image_data_url = url_from_pil(image)
    else:
        image = pil_from_url(image_data_url)
        
    max_area = 480 * 832
    aspect_ratio = image.height / image.width
    mod_value = pipe.vae_scale_factor_spatial * pipe.transformer.config.patch_size[1]
    height = round(np.sqrt(max_area * aspect_ratio)) // mod_value * mod_value
    width = round(np.sqrt(max_area / aspect_ratio)) // mod_value * mod_value
    image = image.resize((width, height))



    chat_gpt_instruction = """You are a prompt refiner for the Wan2.1 Image to Video Model GIF generator. 
    You will receive a) text prompt b) a style string. Your job is to output 1) A good descriptive prompt
    for the Wan2.1 Image to Video model that follows all the requirements for the text prompt that generates a gif in the style
    of the style string. 2)A negative prompt 3) Output a name for the gif.
    There are three styles, realstic, which focuses on photo realistic video with correct lighting, animated, which looks like an animated disney or pixar video and finally painting
    which emulates the style of a water or oil painting, showing strokes and artistic choices. The negative prompt should be a bunch of keywords separated by commas like 'Shaky', Distorted, blurry, low quality, and even add 'animated' for the realistic style, cause animated is not realistic. For negative prompt add descriptors that are undesirable
    For example:
    prompt = "A cat and a dog baking a cake together in a kitchen. The cat is carefully measuring flour, while the dog is stirring the batter with a wooden spoon. The kitchen is cozy, with sunlight streaming through the window."
negative_prompt = "Bright tones, overexposed, static, blurred details, subtitles, style, works, paintings, images, static, overall gray, worst quality, low quality, JPEG compression residue, ugly, incomplete, extra fingers, poorly drawn hands, poorly drawn faces, deformed, disfigured, misshapen limbs, fused fingers, still picture, messy background, three legs, many people in the background, walking backwards"
    Use the word realistic, animated or painting in the prompt depending on the style
    The user has also attached an image from which the gif generation has to start from, tailor prompt accordingly.
     You will only reply with item 1) and item 2) and item 3) Separated by a '|' character. Your response should be of the form [positive prompt] | [negative prompt] | [title]
    """

    # Get updated prompts from chatgpt
    completion = client.chat.completions.create(
    model="gpt-4o",
    max_tokens=512, 
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"{chat_gpt_instruction} "
                        f"text_prompt: {text_prompt} "
                        f"style string: {style_string}"
                    )
                },
                {
                    "type": "image_url",
                    "image_url": { "url": image_data_url }  # send image
                }
            ]
        }
    ]
)

    chatgpt_response = completion.choices[0].message.content
    print(chatgpt_response)
    chat_gpt_updated_prompt, chat_gpt_negative_prompt, gif_name = chatgpt_response.split("|") 

    num_frames = 33

    output = pipe(
        image=image,
        prompt=chat_gpt_updated_prompt,
        negative_prompt=chat_gpt_negative_prompt,
        height=height,
        width=width,
        num_frames=num_frames,
        guidance_scale=5.0,
        num_inference_steps=30,
    ).frames[0]


    mp4_path = app.config["MP4_OUTPUT_FOLDER"] + "/" + gif_name + ".mp4"
    gif_path = app.config["GIF_OUTPUT_FOLDER"] + "/" + gif_name + ".gif"

    export_to_video(output, mp4_path, fps=16) # 

    # Convert MP4 to GIF
    videoClip = VideoFileClip(mp4_path)
    videoClip.write_gif(gif_path)
    print("Sent file back") 

    with open(gif_path, "rb") as f: # Change this to gif
        gif_binary_data = f.read()

    gifbase64 = base64.b64encode(gif_binary_data).decode("utf-8")

    response = {
        "chatgpt-prompt": chat_gpt_updated_prompt,
        "gif-name": gif_name,
        "gif-data": gifbase64,
        "mimetype": "image/gif"
    
    }

    return jsonify(response), 200


if __name__ == '__main__':

    app.run(debug=True, port=5000)