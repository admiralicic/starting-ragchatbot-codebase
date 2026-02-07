# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Retrieval-Augmented Generation (RAG) chatbot system for querying course materials. The system uses ChromaDB for vector storage, Anthropic's Claude API for AI generation, and provides a full-stack web interface.

**Tech Stack:**
- Backend: Python 3.13, FastAPI, ChromaDB, Sentence Transformers
- Frontend: Vanilla JavaScript, HTML, CSS
- Package Manager: `uv` (required)
- AI: Anthropic Claude API with tool calling

## Important: Dependency Management

**Always use `uv` to manage dependencies and run Python files - never use `pip` or `python` directly.**

This project uses `uv` for fast, reliable dependency management. All Python commands must be run through `uv`:
- ✅ `uv sync` - Install/update dependencies
- ✅ `uv run python script.py` - Run Python scripts/files
- ✅ `uv run uvicorn app:app` - Run the server
- ✅ `uv add package-name` - Add new dependencies
- ❌ `pip install` - Do not use
- ❌ `python script.py` - Do not use directly (always use `uv run python`)

## Development Commands

### Setup
```bash
# Install dependencies
uv sync

# Create .env file with your API key
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your-key-here
```

### Running the Application
```bash
# Start the server (from project root)
./run.sh

# Or manually from backend directory
cd backend
uv run uvicorn app:app --reload --port 8000
```

The application serves at `http://localhost:8000` with API docs at `http://localhost:8000/docs`.

### Development
```bash
# Run Python with dependencies
uv run python script.py

# Add new dependencies (updates pyproject.toml and uv.lock)
uv add package-name

# Remove dependencies
uv remove package-name

# Access Python REPL with project dependencies
cd backend
uv run python
```

**Note:** Always prefix Python commands with `uv run` to ensure they use the project's dependencies.

## Architecture Overview

### Request Flow (Tool-Based RAG)

The system uses **Anthropic's tool calling** to intelligently decide when to search course content:

1. **Frontend** (`frontend/script.js`) → POST `/api/query` with `{query, session_id}`
2. **FastAPI** (`backend/app.py`) → Routes to `rag_system.query()`
3. **RAG System** (`backend/rag_system.py`) → Orchestrates the flow:
   - Retrieves conversation history from `SessionManager`
   - Passes query + tool definitions to `AIGenerator`
4. **AI Generator** (`backend/ai_generator.py`) → **2-step Claude API interaction**:
   - **Call #1**: Claude decides whether to use `search_course_content` tool
   - If tool used: Executes search via `ToolManager`
   - **Call #2**: Claude synthesizes search results into final answer
5. **Tool Execution** (`backend/search_tools.py`):
   - `CourseSearchTool` calls `VectorStore.search()`
   - Returns formatted results with source tracking
6. **Vector Store** (`backend/vector_store.py`) → ChromaDB operations:
   - Resolves course names via semantic search in `course_catalog` collection
   - Queries `course_content` collection with filters
   - Returns top 5 chunks (configurable in `config.py`)
7. **Response**: Answer + sources → JSON → Frontend renders with markdown

### Core Components

**Two-Collection Vector Store Design:**
- `course_catalog`: Course metadata (titles, instructors, lessons) for semantic course name resolution
- `course_content`: Text chunks (800 chars, 100 char overlap) with metadata for retrieval

**Document Processing Pipeline** (`backend/document_processor.py`):
- Parses structured course documents (title, instructor, lessons)
- Sentence-based chunking with overlap to preserve context
- Enriches chunks with metadata: `"Course {title} Lesson {N} content: {text}"`

**Session Management** (`backend/session_manager.py`):
- Maintains last 2 conversation exchanges (4 messages) per session
- History injected into Claude's system prompt for context-aware responses

**Configuration** (`backend/config.py`):
- `CHUNK_SIZE`: 800 chars
- `CHUNK_OVERLAP`: 100 chars
- `MAX_RESULTS`: 5 search results
- `MAX_HISTORY`: 2 exchanges
- `EMBEDDING_MODEL`: "all-MiniLM-L6-v2"
- `ANTHROPIC_MODEL`: "claude-sonnet-4-20250514"

### Data Models (`backend/models.py`)

- `Course`: Represents full course with lessons list
- `Lesson`: Individual lesson metadata (number, title, link)
- `CourseChunk`: Text chunk with course/lesson metadata for vector storage

### Course Document Format

Files in `docs/` follow this structure:
```
Course Title: [Title]
Course Link: [URL]
Course Instructor: [Name]

Lesson 0: [Title]
Lesson Link: [URL]
[Content...]

Lesson 1: [Title]
...
```

## Key Implementation Details

### Adding New Documents
On startup (`app.py:88-98`), the system automatically loads documents from `../docs/` and avoids re-processing existing courses (checks by course title).

### Tool Calling Pattern
The `search_course_content` tool supports:
- `query`: Required search text
- `course_name`: Optional, uses fuzzy matching via vector search
- `lesson_number`: Optional filter

### Source Attribution
Search results track sources (`search_tools.py:103-112`) which are displayed in the frontend's collapsible "Sources" section.

### ChromaDB Persistence
The vector database persists at `backend/chroma_db/` (gitignored). Delete this directory to force re-indexing.

### AI System Prompt
Located in `ai_generator.py:8-30`. Instructs Claude to:
- Use search tool only for course-specific questions (max 1 search per query)
- Answer general questions without searching
- Provide brief, concise, educational responses
- Avoid meta-commentary about search process

## Configuration Notes

- **Temperature**: Set to 0 for deterministic responses
- **Max tokens**: 800 (adjust in `ai_generator.py:40` if responses are truncated)
- **Embedding model**: Fast, lightweight model suitable for educational content
- **Session limit**: Prevents unbounded context growth while maintaining conversation continuity

## Environment Variables

Required in `.env`:
- `ANTHROPIC_API_KEY`: Your Anthropic API key (required)

## Working with ChromaDB

The vector store is automatically initialized and populated on first run. To reset:
```bash
# Delete the database
rm -rf backend/chroma_db

# Restart the server - will re-index docs/ on startup
./run.sh
```

## Frontend Integration

The frontend (`frontend/`) is served as static files by FastAPI. The API uses `/api` prefix for all endpoints:
- `POST /api/query`: Main chat endpoint
- `GET /api/courses`: Course statistics

Markdown rendering uses `marked.js` library (loaded via CDN in `index.html`).
