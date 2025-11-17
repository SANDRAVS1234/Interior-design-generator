import streamlit as st
from openai import OpenAI
import base64
from PIL import Image
import io
import os

st.set_page_config(page_title="Interior Design Generator (OpenAI API)", layout="wide")

# -------------------------
# Load API Key
# -------------------------
API_KEY = None
if "OPENAI_API_KEY" in st.secrets:
    API_KEY = st.secrets["OPENAI_API_KEY"]
else:
    API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    st.error("No OpenAI API key found. Add it in Streamlit Secrets or as an env variable.")
    st.stop()

client = OpenAI(api_key=API_KEY)

# -------------------------
# UI
# -------------------------
st.title("🏡 Interior Design Generator (OpenAI API-based)")
st.markdown("This app uses **OpenAI's image generation API** to produce interior design images.")

prompt = st.text_area(
    "Enter your interior design prompt:",
    value="A modern minimalist bedroom with white walls and wooden furniture",
    height=150
)

num_images = st.slider("Number of images", 1, 4, 1)

size = st.selectbox(
    "Image Size",
    ["1024x1024", "512x512", "256x256"],
    index=0
)

generate = st.button("Generate Images")

# -------------------------
# Image Generation
# -------------------------
if generate:
    try:
        with st.spinner("Generating images with OpenAI GPU backend..."):
            response = client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size=size,
                n=num_images
            )

        images = []
        for img_data in response.data:
            img_b64 = img_data.b64_json
            img = Image.open(io.BytesIO(base64.b64decode(img_b64)))
            images.append(img)

        st.success("Images generated successfully!")

        cols = st.columns(num_images)
        for i, img in enumerate(images):
            with cols[i]:
                st.image(img, caption=f"Result #{i+1}", use_column_width=True)

                # Download button
                img_buffer = io.BytesIO()
                img.save(img_buffer, format="PNG")
                img_bytes = img_buffer.getvalue()
                b64 = base64.b64encode(img_bytes).decode()

                st.download_button(
                    "Download",
                    data=img_bytes,
                    file_name=f"design_{i+1}.png",
                    mime="image/png"
                )

    except Exception as e:
        st.error(f"Image generation failed: {str(e)}")
