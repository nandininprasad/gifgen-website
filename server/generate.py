import torch
import os
from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
from diffusers import AutoencoderKLWan, WanImageToVideoPipeline
from diffusers.utils import export_to_video, load_image
from transformers import CLIPVisionModel, BitsAndBytesConfig
from PIL import Image

load_dotenv()
open_ai_api_key = os.environ["OPEN_AI_API_KEY"]

if not open_ai_api_key:
    print("Error: OPEN_AI_API_KEY not found in environment variables.")
    raise Exception("Open ai key not found")

client = OpenAI(api_key=open_ai_api_key)




def generate_gif(text_prompt, style_string, starting_image, output_folder):
    return "ok"


if __name__ == "__main__":
    # Available models: Wan-AI/Wan2.1-I2V-14B-480P-Diffusers, Wan-AI/Wan2.1-I2V-14B-720P-Diffusers
    model_id = "Wan-AI/Wan2.1-I2V-14B-480P-Diffusers"

    image_encoder = CLIPVisionModel.from_pretrained(
        model_id, subfolder="image_encoder", torch_dtype=torch.float32
    )
    vae = AutoencoderKLWan.from_pretrained(model_id, subfolder="vae", torch_dtype=torch.float32)
    pipe = WanImageToVideoPipeline.from_pretrained(
        model_id, vae=vae, image_encoder=image_encoder, torch_dtype=torch.bfloat16,
    )

    pipe.to("cuda")

    image = Image.open("./seg_woman_01.png")

    max_area = 480 * 832
    aspect_ratio = image.height / image.width
    mod_value = pipe.vae_scale_factor_spatial * pipe.transformer.config.patch_size[1]
    height = round(np.sqrt(max_area * aspect_ratio)) // mod_value * mod_value
    width = round(np.sqrt(max_area / aspect_ratio)) // mod_value * mod_value
    image = image.resize((width, height))


    prompt = "A young woman with long dark hair sits by a window in a cozy café, sipping coffee from a ceramic mug. Soft morning light filters through the glass, casting warm highlights on her face. Outside, the street is quiet. Her expression is peaceful, lost in thought, with a gentle steam rising from the mug. The camera slowly zooms in."

    negative_prompt = "Bright tones, overexposed, static, blurred details, subtitles, style, works, paintings, images, static, overall gray, worst quality, low quality, JPEG compression residue, ugly, incomplete, extra fingers, poorly drawn hands, poorly drawn faces, deformed, disfigured, misshapen limbs, fused fingers, still picture, messy background, three legs, many people in the background, walking backwards"

    num_frames = 129

    output = pipe(
        image=image,
        prompt=prompt,
        negative_prompt=negative_prompt,
        height=height,
        width=width,
        num_frames=num_frames,
        guidance_scale=5.0,
        num_inference_steps=30,
    ).frames[0]
    export_to_video(output, "wan-i2v.mp4", fps=16)