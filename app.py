import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="Interior Design Generator - FREE (No API Key)", layout="wide")

MODEL_URL = "https://api-inference.huggingface.co/models/stabilityai/sdxl-turbo"

st.title("🏡 Interior Design Generator (FREE • No API Key Required)")
st.write("Generate images using the public HuggingFace SDXL-Turbo API.")

prompt = st.text_area(
    "Enter your interior design prompt:",
    "A modern luxurious living room interior with marble flooring and warm lighting",
    height=150
)

generate = st.button("Generate Image")


def generate_image(prompt):
    payload = {"inputs": prompt}

    response = requests.post(MODEL_URL, json=payload)

    if response.status_code != 200:
        raise ValueError(f"API Error {response.status_code}: {response.text}")

    return Image.open(io.BytesIO(response.content))


if generate:
    if not prompt.strip():
        st.error("⚠ Please enter a prompt.")
    else:
        with st.spinner("⏳ Generating image using HuggingFace (free public model)..."):
            try:
                img = generate_image(prompt)
                st.image(img, caption="Generated Interior Design", use_column_width=True)

                # Download button
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button(
                    "Download Image",
                    buf.getvalue(),
                    "design.png",
                    mime="image/png"
                )
            except Exception as e:
                st.error(str(e))
