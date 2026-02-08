# RAG System Test Suite

Comprehensive test suite for the Retrieval-Augmented Generation (RAG) chatbot system.

## Overview

This test suite provides unit tests, integration tests, and API endpoint tests to ensure the reliability and correctness of the RAG system components.

## Test Structure

```
tests/
├── conftest.py                    # Shared pytest fixtures and test setup
├── test_api_endpoints.py          # FastAPI endpoint tests (23 tests)
├── test_ai_generator.py           # AI generator tool calling tests (7 tests)
├── test_course_search_tool.py     # Search tool unit tests (4 tests)
├── test_rag_integration.py        # Integration tests (5 tests)
└── run_all_tests.py              # Legacy test runner
```

## Running Tests

### Run All Tests
```bash
cd backend
uv run pytest tests/ -v
```

### Run Specific Test Files
```bash
# API endpoint tests only
uv run pytest tests/test_api_endpoints.py -v

# AI generator tests only
uv run pytest tests/test_ai_generator.py -v

# Integration tests only
uv run pytest tests/test_rag_integration.py -v
```

### Run Tests by Marker
```bash
# Run only API tests (if marked)
uv run pytest tests/ -v -m api

# Run only unit tests (if marked)
uv run pytest tests/ -v -m unit

# Run only integration tests (if marked)
uv run pytest tests/ -v -m integration
```

### Run Specific Test
```bash
uv run pytest tests/test_api_endpoints.py::TestQueryEndpoint::test_query_with_new_session -v
```

## Test Coverage

### API Endpoint Tests (`test_api_endpoints.py`)
Tests the FastAPI REST API endpoints for proper request/response handling:

- **TestQueryEndpoint**: Tests POST `/api/query` endpoint
  - Session creation and management
  - Query processing with/without session
  - Answer and source response format
  - Input validation and error handling
  - Special characters and edge cases

- **TestCoursesEndpoint**: Tests GET `/api/courses` endpoint
  - Course statistics retrieval
  - Empty catalog handling
  - Error handling

- **TestRootEndpoint**: Tests GET `/` root endpoint
  - Basic connectivity

- **TestAPIIntegration**: Integration tests for API workflows
  - Multi-turn conversations
  - Parallel session handling
  - Combined query and course lookup workflows

- **TestRequestValidation**: Input validation tests
  - Invalid JSON handling
  - Wrong content types
  - Type validation
  - Extra field handling

- **TestCORSAndHeaders**: CORS and HTTP header tests
  - CORS middleware configuration
  - OPTIONS preflight requests

### AI Generator Tests (`test_ai_generator.py`)
Tests the Anthropic Claude API integration and tool calling:

- Tool definitions passed to API
- Two-step tool execution flow
- Conditional tool execution based on stop_reason
- Conversation history inclusion
- Multi-round tool calling (up to 2 rounds)
- Max rounds enforcement
- Early termination optimization

### Search Tool Tests (`test_course_search_tool.py`)
Unit tests for the course search functionality:

- Search with valid results
- Search with zero results
- Course name filtering
- Error handling

### Integration Tests (`test_rag_integration.py`)
Tests component interactions and configuration:

- MAX_RESULTS configuration validation
- VectorStore search behavior
- CourseSearchTool with real VectorStore
- ToolManager integration
- RAGSystem component initialization

## Test Fixtures

The `conftest.py` file provides reusable fixtures for all tests:

### Configuration
- `test_config`: Test configuration with safe defaults

### Mocked Components
- `mock_chroma_client`: Mocked ChromaDB client
- `mock_vector_store`: Mocked VectorStore with predefined responses
- `mock_ai_generator`: Mocked AIGenerator
- `mock_session_manager`: Mocked SessionManager
- `mock_tool_manager`: Mocked ToolManager with tool definitions
- `mock_rag_system`: Fully mocked RAGSystem with all dependencies

### Test Data
- `sample_course`: Sample Course object with lessons
- `sample_search_results`: Sample SearchResults for testing

### API Testing
- `api_test_client`: FastAPI TestClient with mocked RAG system
  - Creates a test app without static file mounting
  - Avoids import issues with missing frontend files
  - Provides isolated API testing environment

## Pytest Configuration

The pytest configuration is defined in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["backend/tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--tb=short",
    "--strict-markers",
    "--disable-warnings",
]
markers = [
    "unit: Unit tests for individual components",
    "integration: Integration tests for component interactions",
    "api: API endpoint tests",
    "slow: Tests that take longer to run",
]
```

## Test Dependencies

Test-specific dependencies (installed via `uv sync`):
- `pytest>=8.0.0`: Testing framework
- `pytest-asyncio>=0.23.0`: Async test support
- `httpx>=0.27.0`: HTTP client for TestClient

## Writing New Tests

### API Endpoint Test Example
```python
def test_new_endpoint(api_test_client, mock_rag_system):
    """Test description"""
    # Configure mock behavior
    mock_rag_system.some_method.return_value = "expected_result"

    # Make API request
    response = api_test_client.post("/api/endpoint", json={"data": "value"})

    # Assert response
    assert response.status_code == 200
    assert response.json()["key"] == "expected_value"

    # Verify mock was called correctly
    mock_rag_system.some_method.assert_called_once_with("expected_arg")
```

### Unit Test Example
```python
from unittest.mock import Mock, patch

def test_component_behavior():
    """Test description"""
    # Setup mocks
    mock_dependency = Mock()
    mock_dependency.method.return_value = "result"

    # Test component
    component = YourComponent(mock_dependency)
    result = component.do_something()

    # Assertions
    assert result == "expected"
    mock_dependency.method.assert_called_once()
```

## Best Practices

1. **Use Fixtures**: Leverage the shared fixtures in `conftest.py` to avoid duplication
2. **Mock External Dependencies**: Always mock ChromaDB, Anthropic API, and file system operations
3. **Test Edge Cases**: Include tests for empty inputs, errors, and boundary conditions
4. **Clear Test Names**: Use descriptive test names that explain what is being tested
5. **Isolated Tests**: Each test should be independent and not rely on other tests
6. **Assert Behavior**: Verify both return values and that mocks were called correctly
7. **Use side_effect**: For mocks that need to return fresh values on each call

## Troubleshooting

### Tests Fail with Import Errors
Make sure you're running from the `backend` directory and using `uv run`:
```bash
cd backend
uv run pytest tests/ -v
```

### Mock Not Resetting Between Tests
Use `side_effect` instead of `return_value` for mocks that need fresh state:
```python
mock.method.side_effect = lambda x: {"fresh": "value"}
```

### Pydantic Validation Errors
Ensure mock data matches the expected Pydantic model types:
```python
# Wrong: lesson as int
{"course": "Test", "lesson": 1}

# Correct: lesson as string
{"course": "Test", "lesson": "1"}
```

## Future Enhancements

Potential areas for test expansion:
- [ ] Add document processor tests
- [ ] Add vector store persistence tests
- [ ] Add session manager state tests
- [ ] Add performance/load tests
- [ ] Add test coverage reporting
- [ ] Add end-to-end tests with real API calls (using test API key)
