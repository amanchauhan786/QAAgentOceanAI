import streamlit as st
import os
import json
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
# UPDATED IMPORTS for compatibility
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# --- IMPORT THE RUNNER MODULE ---
from runner import execute_selenium_code

# --- CONFIGURATION ---
st.set_page_config(page_title="Autonomous QA Agent", layout="wide")

# --- SESSION STATE INITIALIZATION ---
if "vector_db" not in st.session_state:
    st.session_state.vector_db = None
if "test_cases" not in st.session_state:
    st.session_state.test_cases = []
if "html_context" not in st.session_state:
    st.session_state.html_context = ""

# --- SIDEBAR: SETUP ---
with st.sidebar:
    st.title("⚙️ Configuration")
    st.info("Step 1: Enter your API Key")
    api_key = st.text_input("Google Gemini API Key", type="password")

    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        genai.configure(api_key=api_key)
        st.success("Authentication Successful")

    st.divider()
    st.markdown("### About")
    st.caption(
        "This agent uses RAG to generate test cases from documentation and writes Selenium scripts automatically.")

# --- MAIN UI ---
st.title("🤖 Autonomous QA Agent")
st.markdown("### Phase 1: Knowledge Base Ingestion")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Support Documents")
    uploaded_files = st.file_uploader(
        "Upload rules (MD, TXT)",
        accept_multiple_files=True,
        type=['md', 'txt', 'json']
    )

with col2:
    st.subheader("2. Target HTML")
    # Option to upload or paste HTML
    html_input_method = st.radio("Input Method", ["Upload File", "Paste Code"])
    html_content = ""

    if html_input_method == "Upload File":
        html_file = st.file_uploader("Upload checkout.html", type=['html'])
        if html_file:
            html_content = html_file.read().decode("utf-8")
    else:
        html_content = st.text_area("Paste HTML here", height=200)

# --- LOGIC: BUILD KNOWLEDGE BASE ---
if st.button("Build Knowledge Base", type="primary"):
    if not api_key:
        st.error("Please enter your API Key in the sidebar first.")
    elif not uploaded_files:
        st.error("Please upload at least one support document.")
    elif not html_content:
        st.error("Please provide the Target HTML.")
    else:
        with st.spinner("Parsing documents and creating embeddings..."):
            try:
                # 1. Process Text Files
                docs = []
                for file in uploaded_files:
                    text = file.read().decode("utf-8")
                    docs.append(Document(page_content=text, metadata={"source": file.name}))

                # 2. Chunking
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
                chunks = text_splitter.split_documents(docs)

                # 3. Embeddings (Using HuggingFace - Local & Stable)
                embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

                # 4. Vector Store
                st.session_state.vector_db = FAISS.from_documents(chunks, embeddings)
                st.session_state.html_context = html_content

                st.success(f"✅ Knowledge Base Built! Processed {len(chunks)} chunks from {len(uploaded_files)} files.")
            except Exception as e:
                st.error(f"Error building Knowledge Base: {e}")

st.divider()

# --- PHASE 2: TEST CASE GENERATION AGENT ---
st.markdown("### Phase 2: Test Case Generation Agent")

# Example prompt for the user
default_prompt = "Generate positive and negative test cases for the Discount Code feature."
user_query = st.text_input("Agent Instruction:", value=default_prompt)

