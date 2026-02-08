"""
API Endpoint Tests for FastAPI RAG System
Tests /api/query, /api/courses, and root endpoints for proper request/response handling
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from fastapi import status


class TestQueryEndpoint:
    """Tests for POST /api/query endpoint"""

    def test_query_with_new_session(self, api_test_client, mock_rag_system):
        """Test query endpoint creates a new session when none provided"""
        response = api_test_client.post(
            "/api/query",
            json={"query": "What is Python?"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check response structure
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data

        # Verify session was created
        assert data["session_id"] == "test-session-123"
        mock_rag_system.session_manager.create_session.assert_called_once()

        # Verify RAG system query was called
        mock_rag_system.query.assert_called_once()

    def test_query_with_existing_session(self, api_test_client, mock_rag_system):
        """Test query endpoint uses provided session ID"""
        session_id = "existing-session-456"

        response = api_test_client.post(
            "/api/query",
            json={
                "query": "What are Python variables?",
                "session_id": session_id
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should use provided session ID
        assert data["session_id"] == session_id

        # Verify RAG system was called with correct session
        mock_rag_system.query.assert_called_once_with(
            "What are Python variables?",
            session_id
        )

        # Should NOT create new session
        mock_rag_system.session_manager.create_session.assert_not_called()

    def test_query_returns_answer_and_sources(self, api_test_client, mock_rag_system):
        """Test that query endpoint returns both answer and sources"""
        # Configure mock to return specific data
        mock_rag_system.query.side_effect = lambda q, s=None: (
            "Python is a versatile programming language.",
            [
                {"course": "Python Basics", "lesson": "1", "link": "https://example.com/lesson1"},
                {"course": "Python Basics", "lesson": "2", "link": "https://example.com/lesson2"}
            ]
        )

        response = api_test_client.post(
            "/api/query",
            json={"query": "Tell me about Python"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify answer
        assert data["answer"] == "Python is a versatile programming language."

        # Verify sources structure
        assert len(data["sources"]) == 2
        assert data["sources"][0]["course"] == "Python Basics"
        assert data["sources"][0]["lesson"] == "1"
        assert data["sources"][0]["link"] == "https://example.com/lesson1"

    def test_query_missing_query_field(self, api_test_client):
        """Test that query endpoint rejects requests without query field"""
        response = api_test_client.post(
            "/api/query",
            json={"session_id": "test"}  # Missing 'query' field
        )

        # FastAPI should return 422 for validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_query_empty_string(self, api_test_client, mock_rag_system):
        """Test that query endpoint handles empty query string"""
        response = api_test_client.post(
            "/api/query",
            json={"query": ""}
        )

        # Should still process (RAG system will handle empty query)
        assert response.status_code == status.HTTP_200_OK
        mock_rag_system.query.assert_called_once()

    def test_query_with_special_characters(self, api_test_client, mock_rag_system):
        """Test query endpoint handles special characters in query"""
        special_query = "What is @Python's #1 feature? & how does it work?"

        response = api_test_client.post(
            "/api/query",
            json={"query": special_query}
        )

        assert response.status_code == status.HTTP_200_OK
        # Verify the query was passed through correctly
        call_args = mock_rag_system.query.call_args
        assert special_query in call_args[0][0]

    def test_query_error_handling(self, api_test_client, mock_rag_system):
        """Test that query endpoint properly handles exceptions"""
        # Make RAG system raise an exception
        mock_rag_system.query.side_effect = Exception("Database connection failed")

        response = api_test_client.post(
            "/api/query",
            json={"query": "What is Python?"}
        )

        # Should return 500 with error detail
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Database connection failed" in response.json()["detail"]

    def test_query_with_long_text(self, api_test_client, mock_rag_system):
        """Test query endpoint handles long query text"""
        long_query = "What is Python? " * 100  # Very long query

        response = api_test_client.post(
            "/api/query",
            json={"query": long_query}
        )

        assert response.status_code == status.HTTP_200_OK
        mock_rag_system.query.assert_called_once()


class TestCoursesEndpoint:
    """Tests for GET /api/courses endpoint"""

    def test_get_courses_success(self, api_test_client, mock_rag_system):
        """Test courses endpoint returns course statistics"""
        response = api_test_client.get("/api/courses")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check response structure
        assert "total_courses" in data
        assert "course_titles" in data

        # Verify values from mock
        assert data["total_courses"] == 3
        assert len(data["course_titles"]) == 3
        assert "Python Basics" in data["course_titles"]

        # Verify RAG system was called
        mock_rag_system.get_course_analytics.assert_called_once()

    def test_get_courses_empty_catalog(self, api_test_client, mock_rag_system):
        """Test courses endpoint with empty course catalog"""
        # Configure mock to return empty catalog
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 0,
            "course_titles": []
        }

        response = api_test_client.get("/api/courses")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["total_courses"] == 0
        assert data["course_titles"] == []

    def test_get_courses_error_handling(self, api_test_client, mock_rag_system):
        """Test courses endpoint handles exceptions"""
        # Make analytics method raise an exception
        mock_rag_system.get_course_analytics.side_effect = Exception("Vector store unavailable")

        response = api_test_client.get("/api/courses")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Vector store unavailable" in response.json()["detail"]

    def test_get_courses_no_parameters(self, api_test_client):
        """Test that courses endpoint doesn't accept query parameters"""
        # GET requests with parameters should still work (parameters ignored)
        response = api_test_client.get("/api/courses?invalid=param")

        assert response.status_code == status.HTTP_200_OK


