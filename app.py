import streamlit as st
import requests
from PIL import Image
import io
import base64

st.set_page_config(page_title="Interior Design Generator - Clipdrop SDXL", layout="wide")

# Load API key
API_KEY = st.secrets.get("CLIPDROP_API_KEY")

if not API_KEY:
    st.error("❌ Missing CLIPDROP_API_KEY in Streamlit Secrets.")
    st.stop()

# Clipdrop SDXL endpoint
CLIPDROP_URL = "https://clipdrop-api.co/text-to-image/v1"

st.title("🏡 Interior Design Generator (Clipdrop SDXL)")
st.write("Generate interior design concepts using **Stable Diffusion XL (Clipdrop)**.")

prompt = st.text_area(
    "Enter your interior design prompt:",
    "A modern luxury bedroom interior with ambient lighting and wooden textures",
    height=150
)

generate = st.button("Generate Image")


def generate_image(prompt):
    headers = {
        "x-api-key": API_KEY
    }
    data = {
        "prompt": prompt,
        "output_format": "png"
    }

    response = requests.post(CLIPDROP_URL, headers=headers, data=data)

    if response.status_code != 200:
        raise Exception(f"❌ API Error {response.status_code}: {response.text}")

    return Image.open(io.BytesIO(response.content))


if generate:
    if not prompt.strip():
        st.error("⚠ Please enter a prompt.")
    else:
        with st.spinner("⏳ Generating image using Clipdrop SDXL…"):
            try:
                img = generate_image(prompt)
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
