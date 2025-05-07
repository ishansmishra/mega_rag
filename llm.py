# llm.py
import os
import logging
import traceback
from dotenv import load_dotenv
import google.generativeai as genai
from qdrant_client import QdrantClient

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load and validate environment variables
load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_KEY = os.getenv("QDRANT_KEY")

if not all([GOOGLE_KEY, QDRANT_URL, QDRANT_KEY]):
    raise EnvironmentError("Missing required environment variables.")

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_KEY)

# Initialize Qdrant client
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_KEY)


def retrieve_context(question: str, collection: str, top_k: int = 5) -> str:
    """
    Retrieves the top_k most relevant text chunks from Qdrant for a given question.
    """
    try:
        # Embed the query
        embed_result = genai.embed_content(
            model="models/embedding-001",
            content=question,
            task_type="retrieval_query"
        )
        query_vector = embed_result["embedding"]

        # Search Qdrant
        search_results = qdrant_client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=top_k
        )

        # Gather relevant passages
        contexts = [result.payload.get("text", "") for result in search_results]
        return "\n\n".join(contexts)

    except Exception as e:
        logging.error(f"Error retrieving context: {traceback.format_exc()}")
        raise RuntimeError(f"Failed to retrieve relevant information: {str(e)}")


def answer_query(question: str, collection: str) -> str:
    """
    Answers a question using context retrieved from the specified Qdrant collection.
    """
    try:
        # Get context
        context = retrieve_context(question, collection)

        # Construct prompt
        prompt = f"""You are a helpful AI assistant answering questions based on a provided PDF document.

Question: {question}

Here are relevant passages from the document:
{context}

Based only on the information above, answer the question. 
If the answer is not explicitly present, respond that it cannot be determined from the document.
"""

        # Generate response using Gemini
        model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
        response = model.generate_content(prompt)

        return response.text.strip()

    except Exception as e:
        logging.error(f"Error in answer_query: {traceback.format_exc()}")
        raise RuntimeError(f"Query processing error: {str(e)}")