if st.button("Generate Test Cases"):
    if not st.session_state.vector_db:
        st.error("⚠️ Knowledge Base not found. Please complete Phase 1.")
    else:
        with st.spinner("🔍 Retrieving rules & generating test plan..."):
            try:
                # 1. RAG Retrieval
                retriever = st.session_state.vector_db.as_retriever(search_kwargs={"k": 3})
                relevant_docs = retriever.invoke(user_query)
                context_text = "\n\n".join(
                    [f"[Source: {d.metadata.get('source', 'doc')}]: {d.page_content}" for d in relevant_docs])

                # 2. LLM Prompting
                # Corrected model name to ensure it works
                model = genai.GenerativeModel('gemini-2.5-flash')

                prompt = f"""
                You are a Senior QA Automation Engineer.
                Generate a structured test plan based **strictly** on the provided Documentation Context and HTML.

                ---
                DOCUMENTATION CONTEXT:
                {context_text}
                ---
                TARGET HTML STRUCTURE:
                {st.session_state.html_context[:1500]} 
                ---
                USER REQUEST: {user_query}
                ---

                INSTRUCTIONS:
                1. Create comprehensive test cases (Positive & Negative).
                2. Use 'Test_ID' like TC-001, TC-002.
                3. 'Grounded_In' must reference the specific source file provided in context.
                4. Output strictly valid JSON list format. No Markdown blocks.

                JSON SCHEMA:
                [
                    {{
                        "Test_ID": "TC-001",
                        "Feature": "Discount Code",
                        "Test_Scenario": "Enter valid code 'SAVE20'",
                        "Expected_Result": "Total reduces by 20%",
                        "Grounded_In": "product_specs.md"
                    }}
                ]
                """

                response = model.generate_content(prompt)

                # 3. Parsing
                clean_json = response.text.replace("```json", "").replace("```", "").strip()
                test_cases = json.loads(clean_json)

                st.session_state.test_cases = test_cases
                st.success(f"Generated {len(test_cases)} test cases.")

            except Exception as e:
                st.error(f"Agent Error: {e}")

# Display Results
if st.session_state.test_cases:
    st.table(st.session_state.test_cases)

    # --- PHASE 3: SELENIUM SCRIPT AGENT ---
    st.divider()
    st.markdown("### Phase 3: Selenium Script Generation")

    # Dropdown to select test case
    tc_options = [f"{tc['Test_ID']}: {tc['Test_Scenario']}" for tc in st.session_state.test_cases]
    selected_option = st.selectbox("Select a Test Case to Automate:", tc_options)

    if st.button("Generate Selenium Script"):
        # Find the full object
        selected_index = tc_options.index(selected_option)
        selected_case = st.session_state.test_cases[selected_index]

        with st.spinner("💻 Writing Python Selenium Code..."):
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')

                script_prompt = f"""
                You are a Python Selenium Expert.
                Write a complete, runnable Python script for the following test case.

                TEST CASE:
                {json.dumps(selected_case)}

                TARGET HTML:
                {st.session_state.html_context}

                STRICT REQUIREMENTS:
                1. Use `webdriver.Chrome()`.
                2. Initialize the driver normally (NOT headless) and maximize the window.
                3. Add `import time` at the top.
                4. Add `time.sleep(2)` immediately after `driver.get()`.  <-- ADD THIS
                5. Add `time.sleep(1)` BEFORE every `.click()` or `.send_keys()` action. <-- ADD THIS
                6. Use exact ID/Class selectors found in the HTML.
                7. Include assertions to verify the `Expected_Result`.
                8. Return ONLY the Python code (no markdown formatting).
                """

                resp = model.generate_content(script_prompt)
                code = resp.text.replace("```python", "").replace("```", "").strip()

                # Save to session state
                st.session_state.generated_code = code
                st.success("Script Generated Successfully!")

            except Exception as e:
                st.error(f"Script Generation Error: {e}")

    # --- EXECUTION SECTION ---
    if "generated_code" in st.session_state:
        st.subheader("Generated Python Script")
        st.code(st.session_state.generated_code, language="python")

        st.markdown("---")
        st.subheader("🚀 Execute Test")

        if st.button("Run Simulation Now"):
            with st.spinner("Running Selenium Test..."):
                # Call the runner function
                result = execute_selenium_code(st.session_state.generated_code)

                if result["success"]:
                    st.success("✅ Test Passed Successfully!")
                    with st.expander("View Console Logs", expanded=True):
                        st.text(result["output"])
                else:
                    st.error("❌ Test Failed")
                    with st.expander("View Error Logs", expanded=True):
                        st.text(result["error"])
                        st.text(result["output"])