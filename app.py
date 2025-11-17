# app.py
import streamlit as st
import requests
import io
import base64
from PIL import Image
import os
from typing import List, Optional

st.set_page_config(page_title="API-based Interior Design Generator", layout="wide")

# ---------------------------
# Helper: obtain API key
# ---------------------------
# Prefer Streamlit secrets (when deployed) but fall back to environment variable for local runs.
API_KEY = None
if "TOGETHER_API_KEY" in st.secrets:
    API_KEY = st.secrets["TOGETHER_API_KEY"]
else:
    API_KEY = os.environ.get("TOGETHER_API_KEY")

if not API_KEY:
    st.warning(
        "No API key found. Set `TOGETHER_API_KEY` in Streamlit secrets (or export it as an env var locally)."
    )

# ---------------------------
# UI: header and inputs
# ---------------------------
st.title("🏡 Interior Design Generator (API-based)")
st.markdown(
    "Enter a prompt, select style & options, and the app will request images from a GPU API (no heavy local models)."
)

with st.sidebar:
    st.header("Generation Settings")
    model = st.selectbox(
        "Model",
        options=[
            "stabilityai/sdxl-turbo",   # high-quality, fast
            "stabilityai/stable-diffusion-xl-beta",  # alternative
        ],
        index=0,
        help="Which hosted model to use via the API"
    )
    style = st.selectbox(
        "Design style",
        options=[
            "Minimalist",
            "Modern",
            "Scandinavian",
            "Industrial",
            "Bohemian",
            "Rustic",
            "Luxury",
        ],
        index=0
    )
    width = st.selectbox("Width", [512, 768, 1024], index=2)
    height = st.selectbox("Height", [512, 768, 1024], index=2)
    steps = st.slider("Steps (inference)", 1, 50, 8)
    num_images = st.slider("Number of images", 1, 4, 2)
    seed = st.text_input("Seed (optional)", value="", help="Leave blank for random")
    save_samples = st.checkbox("Show base64 response for debugging", value=False)

prompt_input = st.text_area(
    "Enter your interior design prompt",
    value="A minimalist style bedroom interior design with white walls and simple furniture",
    height=140,
)

generate_btn = st.button("Generate")

# ---------------------------
# API call helper
# ---------------------------
TOGETHER_URL = "https://api.together.xyz/v1/images/generations"

def call_together_api(
    api_key: str,
    prompt: str,
    model_name: str,
    width: int = 1024,
    height: int = 1024,
    steps: int = 4,
    n_samples: int = 1,
    seed: Optional[int] = None,
):
    """
    Calls Together Images API and returns list of PIL Images.
    Raises ValueError with the API error message if something fails.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_name,
        "prompt": prompt,
        "steps": steps,
        "width": width,
        "height": height,
        "samples": n_samples
    }
    if seed is not None:
        payload["seed"] = seed

    resp = requests.post(TOGETHER_URL, json=payload, headers=headers, timeout=120)
    try:
        data = resp.json()
    except Exception:
        raise ValueError(f"Invalid JSON response from API (status {resp.status_code}): {resp.text}")

    # Debug: optionally return the raw API data for troubleshooting
    if "error" in data:
        raise ValueError(f"API error: {data.get('error')}")
    if "data" not in data:
        # API format mismatch
        raise ValueError(f"Unexpected API response: {data}")

    images = []
    for item in data["data"]:
        # some APIs return b64 under different keys; handle common shapes
        b64 = item.get("b64_json") or item.get("b64") or item.get("b64_image")
        if not b64:
            raise ValueError(f"Expected base64 image in API response item: {item}")
        img_bytes = base64.b64decode(b64)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        images.append(img)
    return images, data

# ---------------------------
# Generate flow
# ---------------------------
if generate_btn:
    if not API_KEY:
        st.error("No API key configured. Add TOGETHER_API_KEY to Streamlit secrets or export it locally.")
    elif not prompt_input or prompt_input.strip() == "":
        st.error("Please enter a prompt.")
    else:
        final_prompt = f"{prompt_input}. Style: {style}."
        st.info("Sending request to image generation API (uses remote GPU)...")
        with st.spinner("Generating images (this may take a few seconds)..."):
            try:
                seed_val = int(seed) if seed.strip() != "" else None
            except Exception:
                seed_val = None

            try:
                imgs, raw_api = call_together_api(
                    api_key=API_KEY,
                    prompt=final_prompt,
                    model_name=model,
                    width=width,
                    height=height,
                    steps=steps,
                    n_samples=num_images,
                    seed=seed_val,
                )
            except Exception as e:
                st.error(f"Generation failed: {str(e)}")
                if isinstance(e, ValueError):
                    st.write("Full API response (debug):")
                    st.write(getattr(e, "args", ["no extra info"]))
                raise st.stop()

            st.success(f"Generated {len(imgs)} image(s).")

            # show raw response optionally
            if save_samples:
                st.subheader("Raw API response (debug)")
                st.json(raw_api)

            # display images in a grid
            cols = st.columns(len(imgs))
            for i, img in enumerate(imgs):
                with cols[i]:
                    st.image(img, use_column_width=True, caption=f"Result #{i+1}")
                    # download button
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    byte_data = buf.getvalue()
                    b64_download = base64.b64encode(byte_data).decode()
                    href = f"data:file/png;base64,{b64_download}"
                    st.markdown(f"[Download image {i+1}]({href})", unsafe_allow_html=True)

        st.balloons()

# ---------------------------
# Footer: instructions
# ---------------------------
st.markdown("---")
st.markdown(
    "**How to set API key**\n\n"
    "- On Streamlit Cloud: go to _Manage app → Settings → Secrets_ and add `TOGETHER_API_KEY = \"your_key_here\"`.\n"
    "- Locally: in your terminal run `export TOGETHER_API_KEY=your_key` (mac/linux) or `setx TOGETHER_API_KEY \"your_key\"` (Windows), then restart VS Code.\n"
    "- You can also set `st.secrets` via a `.streamlit/secrets.toml` file for local testing:\n\n"
    "```\n"
    "TOGETHER_API_KEY = \"your_key_here\"\n"
    "```\n"
)
