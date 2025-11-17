import streamlit as st
from PIL import Image
import torch
from diffusers import StableDiffusionPipeline

st.set_page_config(page_title="DreamSpace: AI-Crafted Interiors", layout="wide")

@st.cache_resource
def load_model():
    model_id = "runwayml/stable-diffusion-v1-5"
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
    return pipe

st.title("🎨 Text-to-Image Generator")

prompt = st.text_input("Enter your prompt:")
generate = st.button("Generate")

if generate and prompt.strip() != "":
    with st.spinner("Generating image..."):
        pipe = load_model()
        result = pipe(prompt)
        image = result.images[0]

        st.image(image, caption="Generated Image", use_column_width=True)

        # Option to download output
        image.save("output.png")
        with open("output.png", "rb") as f:
            st.download_button("Download Image", data=f, file_name="image.png")
