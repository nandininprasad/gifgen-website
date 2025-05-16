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
from moviepy import VideoFileClip
import numpy as np
import torch


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

# def dummy_pipe(x):
#     return "assets/homealone.gif"

pipe = dummy_pipe

print("HELLO")
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
    image = request_data["image"]
    

    ### ADD A REQUIREMENTS CHECK FOR IMG 

    if image is None:
        image = Image.open("assets/blackImg.png")
        
    max_area = 480 * 832
    aspect_ratio = image.height / image.width
    mod_value = pipe.vae_scale_factor_spatial * pipe.transformer.config.patch_size[1]
    height = round(np.sqrt(max_area * aspect_ratio)) // mod_value * mod_value
    width = round(np.sqrt(max_area / aspect_ratio)) // mod_value * mod_value
    image = image.resize((width, height))



    chat_gpt_instruction = """
    You are a prompt refiner for the Wan2.1 Image to Video Model GIF generator. 
    You will receive a) text prompt b) a style string. Your job is to output 1) A good descriptive prompt
    for the Wan2.1 Image to Video model that follows all the requirements for the text prompt that generates a gif in the style
    of the style string. 2)A negative prompt 3) Output a name for the gif. You will only reply with item 1) and item 2) and item 3) Separated by a '|' character
    """


    # Get updated prompts from chatgpt
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
        {"role": "user", "content": chat_gpt_instruction + " text_prompt: " + text_prompt + " style string: " + style_string }
            ]
    )

    chatgpt_response = completion.choices[0].message.content
    print(chatgpt_response)
    chat_gpt_updated_prompt, chat_gpt_negative_prompt, gif_name = chatgpt_response.split("|") 

    num_frames = 129

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