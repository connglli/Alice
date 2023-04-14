import io
import os.path
import uuid

import requests
from config import Config
from PIL import Image

cfg = Config()
working_directory = "auto_gpt_workspace"


def generate_image(prompt):

    filename = str(uuid.uuid4()) + ".jpg"

    # STABLE DIFFUSION
    if cfg.image_provider == 'sd':

        API_URL = "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"
        headers = {"Authorization": "Bearer " + cfg.huggingface_api_token}

        response = requests.post(API_URL, headers=headers, json={
            "inputs": prompt,
        })

        image = Image.open(io.BytesIO(response.content))
        print("Image Generated for prompt:" + prompt)

        image.save(os.path.join(working_directory, filename))

        return "Saved to disk:" + filename

    else:
        return "No Image Provider Set"
