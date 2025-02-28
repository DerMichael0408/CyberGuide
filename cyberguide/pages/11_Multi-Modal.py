import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO
import json
import ollama
import fitz  # PyMuPDF for PDF handling
import tempfile
import os
from utilities.icon import page_icon
from utilities.template import setup_page

# Use setup_page for consistent styling and sidebar
setup_page(
    page_title="Multi-Modal",
    icon_emoji="📄",
    subtitle="Analyze images and documents with multi-modal AI models"
)

# Custom CSS for better styling - matching model management page aesthetics
st.markdown("""
<style>
    /* Content containers */
    .content-container {
        background-color: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #eee;
        padding: 15px;
        height: 600px;
        overflow-y: auto;
    }
    
    /* Chat message styling */
    .user-message {
        background-color: #e6f3ff;
        border-radius: 10px;
        padding: 12px;
        margin: 8px 0;
        border-bottom-right-radius: 2px;
    }
    .assistant-message {
        background-color: #f0f0f0;
        border-radius: 10px;
        padding: 12px;
        margin: 8px 0;
        border-bottom-left-radius: 2px;
    }
    
    /* Model status indicator */
    .model-status {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 10px 15px;
        margin-bottom: 15px;
        border-left: 3px solid #FF4B4B;
    }
    
    /* File upload area */
    .upload-area {
        border: 2px dashed #ddd;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        margin-bottom: 15px;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background-color: #FF4B4B !important;
    }
    
    /* PDF preview container */
    .pdf-preview {
        background-color: #f9f9f9;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

def img_to_base64(image):
    """
    Convert an image to base64 format.

    Args:
        image: PIL.Image - The image to be converted.
    Returns:
        str: The base64 encoded image.
    """
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def check_if_llava_installed():
    """
    Check if llava model is installed.
    """
    try:
        models_info = ollama.list()
        # Try to get "name" and fallback to "model" if "name" isn't present.
        installed_models = [
            m.get("name", m.get("model", "")) for m in models_info.get("models", [])
        ]
        return "llava:latest" in installed_models
    except Exception as e:
        st.error(f"Error checking models: {str(e)}")
        return False

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(pdf_file.read())
        temp_path = temp_file.name
    
    text = ""
    try:
        doc = fitz.open(temp_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        doc.close()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    return text

def get_pdf_images(pdf_file, max_pages=3):
    """Extract images of the first few pages from a PDF file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(pdf_file.read())
        temp_path = temp_file.name
    
    images = []
    try:
        doc = fitz.open(temp_path)
        num_pages = min(len(doc), max_pages)
        
        for page_num in range(num_pages):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            img_data = pix.tobytes("png")
            images.append(Image.open(BytesIO(img_data)))
        
        doc.close()
    except Exception as e:
        st.error(f"Error extracting images from PDF: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    return images

def download_llava():
    """Download llava model with a progress bar."""
    progress_bar = st.progress(0, text="Starting download of llava:latest...")
    status_area = st.empty()
    
    try:
        last_percentage = 0
        
        for progress in ollama.pull("llava:latest", stream=True):
            if 'status' in progress:
                status_area.text(progress['status'])
            
            if 'completed' in progress and 'total' in progress and progress['total'] > 0:
                percentage = min(99, int((progress['completed'] / progress['total']) * 100))
                progress_bar.progress(percentage/100, text=f"Downloading llava:latest: {percentage}%")
                last_percentage = percentage
                
            # Check if download is complete
            if 'completed' in progress and progress.get('completed', False):
                break
        
        progress_bar.progress(100, text="Downloaded llava:latest!")
        status_area.success("✅ llava:latest downloaded successfully!")
        return True
    except Exception as e:
        status_area.error(f"Failed to download llava:latest: {str(e)}")
        return False

def main():
    #page_icon("📄")
    role_suffix = f" (Role: {st.session_state.selected_role})" if 'selected_role' in st.session_state else ""
    #st.subheader(f"Multi-Modal{role_suffix}", divider="red", anchor=False)
    
    # Initialize session state
    if "chats" not in st.session_state:
        st.session_state.chats = []
    if "current_document" not in st.session_state:
        st.session_state.current_document = None
    if "document_type" not in st.session_state:
        st.session_state.document_type = None
    
    # Check if llava is installed
    llava_installed = check_if_llava_installed()
    
    # Model status indicator
    if not llava_installed:
        st.markdown(
            """
            <div class="model-status">
                <strong>⚠️ llava:latest is not installed</strong><br>
                This tool requires the llava multimodal model for image and PDF analysis.
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        if st.button("📥 Download llava:latest Model"):
            if download_llava():
                st.success("Model downloaded successfully! Refreshing...")
                st.rerun()
        
        st.info("Please download the required model to continue.")
        return
    
    # File upload section
    st.markdown("### Upload a Document for Analysis")
    uploaded_file = st.file_uploader(
        "Upload an image or PDF for analysis",
        type=["png", "jpg", "jpeg", "pdf"],
        help="Upload an image or PDF to analyze for potential phishing indicators"
    )

    # Create two columns for chat and document display
    col1, col2 = st.columns(2)

    # Chat column
    with col1:
        st.markdown("### Analysis Chat")
        chat_container = st.container(height=600, border=True)
        
        # Display chat only if a file is uploaded
        if uploaded_file is not None:
            # Determine file type and process accordingly
            if uploaded_file.type == "application/pdf":
                st.session_state.document_type = "pdf"
                
                # Process PDF if it's a new document
                if st.session_state.current_document != uploaded_file.name:
                    with st.spinner("Processing PDF..."):
                        # Extract PDF text
                        pdf_text = extract_text_from_pdf(uploaded_file)
                        
                        # Reset file pointer
                        uploaded_file.seek(0)
                        
                        # Convert PDF pages to images
                        pdf_images = get_pdf_images(uploaded_file)
                        
                        # Store the first image and text for analysis if available
                        if pdf_images:
                            st.session_state.current_document = uploaded_file.name
                            st.session_state.pdf_image = pdf_images[0]
                            st.session_state.pdf_text = pdf_text
                        else:
                            st.error("Could not extract images from PDF")
                            return
                # Retrieve the cached image from session state
                image = st.session_state.pdf_image
            else:
                st.session_state.document_type = "image"
                # Process image
                if st.session_state.current_document != uploaded_file.name:
                    # If new image, clear chat
                    st.session_state.chats = []
                    st.session_state.current_document = uploaded_file.name
                # Open the image
                image = Image.open(uploaded_file)
            
            # Display chat messages
            with chat_container:
                for message in st.session_state.chats:
                    avatar = "🧠" if message["role"] == "assistant" else "🔍"
                    with st.chat_message(message["role"], avatar=avatar):
                        st.markdown(message["content"])
                
                # Chat input
                user_input = st.chat_input("Ask about potential phishing indicators...")
                
                if user_input:
                    # Add user message to chat
                    st.session_state.chats.append({"role": "user", "content": user_input})
                    
                    # Display user message
                    with st.chat_message("user", avatar="🔍"):
                        st.markdown(user_input)
                    
                    # Convert image for API
                    image_base64 = img_to_base64(image)
                    
                    # API preparation
                    API_URL = "http://localhost:11434/api/generate"
                    headers = {
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    }
                    
                    # Add context for PDF if applicable
                    if st.session_state.document_type == "pdf":
                        prompt = f"""
                        I'm showing you both an image of the first page of a PDF and providing some text extracted from it.
                        
                        Text from PDF:
                        {st.session_state.pdf_text[:2000]}...
                        
                        User question: {user_input}
                        
                        Check for phishing indicators both in the visual appearance and the text content.
                        """
                    else:
                        prompt = f"""
                        Analyze this image for potential phishing indicators.
                        
                        User question: {user_input}
                        
                        Look for visual signs of phishing like fake logos, unprofessional design, 
                        mismatched URLs, unusual requests, or anything suspicious.
                        """
                    
                    # Prepare request data
                    data = {
                        "model": "llava:latest",
                        "prompt": prompt,
                        "images": [image_base64],
                    }
                    
                    # Process the response
                    with st.chat_message("assistant", avatar="🧠"):
                        with st.spinner("Analyzing..."):
                            response = requests.post(API_URL, json=data, headers=headers)
                        
                        if response.status_code == 200:
                            response_lines = response.text.split("\n")
                            llava_response = ""
                            
                            for line in response_lines:
                                if line.strip():  # Skip empty lines
                                    try:
                                        response_data = json.loads(line)
                                        if "response" in response_data:
                                            llava_response += response_data["response"]
                                    except json.JSONDecodeError:
                                        pass  # Skip invalid JSON lines
                            
                            if llava_response:
                                st.markdown(llava_response)
                                st.session_state.chats.append({"role": "assistant", "content": llava_response})
                            else:
                                st.error("No response received from the model.")
                        else:
                            st.error(f"Failed to get a response from the model. Status code: {response.status_code}")
        else:
            # Display placeholder when no file is uploaded
            with chat_container:
                st.info("Upload an image or PDF to start the analysis.")

    # Document display column
    with col2:
        st.markdown("### Document Preview")
        preview_container = st.container(height=600, border=True)
        
        with preview_container:
            if uploaded_file is not None:
                if st.session_state.document_type == "pdf":
                    # Display PDF previews
                    st.markdown("#### PDF Preview")
                    
                    # Get fresh previews of PDF pages
                    uploaded_file.seek(0)  # Reset file pointer
                    pdf_previews = get_pdf_images(uploaded_file)
                    
                    # Show page previews
                    for i, img in enumerate(pdf_previews):
                        st.markdown(f"##### Page {i+1}")
                        st.image(img, use_container_width=True)
                        st.markdown("---")
                else:
                    # Display image
                    st.image(uploaded_file, caption="Uploaded image", use_container_width=True)
                    
                    # Add some helpful tips for analysis
                    with st.expander("📝 Tips for Phishing Detection"):
                        st.markdown("""
                        **Look for these common phishing indicators:**
                        
                        - Suspicious sender addresses
                        - Mismatched or fake URLs
                        - Poor grammar or spelling
                        - Generic greetings
                        - Urgent calls to action
                        - Requests for sensitive information
                        - Unprofessional design
                        - Unusual attachments
                        """)
            else:
                # Display placeholder
                st.markdown(
                    """
                    <div class="upload-area">
                        <h4>📤 No document uploaded</h4>
                        <p>Upload an image or PDF to see it displayed here</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                st.info("""
                **This tool helps you analyze:**
                
                - Suspicious emails (screenshots or PDFs)
                - Potential phishing websites
                - QR codes that might lead to malicious sites
                - Documents with social engineering elements
                
                Upload a document to begin your analysis.
                """)

if __name__ == "__main__":
    main()