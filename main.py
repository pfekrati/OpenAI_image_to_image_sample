import streamlit as st
import os
import base64
import requests
from dotenv import load_dotenv
from PIL import Image
import io

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

# Display thumbnails for uploaded images in a grid (3 per row)
if uploaded_files:
    st.write("### Uploaded images")
    
    # Create rows of 3 images each
    for i in range(0, len(uploaded_files), 3):
        # Create columns for each row
        cols = st.columns(3)
        
        # Fill each column with an image if available
        for j in range(3):
            if i + j < len(uploaded_files):
                with cols[j]:
                    file = uploaded_files[i + j]
                    img = Image.open(file)
                    # Calculate thumbnail width and height as 50% of original
                    thumbnail_width = img.width // 2
                    file.seek(0)  # Reset file pointer
                    st.image(file, caption=file.name, width=thumbnail_width)
                    # Show image dimensions as additional info
                    st.caption(f"Dimensions: {img.width}x{img.height}")
            
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
                    "prompt": instruction,
                    "n": 3
                    # ,"output_compression": 80,
                    # "quality": "high",
                    # "output_format":"jpeg"
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

                    print(response_data)  # Debugging line to check the response structure
                    
                    # Create a header for the generated images
                    st.write("### Generated Images")
                    
                    # Create 3 columns for the images
                    cols = st.columns(3)
                    
                    # Display each generated image in its own column
                    for i, img_data in enumerate(response_data['data']):
                        image_base64 = img_data['b64_json']
                        image_bytes = base64.b64decode(image_base64)
                        
                        # Create a temporary PIL Image to get dimensions
                        pil_img = Image.open(io.BytesIO(image_bytes))
                        # Calculate width as 50% of original
                        width = pil_img.width // 2
                        
                        # Display in the appropriate column
                        with cols[i]:
                            st.image(image_bytes, caption=f"Generated Image {i+1}", width=width)
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                st.error(f"Error generating image: {str(e)}")
