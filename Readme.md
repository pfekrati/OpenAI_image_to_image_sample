# OpenAI Image-to-Image Sample

This project demonstrates how to use the Azure OpenAI gpt-image-1 model to generate a new image from existing images.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/pfekrati/OpenAI_image_to_image_sample.git
cd OpenAI_image_to_image_sample
```

### 2. Add Environment Variables

Create a `.env` file in the project root and add the following variables:

```env
AZURE_ENDPOINT=https://<your-endpoint>/openai/deployments/<deployment-name>/images/edits?api-version=2025-04-01-preview
API_KEY=<your-api-key>
```

> **Note:**  
> The endpoint used is for **image editing** (`edits`), not image generation.

### 3. Set Up a Virtual Environment

It is recommended to use a virtual environment:

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies

Install all required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 5. Run the Application

Start the Streamlit app:

```bash
streamlit run main.py
```

---

## Notes

- Ensure your Azure OpenAI resource is properly configured.
- Do **not** share your `.env` file or API keys publicly.

---

## License

This project is for educational purposes.