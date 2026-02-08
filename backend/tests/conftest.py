"""
Shared test fixtures for the RAG system test suite
Provides mocked components and test data for API and integration tests
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import Mock, MagicMock
from fastapi.testclient import TestClient

from config import Config
from vector_store import VectorStore, SearchResults
from ai_generator import AIGenerator
from session_manager import SessionManager
from search_tools import ToolManager, CourseSearchTool, CourseOutlineTool
from rag_system import RAGSystem
from models import Course, Lesson


@pytest.fixture
def test_config():
    """Provide a test configuration"""
    return Config(
        ANTHROPIC_API_KEY="test-key-12345",
        ANTHROPIC_MODEL="claude-sonnet-4-20250514",
        EMBEDDING_MODEL="all-MiniLM-L6-v2",
        CHUNK_SIZE=800,
        CHUNK_OVERLAP=100,
        MAX_RESULTS=5,
        MAX_HISTORY=2,
        MAX_TOOL_ROUNDS=2,
        CHROMA_PATH="./test_chroma_db"
    )


@pytest.fixture
def mock_chroma_client():
    """Provide a mocked ChromaDB client"""
    mock_client = Mock()
    mock_collection = Mock()

    # Default behavior: return empty results
    mock_collection.query.return_value = {
        'documents': [[]],
        'metadatas': [[]],
        'distances': [[]]
    }
    mock_collection.get.return_value = {'ids': []}
    mock_collection.count.return_value = 0

    mock_client.get_or_create_collection.return_value = mock_collection

    return mock_client


@pytest.fixture
def mock_vector_store():
    """Provide a mocked VectorStore with predefined responses"""
    mock_store = Mock(spec=VectorStore)

    # Default search results
    mock_store.search.return_value = SearchResults(
        documents=["Python is a high-level programming language."],
        metadata=[{
            "course_title": "Python Basics",
            "lesson_number": 1,
            "chunk_index": 0
        }],
        distances=[0.3],
        error=None
    )

    mock_store.get_lesson_link.return_value = "https://example.com/lesson1"
    mock_store.get_course_count.return_value = 3
    mock_store.get_existing_course_titles.return_value = [
        "Python Basics",
        "JavaScript Fundamentals",
        "Web Development"
    ]

    return mock_store


@pytest.fixture
def mock_ai_generator():
    """Provide a mocked AIGenerator"""
    mock_gen = Mock(spec=AIGenerator)
    mock_gen.generate_response.return_value = "This is a test response from the AI."
    return mock_gen


@pytest.fixture
def mock_session_manager():
    """Provide a mocked SessionManager"""
    mock_manager = Mock(spec=SessionManager)
    mock_manager.create_session.return_value = "test-session-123"
    mock_manager.get_conversation_history.return_value = "User: Previous question\nAssistant: Previous answer"
    return mock_manager


@pytest.fixture
def mock_tool_manager():
    """Provide a mocked ToolManager with predefined tools"""
    mock_manager = Mock(spec=ToolManager)

    mock_manager.get_tool_definitions.return_value = [
        {
            "name": "search_course_content",
            "description": "Search for content in course materials",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "course_name": {"type": "string", "description": "Optional course name"},
                    "lesson_number": {"type": "integer", "description": "Optional lesson number"}
                },
                "required": ["query"]
            }
        }
    ]

    mock_manager.execute_tool.return_value = "Search results for your query"
    mock_manager.get_last_sources.return_value = [
        {
            "course": "Python Basics",
            "lesson": 1,
            "link": "https://example.com/lesson1"
        }
    ]
    mock_manager.reset_sources.return_value = None

    return mock_manager


@pytest.fixture(autouse=False)
def mock_rag_system(mock_vector_store, mock_ai_generator, mock_session_manager, mock_tool_manager):
    """Provide a mocked RAGSystem with all dependencies mocked"""
    from unittest.mock import MagicMock

    mock_rag = MagicMock(spec=RAGSystem)

    # Assign mocked components
    mock_rag.vector_store = mock_vector_store
    mock_rag.ai_generator = mock_ai_generator
    mock_rag.session_manager = mock_session_manager
    mock_rag.tool_manager = mock_tool_manager

    # Configure query method - use side_effect to create fresh values each call
    def query_side_effect(query_text, session_id=None):
        return (
            "This is a test answer about Python programming.",
            [
                {
                    "course": "Python Basics",
                    "lesson": "1",
                    "link": "https://example.com/lesson1"
                }
            ]
        )

    mock_rag.query.side_effect = query_side_effect

    # Configure analytics method
    mock_rag.get_course_analytics.return_value = {
        "total_courses": 3,
        "course_titles": ["Python Basics", "JavaScript Fundamentals", "Web Development"]
    }

    return mock_rag


@pytest.fixture
def sample_course():
    """Provide a sample Course object for testing"""
    return Course(
        title="Python Basics",
        link="https://example.com/python-basics",
        instructor="John Doe",
        lessons=[
            Lesson(number=0, title="Introduction to Python", link="https://example.com/lesson0"),
            Lesson(number=1, title="Variables and Data Types", link="https://example.com/lesson1"),
            Lesson(number=2, title="Control Flow", link="https://example.com/lesson2")
        ]
    )


@pytest.fixture
def sample_search_results():
    """Provide sample search results for testing"""
    return SearchResults(
        documents=[
            "Python is a high-level programming language.",
            "Variables in Python are dynamically typed.",
            "Python uses indentation to define code blocks."
        ],
        metadata=[
            {"course_title": "Python Basics", "lesson_number": 0, "chunk_index": 0},
            {"course_title": "Python Basics", "lesson_number": 1, "chunk_index": 0},
            {"course_title": "Python Basics", "lesson_number": 2, "chunk_index": 1}
        ],
        distances=[0.2, 0.3, 0.4],
        error=None
    )


@pytest.fixture
def api_test_client(mock_rag_system, test_config):
    """
    Provide a FastAPI TestClient with mocked RAG system
    Creates a test app without static file mounting to avoid import issues
    """
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from typing import List, Optional, Dict

    # Create a test-specific FastAPI app
    test_app = FastAPI(title="Test RAG System")

    # Add CORS middleware
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Pydantic models (same as main app)
    class QueryRequest(BaseModel):
        query: str
        session_id: Optional[str] = None

    class QueryResponse(BaseModel):
        answer: str
        sources: List[Dict[str, Optional[str]]]
        session_id: str

    class CourseStats(BaseModel):
        total_courses: int
        course_titles: List[str]

    # Define API endpoints (same as main app, but using mock_rag_system)
    @test_app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        try:
            session_id = request.session_id
            if not session_id:
                session_id = mock_rag_system.session_manager.create_session()

            answer, sources = mock_rag_system.query(request.query, session_id)

            return QueryResponse(
                answer=answer,
                sources=sources,
                session_id=session_id
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @test_app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        try:
            analytics = mock_rag_system.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @test_app.get("/")
    async def root():
        return {"message": "RAG System API - Test Mode"}

    # Return TestClient
    return TestClient(test_app)
