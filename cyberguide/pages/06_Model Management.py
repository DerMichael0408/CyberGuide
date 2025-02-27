import streamlit as st
import subprocess
import time
import os
import re
from utilities.icon import page_icon

# Page configuration
st.set_page_config(
    page_title="Model Management",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .model-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 3px solid #FF4B4B;
        min-height: 150px;
    }
    .badge {
        display: inline-block;
        padding: 2px 6px;
        border-radius: 8px;
        font-size: 11px;
        margin-right: 5px;
    }
    .hw-light { background-color: #90EE90; }
    .hw-medium { background-color: #FFD700; }
    .hw-heavy { background-color: #FFA07A; }
    
    /* Custom progress bar styling with red fill */
    .stProgress > div > div > div > div {
        background-color: #FF4B4B !important;
    }
    
    /* Simple download title */
    .download-title {
        font-size: 16px;
        font-weight: 500;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Verified models that exist in Ollama's repository
LOCAL_MODELS = {
    "phi3:mini": {
        "hw": "light", 
        "description": "Small but capable - runs on most hardware",
        "params": "3.8B",
        "ram": "8GB+"
    },
    "mistral:latest": {
        "hw": "medium", 
        "description": "Efficient 7B parameter model with good performance",
        "params": "7B",
        "ram": "12GB+"
    },
    "llama3:8b": {
        "hw": "medium", 
        "description": "Meta's 8B parameter model, good balance",
        "params": "8B",
        "ram": "16GB+"
    },
    "gemma:2b": {
        "hw": "light", 
        "description": "Google's lightweight model - runs on modest hardware",
        "params": "2B",
        "ram": "6GB+"
    },
    "codegemma:2b": {
        "hw": "light", 
        "description": "Google's code-focused model, runs on modest hardware",
        "params": "2B",
        "ram": "6GB+"
    },
    "phi:latest": {
        "hw": "light", 
        "description": "Microsoft's model, efficient for smaller hardware",
        "params": "2.7B",
        "ram": "8GB+"
    }
}

# Model templates for quick start
MODEL_TEMPLATES = {
    "Basic Assistant": """FROM mistral:latest
SYSTEM You are a helpful assistant. Provide clear and concise answers.""",
    "Coding Helper": """FROM codegemma:2b
SYSTEM You are a coding assistant. Help users write clean, efficient code.""",
    "Creative Writer": """FROM llama3:8b
SYSTEM You are a creative writing assistant. Help users craft engaging content."""
}

def get_hw_badge(hw_level):
    """Returns HTML for a hardware requirement badge"""
    if hw_level == "light":
        return '<span class="badge hw-light">Light</span>'
    elif hw_level == "medium":
        return '<span class="badge hw-medium">Medium</span>'
    elif hw_level == "heavy":
        return '<span class="badge hw-heavy">Heavy</span>'
    return ''

def get_installed_models():
    """Get installed models using command line"""
    try:
        # Run ollama list command
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode != 0:
            return []
            
        # Parse the output
        models = []
        lines = result.stdout.strip().split('\n')
        
        # Skip header line if it exists
        if lines and 'NAME' in lines[0] and 'ID' in lines[0]:
            lines = lines[1:]
            
        for line in lines:
            if line.strip():
                parts = line.split()
                if parts:
                    models.append({
                        'name': parts[0],
                        'size': parts[1] if len(parts) > 1 else 'Unknown',
                        'modified_at': ' '.join(parts[2:]) if len(parts) > 2 else 'Unknown'
                    })
        
        return models
    except Exception as e:
        st.error(f"Error retrieving models: {str(e)}")
        return []

def extract_progress_info(line):
    """Extract download progress from a line of output"""
    # Clean ANSI escape codes
    clean_line = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', line)
    clean_line = re.sub(r'\[\?25[hl]|\[2K|\[1G|\[A', '', clean_line)
    
    # Try different patterns to match download progress
    
    # Pattern for progress percentage and sizes
    progress_pattern = re.compile(r'(\d+)%.*?(\d+(?:\.\d+)?) ([KMG]B)/(\d+(?:\.\d+)?) ([KMG]B).*?(\d+(?:\.\d+)?) ([KMG]B)/s')
    match = progress_pattern.search(clean_line)
    
    if match:
        percentage = int(match.group(1))
        downloaded = f"{match.group(2)} {match.group(3)}"
        total = f"{match.group(4)} {match.group(5)}"
        speed = f"{match.group(6)} {match.group(7)}/s"
        
        return {
            "percentage": percentage,
            "info": f"{downloaded}/{total} • {speed}",
            "type": "progress"
        }
    
    # Check for manifest or processing messages
    manifest_pattern = re.compile(r'(?:pulling|processing|verifying) ([a-z0-9]+|manifest)')
    match = manifest_pattern.search(clean_line)
    
    if match:
        action = match.group(0)
        return {
            "percentage": None,
            "info": action,
            "type": "status"
        }
    
    # If no pattern matched, return default
    return {
        "percentage": None,
        "info": clean_line if clean_line else "Processing...",
        "type": "unknown"
    }

def download_model_direct(model_name):
    """Ultra-simplified download function with only essential UI elements"""
    # Just show the name of model being downloaded
    st.markdown(f'<div class="download-title">Downloading {model_name}</div>', unsafe_allow_html=True)
    
    # Single progress bar that will show percentage
    progress_bar = st.progress(0)
    
    # Text below progress bar will show size info
    size_info = st.empty()
    
    try:
        # Start the download process
        process = subprocess.Popen(
            ["ollama", "pull", model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        last_percentage = 0
        
        # Process output line by line
        for line in iter(process.stdout.readline, ""):
            # Extract progress info
            info = extract_progress_info(line)
            
            # Update UI based on the type of information
            if info["type"] == "progress" and info["percentage"] is not None:
                # Update progress bar with percentage
                progress_bar.progress(info["percentage"] / 100)
                last_percentage = info["percentage"]
                
                # Update size info
                size_info.write(info["info"])
            elif info["type"] == "status":
                # Just update the size info with status
                size_info.write(info["info"])
                
                # For manifest and other stages, don't reset progress
                if last_percentage > 0:
                    progress_bar.progress(last_percentage / 100)
                
            # Small pause to prevent UI lag
            time.sleep(0.05)
            
        # Wait for process to complete
        return_code = process.wait()
        
        if return_code == 0:
            # Download successful - show just a success message and clean up other elements
            progress_bar.empty()
            size_info.empty()
            st.success(f"✅ {model_name} downloaded successfully!")
            return True
        else:
            # Download failed
            progress_bar.empty()
            size_info.empty()
            st.error(f"❌ Failed to download {model_name}")
            return False
            
    except Exception as e:
        st.error(f"Error downloading {model_name}: {str(e)}")
        return False

def create_model(name, modelfile):
    """Create a model from a modelfile"""
    try:
        # Create a temporary modelfile
        modelfile_path = f"/tmp/modelfile_{name}"
        with open(modelfile_path, "w") as f:
            f.write(modelfile)
        
        # Show a status message
        with st.status(f"Creating model: {name}...", expanded=True) as status:
            # Run command to create the model
            process = subprocess.Popen(
                ["ollama", "create", name, "-f", modelfile_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Show output in real-time
            output_lines = []
            for line in iter(process.stdout.readline, ""):
                clean_line = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', line).strip()
                if clean_line:
                    output_lines.append(clean_line)
                    status.update(label=f"Creating {name}... \n" + "\n".join(output_lines[-5:]))
                    time.sleep(0.1)
            
            # Wait for process to complete
            return_code = process.wait()
            
            # Clean up temp file
            if os.path.exists(modelfile_path):
                os.remove(modelfile_path)
            
            if return_code == 0:
                status.update(label=f"✅ Model '{name}' created successfully!", state="complete")
                st.success(f"Model '{name}' is ready to use!")
                return True
            else:
                status.update(label=f"❌ Failed to create model: {name}", state="error")
                st.error(f"Failed to create model: {name}")
                return False
                
    except Exception as e:
        st.error(f"Error creating model: {str(e)}")
        return False

def delete_model(model_name):
    """Delete a model using command line"""
    try:
        with st.status(f"Deleting {model_name}...", expanded=True) as status:
            process = subprocess.run(
                ["ollama", "rm", model_name],
                capture_output=True,
                text=True
            )
            
            if process.returncode == 0:
                status.update(label=f"✅ Model {model_name} deleted successfully!", state="complete")
                return True
            else:
                status.update(label=f"❌ Failed to delete {model_name}: {process.stderr}", state="error")
                return False
                
    except Exception as e:
        st.error(f"Error deleting model: {str(e)}")
        return False

def main():
    page_icon("⚙️")
    st.title("Model Management", anchor=False)
    
    # Get the list of installed models - refresh this after operations
    installed_models = get_installed_models()
    installed_model_names = [model['name'] for model in installed_models]
    
    # Show installed models summary
    models_summary = st.empty()  # Use empty container for easy updates
    with models_summary.container():
        if installed_models:
            st.write(f"**📚 Installed Models: {len(installed_models)}**")
            model_names = ", ".join([f"`{model['name']}`" for model in installed_models])
            st.markdown(model_names)
        else:
            st.info("No models currently installed. Get started by downloading a model below!", icon="👇")
    
    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["📥 Download Models", "🛠️ Create Models", "🗑️ Manage Models"])
    
    with tab1:
        st.subheader("Download Models for Local Use", anchor=False)
        
        # Show download area - this is where the progress will appear
        download_container = st.container()
        
        with download_container:
            # This space will be filled with progress bars when downloads start
            pass
        
        # Display model grid
        st.write("**🚀 Recommended Models for Local Use**")
        
        # Create model grid - simplified to 2 columns for better display
        cols = st.columns(2)
        
        for i, (model_name, info) in enumerate(LOCAL_MODELS.items()):
            with cols[i % 2]:
                # Display model card
                st.markdown(f'''
                <div class="model-card">
                    <strong>{model_name}</strong> {get_hw_badge(info['hw'])}
                    <p style="font-size: 13px; margin: 4px 0;"><strong>Parameters:</strong> {info['params']} | <strong>RAM:</strong> {info['ram']}</p>
                    <p style="font-size: 13px; margin: 4px 0;">{info['description']}</p>
                </div>
                ''', unsafe_allow_html=True)
                
                # Check if model is already installed
                is_installed = model_name in installed_model_names
                
                # Show appropriate button based on status
                if is_installed:
                    st.button("✅ Installed", key=f"installed_{model_name}", disabled=True, use_container_width=True)
                else:
                    # Download button - when clicked, it will show progress in the download_container
                    if st.button(f"📥 Download", key=f"download_{model_name}", use_container_width=True):
                        # This is where the download happens - DIRECTLY in the UI thread
                        with download_container:
                            if download_model_direct(model_name):
                                # Refresh installed models
                                updated_models = get_installed_models()
                                with models_summary.container():
                                    st.write(f"**📚 Installed Models: {len(updated_models)}**")
                                    model_names = ", ".join([f"`{model['name']}`" for model in updated_models])
                                    st.markdown(model_names)
                                
                                time.sleep(1)
                                st.rerun()
        
        # Custom model download
        st.write("---")
        st.subheader("Custom Download", anchor=False)
        
        custom_model = st.text_input("Enter model name:", placeholder="e.g., phi3:latest")
        
        if st.button("📥 Download Custom Model", key="custom_download"):
            if custom_model:
                with download_container:
                    if download_model_direct(custom_model):
                        # Refresh installed models
                        updated_models = get_installed_models()
                        with models_summary.container():
                            st.write(f"**📚 Installed Models: {len(updated_models)}**")
                            model_names = ", ".join([f"`{model['name']}`" for model in updated_models])
                            st.markdown(model_names)
                        
                        time.sleep(1)
                        st.rerun()
            else:
                st.warning("Please enter a model name", icon="⚠️")
                
        # Add command line help
        with st.expander("ℹ️ Need help with model names?"):
            st.markdown("""
            **Model Naming Format in Ollama:**
            
            Most models follow the format: `name:tag`
            
            **Examples of valid model names:**
            - `mistral:latest` - Latest Mistral model
            - `llama3:8b` - Llama 3 8B parameter model
            - `phi:latest` - Latest Phi model
            - `gemma:2b` - Gemma 2B model
            
            You can also browse available models on the Ollama library:
            [https://ollama.com/library](https://ollama.com/library)
            """)
    
    with tab2:
        st.subheader("Create Custom Models", anchor=False)
        
        # Template selector
        template_choice = st.selectbox(
            "Start with a template:",
            ["-- Select a template --"] + list(MODEL_TEMPLATES.keys())
        )
        
        template_content = ""
        if template_choice in MODEL_TEMPLATES:
            template_content = MODEL_TEMPLATES[template_choice]
        
        # Model name and modelfile in a clean layout
        col1, col2 = st.columns([1, 3])
        
        with col1:
            model_name = st.text_input("Name your model:", placeholder="e.g., my-assistant")
            
            create_btn = st.button("🛠️ Create Model", key="create_btn", use_container_width=True)
            
            with st.expander("📖 Help"):
                st.markdown("""
                **Model Creation Steps:**
                1. Choose a base model
                2. Add a SYSTEM prompt
                3. Name your model
                4. Click Create
                """)
        
        with col2:
            modelfile = st.text_area(
                "Modelfile:",
                value=template_content,
                height=200,
                placeholder="FROM mistral:latest\nSYSTEM You are a specialized assistant..."
            )
            
        if create_btn:
            if model_name and modelfile:
                if create_model(model_name, modelfile):
                    # Update installed models
                    updated_models = get_installed_models()
                    with models_summary.container():
                        st.write(f"**📚 Installed Models: {len(updated_models)}**")
                        model_names = ", ".join([f"`{model['name']}`" for model in updated_models])
                        st.markdown(model_names)
                    
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("Please enter both a model name and modelfile content", icon="⚠️")
    
    with tab3:
        st.subheader("Manage Installed Models", anchor=False)
        
        if installed_models:
            # Show models in a table layout
            for model in installed_models:
                cols = st.columns([4, 1])
                with cols[0]:
                    display_size = model.get('size', 'Unknown')
                        
                    st.markdown(f"""
                    <div style="padding: 8px 0; border-bottom: 1px solid #eee;">
                        <strong>{model['name']}</strong><br>
                        <span style="color: gray; font-size: 13px;">Size: {display_size}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[1]:
                    if st.button("🗑️ Delete", key=f"del_{model['name']}", use_container_width=True):
                        if delete_model(model['name']):
                            # Update installed models
                            updated_models = get_installed_models()
                            with models_summary.container():
                                st.write(f"**📚 Installed Models: {len(updated_models)}**")
                                model_names = ", ".join([f"`{model['name']}`" for model in updated_models])
                                st.markdown(model_names)
                            
                            time.sleep(1)
                            st.rerun()
        else:
            st.info("No models available for deletion.", icon="🦗")

if __name__ == "__main__":
    main()