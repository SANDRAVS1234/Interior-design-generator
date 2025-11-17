import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="Interior Design Generator - Clipdrop SDXL", layout="wide")

API_KEY = st.secrets.get("CLIPDROP_API_KEY")

if not API_KEY:
    st.error("❌ Missing CLIPDROP_API_KEY in Streamlit Secrets.")
    st.stop()

CLIPDROP_URL = "https://clipdrop-api.co/text-to-image/v1"

st.title("🏡 Interior Design Generator (Clipdrop SDXL)")
st.write("Generate interior design concepts using **Stable Diffusion XL** from Clipdrop.")

prompt = st.text_area(
    "Interior design prompt:",
    "A luxury modern bedroom interior with warm ambient lighting and elegant furniture",
    height=150
)

steps = st.slider("Inference Steps", 10, 50, 30)
guidance = st.slider("Guidance Scale", 1.0, 15.0, 7.5)

generate = st.button("Generate")


def generate_image(prompt, steps, guidance):
    files = {
        "prompt": (None, prompt),
        "model": (None, "StableDiffusionXL"),
        "guidance_scale": (None, str(guidance)),
        "num_inference_steps": (None, str(steps)),
        "output_format": (None, "png"),
    }

    headers = {"x-api-key": API_KEY}

    response = requests.post(CLIPDROP_URL, headers=headers, files=files)

    if response.status_code != 200:
        raise Exception(f"❌ API Error {response.status_code}: {response.text}")

    return Image.open(io.BytesIO(response.content))


if generate:
    with st.spinner("⏳ Generating image using Clipdrop SDXL…"):
        try:
            img = generate_image(prompt, steps, guidance)

            st.success("Image Generated Successfully!")
            st.image(img, caption="Generated Interior Design", use_column_width=True)

            buf = io.BytesIO()
            img.save(buf, format="PNG")

            st.download_button(
                "Download Image",
                buf.getvalue(),
                "clipdrop_design.png",
                mime="image/png"
            )

        except Exception as e:
            st.error(str(e))
