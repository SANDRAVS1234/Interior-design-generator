import streamlit as st
import requests
import base64

st.set_page_config(page_title="Interior Design Generator", layout="wide")

API_KEY = st.secrets["TOGETHER_API_KEY"]

def generate_image(prompt):
    url = "https://api.together.xyz/v1/images/generations"

    payload = {
        "model": "stabilityai/sdxl-turbo",
        "prompt": prompt,
        "steps": 4,
        "width": 1024,
        "height": 1024
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    # 🔥 INSERTED DEBUG LINE (must be here)
    st.write("API Response:", data)

    # If the API returned an error instead of an image
    if "data" not in data:
        st.error("API error: " + str(data))
        return None

    img_base64 = data["data"][0]["b64_json"]
    return Image.open(io.BytesIO(base64.b64decode(img_base64)))
