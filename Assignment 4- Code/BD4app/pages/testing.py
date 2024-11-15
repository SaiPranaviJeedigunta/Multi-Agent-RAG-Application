import streamlit as st
from utils.api_client import fetch_documents, conduct_research
import logging
from urllib.parse import quote
 
logger = logging.getLogger(__name__)
 
def render():
    # Page title and subtitle
    st.title("🔍 Document Analysis & Testing Tool")
    st.subheader("Select a document to analyze and ask questions")
 
    # Step 1: Fetch available documents from the backend
    documents = fetch_documents()
 
    # Check if documents is a string (error message) or empty
    if isinstance(documents, str):
        st.error(f"Error loading documents: {documents}")
        return
    elif not documents:
        st.warning("No documents available.")
        return
 
    # Dropdown to select a document
    selected_doc = st.selectbox(
        "📂 Choose a document:",
        documents,
        format_func=lambda x: x.split('/')[-1].replace('.pdf', '') if isinstance(x, str) else str(x)
    )
 
    # Display the selected document name
    if selected_doc:
        friendly_name = selected_doc.split('/')[-1].replace('.pdf', '')
        st.write(f"**Selected Document**: {friendly_name}")
       
        # Store full path in session state
        if 'current_document' not in st.session_state:
            st.session_state['current_document'] = selected_doc
 
    # Step 2: Initialize session state for storing answers
    if 'answers' not in st.session_state:
        st.session_state['answers'] = [""] * 5
 
    # Allow users to ask up to 5 questions
    for i in range(5):
        st.markdown(f"### Question {i + 1}")
        question = st.text_input(f"❓ Enter your question {i + 1}:", key=f"question_{i}")
 
        # Button to get an answer for each question
        if st.button(f"Get Answer for Question {i + 1}", key=f"button_{i}"):
            if not question:
                st.warning("⚠️ Please enter a question.")
                continue
 
            with st.spinner("Analyzing..."):
                try:
                    # Log the document path before encoding
                    logger.info(f"Selected document before encoding: {selected_doc}")
                   
                    # Conduct research using the backend
                    result = conduct_research(selected_doc, question)
                   
                    if isinstance(result, dict) and 'error' in result:
                        st.error(f"Error: {result['error']}")
                        st.session_state['answers'][i] = f"Error: {result['error']}"
                    elif isinstance(result, dict):
                        analysis = (
                            result.get("result", {}).get("combined_analysis") or
                            result.get("combined_analysis") or
                            "No answer found"
                        )
                        st.session_state['answers'][i] = analysis
                    else:
                        st.error("Unexpected response format")
                        st.session_state['answers'][i] = "Error: Unexpected response format"
 
                except Exception as e:
                    logger.error(f"Error processing question {i+1}: {str(e)}")
                    st.error(f"Error processing question: {str(e)}")
                    st.session_state['answers'][i] = f"Error: {str(e)}"
 
        # Display the answer if available
        if st.session_state['answers'][i]:
            st.write("Answer:")
            st.write(st.session_state['answers'][i])
 
        st.markdown("<hr style='border: 1px solid #4682B4;'>", unsafe_allow_html=True)
 
    # Add debug information (can be removed in production)
    if st.checkbox("Show Debug Info"):
        st.write("Current Document Path:", selected_doc)
        st.write("Encoded Document Path:", quote(selected_doc, safe='') if selected_doc else None)
        st.write("Session State:", st.session_state)
 
# Entry point for the page
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    render()
 