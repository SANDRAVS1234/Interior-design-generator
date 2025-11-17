import streamlit as st
import requests
from PIL import Image
import io
import os
import base64

st.set_page_config(page_title="Interior Design Generator - Stability AI", layout="wide")

# ---------------------------------------
# Load API Key
# ---------------------------------------
API_KEY = None

if "STABILITY_API_KEY" in st.secrets:
    API_KEY = st.secrets["STABILITY_API_KEY"]
else:
    API_KEY = os.getenv("STABILITY_API_KEY")

if not API_KEY:
    st.error("❌ Missing StabilityAI API Key. Add STABILITY_API_KEY to secrets.")
    st.stop()

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

API_URL = "https://api.stability.ai/v2beta/stable-image/generate/sd3"


# ---------------------------------------
# Generate Image Function
# ---------------------------------------
def generate_image(prompt, size="1024x1024"):
    width, height = size.split("x")

    payload = {
        "prompt": prompt,
        "aspect_ratio": "1:1",
        "output_format": "png",
        "height": int(height),
        "width": int(width)
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise ValueError(f"Error {response.status_code}: {response.text}")

    img_bytes = response.content
    img = Image.open(io.BytesIO(img_bytes))
    return img


# ---------------------------------------
# UI
# ---------------------------------------
st.title("🏡 Interior Design Generator (Stability AI — FREE)")
st.write("Generate interior design images using StabilityAI's **SD3** model for free.")

prompt = st.text_area(
    "Enter your interior design prompt:",
    value="A luxury modern living room with marble floor, soft lighting, and elegant furniture",
    height=150
)

size = st.selectbox(
    "Image Size",
    ["512x512", "768x768", "1024x1024"],
    index=2
)

generate = st.button("Generate Image")

# ---------------------------------------
# Generate
# ---------------------------------------
if generate:
    if prompt.strip() == "":
        st.error("⚠ Enter a prompt.")
    else:
        with st.spinner("⏳ Generating image using FREE StabilityAI API…"):
            try:
                img = generate_image(prompt, size)
                st.success("Image generated successfully!")

                st.image(img, caption="Generated Design", use_column_width=True)

                # Download
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button(
                    "Download Image",
                    buf.getvalue(),
                    "sd3_design.png",
                    mime="image/png"
                )

            except Exception as e:
                st.error(f"Generation failed: {str(e)}")
