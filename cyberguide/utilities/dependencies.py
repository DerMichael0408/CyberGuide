import importlib
import streamlit as st

def check_dependencies():
    """
    Check if required dependencies are installed.
    
    Returns:
        dict: A dictionary containing the status of each dependency.
    """
    dependencies = {
        'chromadb': False,
        'sentence_transformers': False,
        'langchain_chroma': False,
        'fitz': False  # PyMuPDF
    }
    
    for package in dependencies.keys():
        try:
            importlib.import_module(package)
            dependencies[package] = True
        except ImportError:
            dependencies[package] = False
    
    return dependencies

def display_dependency_warnings():
    """
    Display warnings for missing dependencies.
    """
    deps = check_dependencies()
    missing = [dep for dep, installed in deps.items() if not installed]
    
    if missing:
        install_commands = {
            'chromadb': 'pip install chromadb',
            'sentence_transformers': 'pip install sentence_transformers',
            'langchain_chroma': 'pip install langchain-chroma',
            'fitz': 'pip install pymupdf'  # The package name is pymupdf but it's imported as fitz
        }
        
        packages_info = []
        for pkg in missing:
            if pkg == 'fitz':
                packages_info.append(f"{pkg} (install with `{install_commands[pkg]}`)")
            else:
                packages_info.append(pkg)
                
        st.warning(
            f"⚠️ The following packages are required but are not installed: {', '.join(packages_info)}. " +
            "Some features may not be available.\n\n" +
            "To install all required packages, run:\n" +
            "```\npip install chromadb sentence_transformers langchain-chroma pymupdf\n```",
            icon="⚠️"
        )

def safe_import(module_name):
    """
    Safely import a module, returning None if it fails.
    
    Args:
        module_name (str): The name of the module to import.
        
    Returns:
        module or None: The imported module or None if import fails.
    """
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None 