
# ✅ TODO List for Agentic RAG with Uploads

## 🔧 1. Project Setup
- [✅] Create a Python virtual environment
- [✅] Install base dependencies:  
  `gradio`, `qdrant-client`, `sentence-transformers`, `PyMuPDF`, `agno/phidata`, `openai`, `tqdm`
- [ ] Set up `app.py` for Gradio interface
- [✅] Set up `.env` file for API keys (OpenAI, Bing, etc.)

## 📁 2. Document Upload + Ingestion
- [ ] Add Gradio file uploader component
- [ ] Write document parser (`PDF`, `TXT`, `DOCX`)
- [ ] Chunk extracted text (e.g., 200–500 tokens per chunk)
- [ ] Embed chunks using sentence-transformers or OpenAI API
- [ ] Store embeddings in **Qdrant**, per session or user (e.g., `session_xyz123`)

## 🔍 3. Query Processing
- [ ] Add text input to UI for user question
- [ ] Embed the user query
- [ ] Search Qdrant (limit to current user’s collection)
- [ ] Retrieve top-k chunks and pass to agent context

## 🧠 4. Agent Team Logic (Agno/Phidata)
- [ ] Define individual agents:
  - [ ] RetrievalAgent
  - [ ] SynthesizerAgent
  - [ ] WebSearchAgent
  - [ ] CodeAgent
  - [ ] Safety/GuardrailAgent
- [ ] Implement TeamAgent orchestration logic
- [ ] Integrate with tools: web search, calculator, code exec
- [ ] Return answer (and optionally reasoning trace)

## 🧪 5. Testing
- [ ] Upload different file types (legal doc, research paper, etc.)
- [ ] Ask queries with and without answers in document
- [ ] Test fallback to tool use (web/code) when doc fails
- [ ] Handle errors gracefully (file parse failures, API issues)

## 🌐 6. Deployment
- [ ] Add `requirements.txt`
- [ ] Clean up UI (loading spinner, error messages)
- [ ] Deploy on **Hugging Face Spaces**, **Render**, or **Railway**
- [ ] Implement 24h cleanup for Qdrant collections

## 🔐 7. Security & UX
- [ ] Limit upload size and file types
- [ ] Sanitize inputs
- [ ] Optional: Add feedback form or chat history
- [ ] Optional: Rate-limiting or login for heavy use
