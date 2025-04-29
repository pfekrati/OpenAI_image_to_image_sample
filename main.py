import streamlit as st
import os
import base64
import requests
from dotenv import load_dotenv

# Azure Foundry GPT-Image-1 endpoint and API key (replace with your actual values)
# Load environment variables from .env file
load_dotenv()

# Azure Foundry GPT-Image-1 endpoint and API key from environment variables
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
API_KEY = os.getenv("API_KEY")

# Verify environment variables are set
if not AZURE_ENDPOINT or not API_KEY:
    raise ValueError("Missing required environment variables. Please check your .env file.")

# Set page to wide mode and other configurations
st.set_page_config(
    page_title="Image-to-Image Generation with GPT-Image-1",
    layout="wide",  # This makes the app use the full width
    initial_sidebar_state="auto"
)

uploaded_files = st.file_uploader(
    "Upload one or more images", type=["png", "jpg", "jpeg"], accept_multiple_files=True
)

# Display thumbnails for uploaded images
if uploaded_files:
    st.write("Uploaded images:")
    thumbnail_cols = st.columns(min(len(uploaded_files), 4))  # Create columns for thumbnails
    for i, file in enumerate(uploaded_files):
        with thumbnail_cols[i % 4]:  # Use modulo to cycle through columns
            # Display a small thumbnail
            st.image(file, caption=file.name, width=100)
            
instruction = st.text_area("Describe the image you want to generate")

if st.button("Generate Image"):
    if not uploaded_files or not instruction.strip():
        st.warning("Please upload at least one image and provide an instruction.")
    else:
        with st.spinner("Generating image..."):
            try:

                # Prepare headers
                headers = {
                    "api-key": API_KEY,
                    # Azure OpenAI uses api-key instead of Bearer token
                }

                # Prepare the multipart form data
                files = []
                for file in uploaded_files:
                    # Reset file pointer position (might have been read already)
                    file.seek(0)
                    # Add each image to the files list with the same field name
                    files.append(("image[]", (file.name, file.read(), f"image/{file.type.split('/')[-1]}")))
                
                # Add the model and prompt to the form data
                data = {
                    "model": "gpt-image-1",
                    "prompt": instruction
                }

                # Make the API call
                response = requests.post(
                    AZURE_ENDPOINT,
                    headers=headers,
                    files=files,
                    data=data
                )

                # Check if the request was successful
                if response.status_code == 200:
                    # Parse the JSON response
                    response_data = response.json()
                    image_base64 = response_data['data'][0]['b64_json']
                    image_bytes = base64.b64decode(image_base64)
                    
                    # Display the generated image
                    st.image(image_bytes, caption="Generated Image")
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                st.error(f"Error generating image: {str(e)}")
