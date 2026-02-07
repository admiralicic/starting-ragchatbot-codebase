"""
Tests for CourseSearchTool.execute() method
Tests the search tool's ability to query vector store and format results
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import Mock
from search_tools import CourseSearchTool
from vector_store import SearchResults


def test_execute_with_valid_results():
    """Test that execute formats results correctly when vector store returns data"""
    print("\n[TEST 1] Testing CourseSearchTool with valid search results...")

    # Create mock vector store
    mock_store = Mock()
    mock_results = SearchResults(
        documents=["Python is a high-level programming language"],
        metadata=[{
            "course_title": "Introduction to Python",
            "lesson_number": 1
        }],
        distances=[0.5],
        error=None
    )
    mock_store.search.return_value = mock_results
    mock_store.get_lesson_link.return_value = "https://example.com/lesson1"

    # Create tool and execute
    tool = CourseSearchTool(mock_store)
    result = tool.execute(query="What is Python?")

    # Verify
    assert "Introduction to Python" in result, "Course title should be in result"
    assert "Lesson 1" in result, "Lesson number should be in result"
    assert "Python is a high-level programming language" in result, "Content should be in result"
    assert len(tool.last_sources) == 1, "Should track one source"

    print("✅ PASS: CourseSearchTool formats valid results correctly")
    return True


def test_execute_with_zero_results():
    """Test that execute handles empty results (MAX_RESULTS=0 scenario)"""
    print("\n[TEST 2] Testing CourseSearchTool with ZERO results (MAX_RESULTS=0 bug)...")

    # Create mock vector store returning empty results
    mock_store = Mock()
    mock_results = SearchResults(
        documents=[],
        metadata=[],
        distances=[],
        error=None
    )
    mock_store.search.return_value = mock_results

    # Create tool and execute
    tool = CourseSearchTool(mock_store)
    result = tool.execute(query="What is Python?")

    # Verify
    assert "No relevant content found" in result, "Should return 'no content' message"
    assert len(tool.last_sources) == 0, "Should have no sources"

    print("✅ PASS: CourseSearchTool handles empty results")
    print(f"   Result message: '{result}'")
    return True


def test_execute_with_course_filter():
    """Test that course_name filter is passed to vector store"""
    print("\n[TEST 3] Testing CourseSearchTool with course filter...")

    mock_store = Mock()
    mock_results = SearchResults(
        documents=["MCP content"],
        metadata=[{"course_title": "MCP Servers", "lesson_number": 1}],
        distances=[0.3],
        error=None
    )
    mock_store.search.return_value = mock_results
    mock_store.get_lesson_link.return_value = None

    tool = CourseSearchTool(mock_store)
    result = tool.execute(query="MCP", course_name="Introduction to MCP")

    # Verify search was called with course_name
    mock_store.search.assert_called_once()
    call_args = mock_store.search.call_args
    assert call_args.kwargs['course_name'] == "Introduction to MCP"

    print("✅ PASS: Course filter is passed correctly")
    return True


def test_execute_with_error():
    """Test that errors from vector store are propagated"""
    print("\n[TEST 4] Testing CourseSearchTool error handling...")

    mock_store = Mock()
    mock_results = SearchResults(
        documents=[],
        metadata=[],
        distances=[],
        error="Database connection failed"
    )
    mock_store.search.return_value = mock_results

    tool = CourseSearchTool(mock_store)
    result = tool.execute(query="test")

    assert "Database connection failed" in result

    print("✅ PASS: Errors are propagated correctly")
    return True


def run_all_tests():
    """Run all CourseSearchTool tests"""
    print("="*70)
    print("TESTING: CourseSearchTool.execute() method")
    print("="*70)

    tests = [
        test_execute_with_valid_results,
        test_execute_with_zero_results,
        test_execute_with_course_filter,
        test_execute_with_error
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"❌ FAIL: {e}")
        except Exception as e:
            failed += 1
            print(f"❌ ERROR: {e}")

    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*70)

    return passed, failed


if __name__ == "__main__":
    run_all_tests()
