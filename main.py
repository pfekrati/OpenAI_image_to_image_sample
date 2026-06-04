import streamlit as st
import os
import base64
import html
import requests
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from PIL import Image
import io

# Load environment variables from .env file
load_dotenv()

# Azure Foundry GPT-Image-1 endpoint from environment variables
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_OPENAI_SCOPE = "https://cognitiveservices.azure.com/.default"
credential = DefaultAzureCredential()

# Verify environment variables are set
if not AZURE_ENDPOINT:
    raise ValueError("Missing required environment variable AZURE_ENDPOINT. Please check your .env file.")

# Set page to wide mode and other configurations
st.set_page_config(
    page_title="Image-to-Image Generation with GPT-Image-1",
    layout="wide",  # This makes the app use the full width
    initial_sidebar_state="auto"
)

st.markdown(
    """
    <style>
    .image-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1rem;
        align-items: stretch;
        margin-bottom: 1rem;
    }
    .image-card {
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 0.5rem;
        padding: 0.75rem;
        background: rgba(250, 250, 250, 0.04);
        min-width: 0;
    }
    .image-frame {
        width: 100%;
        height: 260px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border-radius: 0.35rem;
        background: rgba(49, 51, 63, 0.06);
    }
    .image-frame img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        display: block;
    }
    .image-caption {
        margin-top: 0.5rem;
        font-size: 0.9rem;
        font-weight: 600;
        overflow-wrap: anywhere;
    }
    .image-dimensions {
        margin-top: 0.15rem;
        color: rgba(49, 51, 63, 0.7);
        font-size: 0.82rem;
    }
    .output-link {
        display: block;
        color: inherit;
        text-decoration: none;
    }
    .image-modal {
        display: none;
        position: fixed;
        inset: 0;
        z-index: 999999;
        background: rgba(0, 0, 0, 0.85);
        padding: 2rem;
        align-items: center;
        justify-content: center;
    }
    .image-modal:target {
        display: flex;
    }
    .modal-content {
        max-width: 96vw;
        max-height: 96vh;
        overflow: auto;
        background: #111;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 0.75rem 2rem rgba(0, 0, 0, 0.5);
    }
    .modal-content img {
        width: auto;
        height: auto;
        max-width: none;
        max-height: none;
        display: block;
    }
    .modal-close {
        position: fixed;
        top: 1rem;
        right: 1.25rem;
        color: #fff !important;
        font-size: 2rem;
        line-height: 1;
        text-decoration: none;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def image_to_data_url(image_bytes, mime_type):
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def render_image_grid(images, enable_modal=False):
    grid_parts = ['<div class="image-grid">']
    modal_parts = []

    for index, image in enumerate(images):
        caption = html.escape(image["caption"])
        dimensions = html.escape(image["dimensions"])
        src = image["src"]
        modal_id = f"generated-image-{index + 1}" if enable_modal else None

        image_markup = (
            f'<div class="image-frame"><img src="{src}" alt="{caption}"></div>'
            f'<div class="image-caption">{caption}</div>'
            f'<div class="image-dimensions">{dimensions}</div>'
        )

        if modal_id:
            grid_parts.append(
                f'<div class="image-card">'
                f'<a class="output-link" href="#{modal_id}" title="Open full-size image">'
                f'{image_markup}'
                f'</a>'
                f'</div>'
            )
            modal_parts.append(
                f'<div id="{modal_id}" class="image-modal">'
                f'<a class="modal-close" href="#generated-images" aria-label="Close">&times;</a>'
                f'<div class="modal-content"><img src="{src}" alt="{caption}"></div>'
                f'</div>'
            )
        else:
            grid_parts.append(f'<div class="image-card">{image_markup}</div>')

    grid_parts.append("</div>")
    st.markdown("".join(grid_parts + modal_parts), unsafe_allow_html=True)


uploaded_files = st.file_uploader(
    "Upload one or more images", type=["png", "jpg", "jpeg"], accept_multiple_files=True
)

# Display thumbnails for uploaded images in a grid (3 per row)
if uploaded_files:
    st.write("### Uploaded images")

    uploaded_images = []
    for file in uploaded_files:
        image_bytes = file.getvalue()
        img = Image.open(io.BytesIO(image_bytes))
        uploaded_images.append(
            {
                "src": image_to_data_url(image_bytes, file.type),
                "caption": file.name,
                "dimensions": f"Dimensions: {img.width}x{img.height}",
            }
        )

    render_image_grid(uploaded_images)
             
instruction = st.text_area("Describe the image you want to generate")

if st.button("Generate Image"):
    if not uploaded_files or not instruction.strip():
        st.warning("Please upload at least one image and provide an instruction.")
    else:
        with st.spinner("Generating image..."):
            try:

                access_token = credential.get_token(AZURE_OPENAI_SCOPE).token

                # Prepare headers
                headers = {
                    "Authorization": f"Bearer {access_token}",
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
                    "n": 5
                    ,"output_compression": 100,
                     "quality": "high",
                    "output_format":"png",
                    "size": "1024x1024"
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
                     
                    # Create a header for the generated images
                    st.markdown('<h3 id="generated-images">Generated Images</h3>', unsafe_allow_html=True)
                     
                    generated_images = []
                    for i, img_data in enumerate(response_data['data']):
                        image_base64 = img_data['b64_json']
                        image_bytes = base64.b64decode(image_base64)
                         
                        # Create a temporary PIL Image to get dimensions
                        pil_img = Image.open(io.BytesIO(image_bytes))
                        generated_images.append(
                            {
                                "src": image_to_data_url(image_bytes, "image/png"),
                                "caption": f"Generated Image {i+1}",
                                "dimensions": f"Dimensions: {pil_img.width}x{pil_img.height}",
                            }
                        )

                    render_image_grid(generated_images, enable_modal=True)
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                st.error(f"Error generating image: {str(e)}")
