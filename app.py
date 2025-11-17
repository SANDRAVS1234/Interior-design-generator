import streamlit as st
import torch
from diffusers import StableDiffusionPipeline
from PIL import Image

# --- Configuration ---
# This MUST match the path where your notebook saved the fine-tuned model
MODEL_PATH = r"C:\Users\sandra\Documents\streamlit_project\fine_tuned_model"
APP_API_KEY = "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" 

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="Interior Design Generator")
st.title("Interior Design Stable Diffusion Model 🏠")

# --- Caching the Model ---
# This loads the model only once and keeps it in memory for performance
@st.cache_resource
def load_pipeline(model_path):
    try:
        pipeline = StableDiffusionPipeline.from_pretrained(
            model_path,
            torch_dtype=torch.float16
        )
        pipeline = pipeline.to("cuda")
        pipeline.enable_xformers_memory_efficient_attention()
        return pipeline
    except Exception as e:
        st.error(f"Error loading model from {model_path}. Make sure the path is correct. Error: {e}")
        return None

# --- Main Application ---
# Simple password protection
api_key_input = st.text_input("Enter your API Key (Password):", type="password")

if api_key_input == APP_API_KEY:
    st.success("Access Granted!")
    
    # Load the model
    pipeline = load_pipeline(MODEL_PATH)
    
    if pipeline:
        # --- User Inputs ---
        prompt = st.text_area("Enter your design prompt:", "A minimalist style bedroom interior design")
        
        with st.form("generate_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                num_inference_steps = st.slider("Inference Steps", 25, 100, 50)
            with col2:
                guidance_scale = st.slider("Guidance Scale (CFG)", 1.0, 20.0, 7.5)
            with col3:
                num_images = st.slider("Number of Images", 1, 4, 1)

            submit_button = st.form_submit_button(label="Generate Image")

        # --- Image Generation ---
        if submit_button:
            with st.spinner(f"Generating {num_images} image(s)..."):
                try:
                    images_list = []
                    for _ in range(num_images):
                        with torch.autocast("cuda"):
                            image = pipeline(
                                prompt,
                                num_inference_steps=num_inference_steps,
                                guidance_scale=guidance_scale,
                                height=512,
                                width=512
                            ).images[0]
                        images_list.append(image)
                    
                    st.image(images_list, caption=[f"Generated Image #{i+1}" for i in range(len(images_list))])
                
                except Exception as e:
                    st.error(f"An error occurred during image generation: {e}")

else:
    if api_key_input:
        st.error("Invalid API Key. Please try again.")

st.sidebar.info(
    "**About this app:**\n"
    "This Streamlit app loads a fine-tuned Stable Diffusion model (`runwayml/stable-diffusion-v1-5`) "
    "for generating interior design images based on text prompts."
)




