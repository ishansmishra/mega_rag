---
title: Mega RAG
emoji: 🧠
colorFrom: indigo
colorTo: pink
sdk: gradio
sdk_version: 5.29.0
app_file: app.py
pinned: false
---
# 📄 PDF Question Answering App

An interactive Gradio-powered web application that allows users to upload PDF documents, index them using vector embeddings, and ask natural language questions based on the content. The system uses **Google Gemini** for embeddings and response generation, and **Qdrant** as a vector database for efficient retrieval.

---

## 🚀 Features

- 📤 **Upload and Parse PDFs** – Extract text from uploaded PDF files.
- ✂️ **Chunking** – Split long documents into manageable text chunks.
- 🔍 **Vector Embedding** – Use Google's Gemini embedding model to convert text to vectors.
- 🧠 **Semantic Search with Qdrant** – Store and retrieve document chunks based on similarity to user queries.
- 🤖 **Answer Generation** – Use Gemini to generate answers using only the retrieved context.

---

## 🛠️ Tech Stack

- **Frontend**: [Gradio](https://www.gradio.app/)
- **Backend**: Python, [PyMuPDF](https://pymupdf.readthedocs.io/), [Qdrant](https://qdrant.tech/)
- **LLM & Embeddings**: [Google Generative AI](https://ai.google/discover/generative-ai/)
- **Vector Store**: Qdrant
- **Environment Management**: `python-dotenv`

---

## 📦 Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/pdf-qa-app.git
   cd pdf-qa-app
   ```

2. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**  
   Create a `.env` file in the root directory:
   ```
   GOOGLE_KEY=your_google_api_key
   QDRANT_URL=http://localhost:6333  # or your Qdrant Cloud URL
   QDRANT_KEY=your_qdrant_api_key
   ```

4. **Run the application**  
   ```bash
   python app.py
   ```

---

## 📁 Project Structure

```
.
├── app.py           # Gradio app and Qdrant embedding pipeline
├── llm.py           # Gemini-based query answering logic
├── .env             # Environment variables (not included in repo)
├── requirements.txt # Python dependencies
```

---

## 🧪 Example Workflow

1. Upload a PDF.
2. The app extracts and chunks the text.
3. Each chunk is embedded and stored in Qdrant.
4. Ask a question about the document.
5. The system retrieves relevant chunks and uses Gemini to answer your question.

---

## ❗ Notes

- Ensure your Qdrant instance is running and accessible.
- The app uses `threading` with a timeout to handle slow LLM queries gracefully.

---

## 📌 Future Improvements

- Support for multiple concurrent sessions.
- Optional summarization of uploaded PDFs.
- Add UI progress indicators during processing.

---

## 📃 License

MIT License.


---

## 🔧 Architectural Decisions & Rationale

###  1. Use of google.generativeai for Embeddings & Responses

    Why? To streamline the stack by using the same provider (Gemini) for both:

        Text embedding (via embed_content)

        Response generation (via generate_content)

    Benefit: Consistent vector semantics and compatibility between retrieval and generation. Also, google gives 300 usd credits

### 2. Use of Qdrant for Vector Search

    Why?

        High performance and low-latency similarity search.

        Native support for vector and metadata filtering.

        Scalable and easy to run locally or on the cloud.

    Alternative Considered: FAISS (faster for local, but lacks native REST API and cloud support).

### 3. Chunking PDF Content

    Why? LLMs and vector databases work best with small, semantically meaningful chunks.

    Decision: Used fixed word-based chunking (CHUNK_SIZE = 300) for simplicity.

    Improvement Potential: Sliding window + sentence boundary detection for smarter chunking.

### 4. Multithreading for Query Processing

    Why? LLM queries can be slow or hang due to API latency.

    Implementation: Query thread is run with a timeout of QUERY_TIMEOUT = 30 seconds.

    Benefit: Ensures the UI doesn't freeze, and provides helpful feedback to the user if something fails.

### 6. Use of Gradio

    Why? Quick to prototype and deploy ML-powered interfaces.

    Alternative Considered: Streamlit (great too, but Gradio has better input/output granularity for simple UIs).

    Benefit: Zero setup UI, supports file upload and interaction with minimal code. Easier to integrate with huggingface spaces

### 7. Session ID Strategy

    Why? Each PDF is stored in its own Qdrant collection (session_{uuid}) to avoid cross-document mixing.

    Future Potential: Add support for multiple simultaneous documents per user, or persistent storage for reuse.
---

## ✅ Architecture Flow (Step-by-Step)

User Uploads PDF

    Gradio UI receives the PDF file.

    File is passed to upload_pdf() function in app.py.

PDF Parsing

    parse_pdf() extracts raw text from all pages using PyMuPDF (fitz).

Text Chunking

    chunk_text() splits the entire PDF text into chunks of ~300 words each.

Text Embedding

    Each chunk is converted into a vector using genai.embed_content() (Gemini embeddings).

Qdrant Collection Initialization

    A new collection is created in Qdrant named after a UUID-based session_id.

    models.VectorParams defines vector size and similarity metric (Cosine).

Vector Storage

    All chunks + metadata (text, chunk_id, filename) are stored in Qdrant as points.

User Submits a Question

    Gradio UI sends the question to answer_query().

Query Embedding & Retrieval

    Inside llm.py, the question is embedded using genai.embed_content().

    Qdrant is queried for the top-5 most similar chunks using the query vector.

Prompt Construction

    The retrieved chunks are compiled into a prompt context.

    A structured prompt is created with instructions and the context.

LLM Answer Generation

    genai.GenerativeModel().generate_content() generates a response based only on retrieved chunks.

Response Display

    Final answer is shown in the Gradio UI.