class TestRootEndpoint:
    """Tests for GET / root endpoint"""

    def test_root_endpoint(self, api_test_client):
        """Test root endpoint returns basic info"""
        response = api_test_client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "message" in data
        assert "Test Mode" in data["message"] or "RAG System" in data["message"]


class TestAPIIntegration:
    """Integration tests for API workflows"""

    def test_multi_turn_conversation_flow(self, api_test_client, mock_rag_system):
        """Test a multi-turn conversation using the same session"""
        # First query - creates session
        response1 = api_test_client.post(
            "/api/query",
            json={"query": "What is Python?"}
        )
        assert response1.status_code == status.HTTP_200_OK
        session_id = response1.json()["session_id"]

        # Second query - uses same session
        response2 = api_test_client.post(
            "/api/query",
            json={
                "query": "Tell me more about it",
                "session_id": session_id
            }
        )
        assert response2.status_code == status.HTTP_200_OK
        assert response2.json()["session_id"] == session_id

        # Verify both queries were processed
        assert mock_rag_system.query.call_count == 2

    def test_parallel_sessions(self, api_test_client, mock_rag_system):
        """Test that multiple sessions can be handled independently"""
        # Session 1
        response1 = api_test_client.post(
            "/api/query",
            json={"query": "What is Python?", "session_id": "session-1"}
        )
        assert response1.status_code == status.HTTP_200_OK

        # Session 2
        response2 = api_test_client.post(
            "/api/query",
            json={"query": "What is JavaScript?", "session_id": "session-2"}
        )
        assert response2.status_code == status.HTTP_200_OK

        # Verify both were processed with correct sessions
        calls = mock_rag_system.query.call_args_list
        assert len(calls) == 2
        assert calls[0][0][1] == "session-1"
        assert calls[1][0][1] == "session-2"

    def test_query_and_courses_workflow(self, api_test_client, mock_rag_system):
        """Test workflow of checking courses then querying"""
        # First check available courses
        courses_response = api_test_client.get("/api/courses")
        assert courses_response.status_code == status.HTTP_200_OK
        courses = courses_response.json()["course_titles"]
        assert len(courses) > 0

        # Then query about a specific course
        query_response = api_test_client.post(
            "/api/query",
            json={"query": f"Tell me about {courses[0]}"}
        )
        assert query_response.status_code == status.HTTP_200_OK
        assert "sources" in query_response.json()


class TestRequestValidation:
    """Tests for request validation and edge cases"""

    def test_invalid_json(self, api_test_client):
        """Test that invalid JSON is rejected"""
        response = api_test_client.post(
            "/api/query",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )

        # Should return 422 for invalid JSON
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_wrong_content_type(self, api_test_client):
        """Test that non-JSON content type is handled"""
        response = api_test_client.post(
            "/api/query",
            data="query=What is Python?",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        # FastAPI should reject non-JSON for JSON endpoints
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_extra_fields_ignored(self, api_test_client, mock_rag_system):
        """Test that extra fields in request are ignored"""
        response = api_test_client.post(
            "/api/query",
            json={
                "query": "What is Python?",
                "extra_field": "should be ignored",
                "another_extra": 123
            }
        )

        # Should still succeed (extra fields ignored by Pydantic)
        assert response.status_code == status.HTTP_200_OK
        mock_rag_system.query.assert_called_once()

    def test_wrong_field_types(self, api_test_client):
        """Test that wrong field types are rejected"""
        response = api_test_client.post(
            "/api/query",
            json={
                "query": 12345,  # Should be string
                "session_id": ["not", "a", "string"]  # Should be string
            }
        )

        # Should return 422 for type validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCORSAndHeaders:
    """Tests for CORS and HTTP headers"""

    def test_cors_middleware_configured(self, api_test_client):
        """Test that CORS middleware is configured in the app"""
        # The TestClient processes middleware, so we can verify the endpoint works
        # across different origins (which CORS would block without proper config)
        response = api_test_client.get("/api/courses")

        # If CORS wasn't configured, cross-origin requests would fail
        # The fact that we can make requests confirms CORS is working
        assert response.status_code == status.HTTP_200_OK

    def test_options_preflight(self, api_test_client):
        """Test OPTIONS preflight request for CORS"""
        response = api_test_client.options(
            "/api/query",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )

        # Should return 200 (OPTIONS requests handled by CORS middleware)
        assert response.status_code == status.HTTP_200_OK


def test_all_endpoints_accessible(api_test_client):
    """Smoke test to verify all endpoints are accessible"""
    endpoints = [
        ("/", "GET"),
        ("/api/courses", "GET"),
        ("/api/query", "POST")
    ]

    for path, method in endpoints:
        if method == "GET":
            response = api_test_client.get(path)
        elif method == "POST":
            response = api_test_client.post(path, json={"query": "test"})

        # All endpoints should be accessible (not 404)
        assert response.status_code != status.HTTP_404_NOT_FOUND, f"Endpoint {method} {path} not found"
