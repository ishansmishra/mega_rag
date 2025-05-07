import os
import uuid
import time
import threading
import logging

import fitz  # PyMuPDF
import gradio as gr
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
import llm

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_KEY = os.getenv("QDRANT_KEY")

# Configure Gemini
genai.configure(api_key=GOOGLE_KEY)

# Constants
CHUNK_SIZE = 300
TOP_K = 5
QUERY_TIMEOUT = 30  # seconds

# Qdrant client
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_KEY)

# Global session ID
session_id = None

# Utilities
def parse_pdf(file_path: str) -> str:
    """Extracts text from a PDF."""
    try:
        with fitz.open(file_path) as doc:
            return "\n".join(page.get_text() for page in doc)
    except Exception as e:
        logging.error(f"Failed to parse PDF: {e}")
        raise

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list:
    """Splits text into chunks."""
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

def embed(text: str) -> list:
    """Generates embedding vector from text."""
    try:
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_query"
        )
        return result["embedding"]
    except Exception as e:
        logging.error(f"Embedding failed: {e}")
        raise

# Core Functions
def upload_pdf(file_obj):
    global session_id

    if file_obj is None:
        return "⚠️ Please upload a PDF file."

    session_id = f"session_{uuid.uuid4().hex[:8]}"
    filename = os.path.basename(file_obj.name)

    try:
        text = parse_pdf(file_obj.name)
        chunks = chunk_text(text)

        sample_vector = embed(chunks[0])
        qdrant.create_collection(
            collection_name=session_id,
            vectors_config=models.VectorParams(size=len(sample_vector), distance=models.Distance.COSINE)
        )

        points = []
        for i, chunk in enumerate(chunks):
            try:
                vector = embed(chunk)
                points.append(models.PointStruct(
                    id=i,
                    vector=vector,
                    payload={"text": chunk, "chunk_id": i, "filename": filename}
                ))
            except Exception as e:
                logging.warning(f"Chunk {i} embedding failed: {e}")

        qdrant.upsert(collection_name=session_id, points=points)

        return f"✅ PDF processed and indexed in {len(points)} chunks.\nSession ID: {session_id}"

    except Exception as e:
        logging.error(f"Upload processing failed: {e}")
        return f"❌ Failed to process PDF: {str(e)}"

def answer_query(question: str):
    if not session_id:
        return "⚠️ Please upload a PDF first."

    result_container = {'success': False, 'response': None, 'error': None}

    def process_query():
        try:
            result_container['response'] = llm.answer_query(question, session_id)
            result_container['success'] = True
        except Exception as e:
            logging.error(f"Query processing error: {e}", exc_info=True)
            result_container['error'] = str(e)

    thread = threading.Thread(target=process_query, daemon=True)
    thread.start()

    start_time = time.time()
    while thread.is_alive():
        if time.time() - start_time > QUERY_TIMEOUT:
            return "⚠️ Query timed out. Please simplify your question or try again."
        time.sleep(0.1)

    return result_container['response'] if result_container['success'] else f"❌ Error: {result_container['error']}"

# Gradio UI
def create_ui():
    with gr.Blocks(title="PDF Question Answering App") as demo:
        with gr.Row():
            pdf_input = gr.File(label="Upload PDF", type="file")
            upload_btn = gr.Button("Process PDF")
        upload_output = gr.Textbox(label="Upload Result", lines=2)

        with gr.Row():
            query_input = gr.Textbox(label="Ask a question about the PDF", lines=1, placeholder="Type your question...")
            query_btn = gr.Button("Ask")
        query_output = gr.Textbox(label="Answer", lines=10)

        upload_btn.click(fn=upload_pdf, inputs=pdf_input, outputs=upload_output)
        query_btn.click(fn=answer_query, inputs=query_input, outputs=query_output)

    return demo

# Launch
if __name__ == "__main__":
    ui = create_ui()
    ui.launch()