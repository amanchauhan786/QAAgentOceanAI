# 🤖 Autonomous QA Agent   
### For Test Case and Selenium Script Generation
[live demo](https://oceanai.streamlit.app/)
## 📋 Project Objective
This project is an intelligent **Autonomous QA Agent** designed to construct a "testing brain" from project documentation. By ingesting product specifications, UI/UX guides, and target HTML structures, the system automatically:
1.  **Generates Test Cases:** Creates comprehensive test plans grounded in documentation using RAG (Retrieval-Augmented Generation).
2.  **Generates Selenium Scripts:** Converts test cases into executable Python Selenium scripts.
3.  **Executes Tests:** Verifies the logic via a visual browser simulation.

[cite_start]**Built for:** Assignment: Development of an Autonomous QA Agent [cite: 1-2].

---

## 🏗️ Architecture & Tech Stack
[cite_start]The system is built using a **Client-Server Architecture** to satisfy the assignment requirement for a FastAPI backend and Streamlit UI[cite: 9].

* **Frontend:** [Streamlit](https://streamlit.io/) - Handles UI, file uploads, and LLM interaction.
* **Backend:** [FastAPI](https://fastapi.tiangolo.com/) - Securely handles the execution of generated Python scripts.
* **AI/LLM:** [Google Gemini](https://ai.google.dev/) (via `langchain-google-genai`) - Model: `gemini-1.5-flash-001`.
* **Vector DB:** [FAISS](https://github.com/facebookresearch/faiss) - Stores document embeddings for RAG.
* **Automation:** [Selenium](https://www.selenium.dev/) - Web browser automation for testing.

---

## 📂 Project Structure
```text
QA_Agent_Project/
│
├── app.py               # Main Streamlit Frontend Application
├── backend.py           # FastAPI Backend for Script Execution
├── requirements.txt     # Python Dependencies
├── README.md            # Project Documentation
│
└── assets/              # Project Assets (Target & Docs)
    ├── checkout.html    # The target web application to test
    ├── product_specs.md # Business rules (Discounts, Shipping)
    └── ui_ux_guide.txt  # Design rules (Colors, Error messages)

