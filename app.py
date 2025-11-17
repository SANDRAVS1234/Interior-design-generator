import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="Interior Design Generator - Clipdrop", layout="wide")

API_KEY = st.secrets.get("CLIPDROP_API_KEY")

if not API_KEY:
    st.error("❌ Missing CLIPDROP_API_KEY in Streamlit Secrets.")
    st.stop()

CLIPDROP_URL = "https://clipdrop-api.co/text-to-image/v1"

st.title("🏡 Interior Design Generator (Clipdrop — Simple & Fast)")
st.write("Generate interior design images using Clipdrop's text-to-image API.")

prompt = st.text_area(
    "Interior design prompt:",
    "A modern luxury bedroom interior with soft lighting and warm colors",
    height=150
)

generate = st.button("Generate Image")


def generate_image(prompt):
    headers = {"x-api-key": API_KEY}

    files = {
        "prompt": (None, prompt)
    }

    response = requests.post(CLIPDROP_URL, headers=headers, files=files)

    if response.status_code != 200:
        raise Exception(f"❌ API Error {response.status_code}: {response.text}")

    return Image.open(io.BytesIO(response.content))


if generate:
    with st.spinner("⏳ Generating image using Clipdrop…"):
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
