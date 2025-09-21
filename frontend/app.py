import streamlit as st
import requests

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:8000"

# --- UI Layout ---
st.set_page_config(page_title="Smart Doc Checker", layout="wide")
st.title("📄 Smart Doc Checker Agent")
st.markdown("Upload 2 or 3 documents (.txt, .md) to find contradictions.")

# --- File Uploader and Analysis ---
uploaded_files = st.file_uploader(
    "Choose your documents",
    accept_multiple_files=True,
    type=['txt', 'md']
)

if st.button("Analyze Documents", disabled=(not uploaded_files)):
    if not (2 <= len(uploaded_files) <= 3):
        st.error("Please upload 2 or 3 files.")
    else:
        with st.spinner("Uploading and analyzing..."):
            files_to_upload = [('files', (file.name, file.getvalue(), file.type)) for file in uploaded_files]
            
            try:
                # 1. Upload
                upload_response = requests.post(f"{BACKEND_URL}/api/upload", files=files_to_upload)
                upload_response.raise_for_status()
                upload_data = upload_response.json()

                st.sidebar.subheader("Usage Counter")
                st.sidebar.write(f"Documents Checked: **{upload_data['usage']['docs_checked']}**")
                st.sidebar.write(f"Reports Generated: **{upload_data['usage']['reports_generated']}**")

                # 2. Analyze
                analyze_response = requests.post(f"{BACKEND_URL}/api/analyze")
                analyze_response.raise_for_status()
                report = analyze_response.json()

                # 3. Display Report
                st.success("Analysis Complete!")
                st.subheader("📝 Analysis Report")
                st.markdown(f"**Summary:** {report['summary']}")

                if report['contradictions']:
                    st.warning(f"Found {len(report['contradictions'])} contradictions.")
                    for i, item in enumerate(report['contradictions']):
                        with st.expander(f"Conflict #{i+1}: `{item['document_1']}` vs. `{item['document_2']}`"):
                            st.markdown(f"**Explanation:** {item['explanation']}")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.error(f"Text from {item['document_1']}")
                                st.code(item['conflicting_text_1'], language='text')
                            with col2:
                                st.error(f"Text from {item['document_2']}")
                                st.code(item['conflicting_text_2'], language='text')
                            st.info(f"**Suggested Fix:** {item['suggestion']}")
                else:
                    st.success("✅ No contradictions found.")
            
            except requests.exceptions.RequestException as e:
                st.error(f"Error communicating with backend: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

# --- Sidebar Info ---
st.sidebar.title("How it Works")
st.sidebar.info(
    """
    1. **Upload Docs**: Select 2 or 3 files.
    2. **Analyze**: The AI agent finds conflicts.
    3. **Review**: See the report and suggestions.
    """
)
