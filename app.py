import streamlit as st
from diffusers import StableDiffusionXLImg2ImgPipeline, StableDiffusionXLPipeline, EulerDiscreteScheduler
import torch
from PIL import Image

st.set_page_config(page_title="Interior Design Generator", layout="wide")

@st.cache_resource
def load_model():
    model_id = "stabilityai/sdxl-turbo"

    # Force a safe scheduler (prevents IndexError)
    scheduler = EulerDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler")

    pipe = StableDiffusionXLPipeline.from_pretrained(
        model_id,
        scheduler=scheduler,
        torch_dtype=torch.float32,
    )

    pipe = pipe.to("cpu")
    return pipe

st.title("🏡 Interior Design Generator")

prompt = st.text_area("Enter your interior design prompt:")

if st.button("Generate"):
    if not prompt.strip():
        st.error("Please enter a prompt!")
    else:
        with st.spinner("Generating..."):
            pipe = load_model()
            image = pipe(prompt, num_inference_steps=4).images[0]

        st.image(image, caption="Generated Design", use_column_width=True)

        image.save("design.png")
        with open("design.png", "rb") as f:
            st.download_button(
                "Download Image",
                data=f,
                file_name="interior_design.png",
                mime="image/png"
            )
