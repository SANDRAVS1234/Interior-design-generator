import streamlit as st
import requests
from PIL import Image
import io
import os

st.set_page_config(page_title="Interior Design Generator - Stability AI SD3", layout="wide")

# ------------------------------
# Load API Key
# ------------------------------
API_KEY = None

if "STABILITY_API_KEY" in st.secrets:
    API_KEY = st.secrets["STABILITY_API_KEY"]
else:
    API_KEY = os.getenv("STABILITY_API_KEY")

if not API_KEY:
    st.error("❌ Missing API key. Add STABILITY_API_KEY to Streamlit secrets.")
    st.stop()


# ------------------------------
# SD3 Image Generation Endpoint
# ------------------------------
API_URL = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "image/*"    # <-- FIXED HERE
}


# ------------------------------
# Call Stability API (multipart)
# ------------------------------
def generate_image(prompt: str):
    files = {
        "prompt": (None, prompt),
        "output_format": (None, "png"),
        "aspect_ratio": (None, "1:1"),
    }

    response = requests.post(API_URL, headers=headers, files=files)

    if response.status_code != 200:
        raise Exception(f"❌ API Error {response.status_code}: {response.text}")

    img = Image.open(io.BytesIO(response.content))
    return img


# ------------------------------
# UI
# ------------------------------
st.title("🏡 Interior Design Generator (Stability AI SD3 — FREE Trial)")
st.write("Generate high-quality interior design images using Stable Diffusion 3 (SD3).")

prompt = st.text_area(
    "Enter your interior design prompt:",
    "A luxurious modern bedroom interior with large windows, warm lighting, and minimal furniture"
)

generate_btn = st.button("Generate Image")

if generate_btn:
    if not prompt.strip():
        st.error("⚠ Please enter a prompt.")
    else:
        with st.spinner("⏳ Generating image using Stability AI (SD3)…"):
            try:
                img = generate_image(prompt)
                st.image(img, caption="Generated Interior Design", use_column_width=True)

                # Download
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button(
                    "Download Image",
                    data=buf.getvalue(),
                    file_name="sd3_interiordesign.png",
                    mime="image/png"
                )

            except Exception as e:
                st.error(str(e))
