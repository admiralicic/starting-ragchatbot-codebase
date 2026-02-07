"""
Integration tests for RAG System with real components
This will expose the MAX_RESULTS=0 bug and other configuration issues
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import Mock, patch
from config import config
from vector_store import VectorStore, SearchResults
from search_tools import CourseSearchTool, ToolManager
from rag_system import RAGSystem


def test_config_max_results():
    """Test that MAX_RESULTS configuration is set correctly"""
    print("\n[TEST 1] Checking MAX_RESULTS configuration...")

    max_results = config.MAX_RESULTS
    print(f"   Current MAX_RESULTS = {max_results}")

    if max_results == 0:
        print("❌ FAIL: MAX_RESULTS is 0! This will cause all searches to return empty results!")
        print("   Expected: MAX_RESULTS should be > 0 (typically 5)")
        print("   This is the ROOT CAUSE of 'query failed' errors")
        return False
    elif max_results < 3:
        print(f"⚠️  WARNING: MAX_RESULTS is {max_results}, which is quite low")
        print("   Recommended: 5 or more for better results")
        return True
    else:
        print(f"✅ PASS: MAX_RESULTS is set to {max_results}")
        return True


def test_vector_store_search_with_config():
    """Test vector store search uses MAX_RESULTS from config"""
    print("\n[TEST 2] Testing VectorStore search with actual config...")

    # Create mock ChromaDB client
    mock_chroma_client = Mock()
    mock_collection = Mock()

    # Mock query response
    mock_collection.query.return_value = {
        'documents': [[]],
        'metadatas': [[]],
        'distances': [[]]
    }

    mock_chroma_client.get_or_create_collection.return_value = mock_collection

    with patch('vector_store.chromadb.PersistentClient', return_value=mock_chroma_client):
        store = VectorStore(
            chroma_path="./test_db",
            embedding_model=config.EMBEDDING_MODEL,
            max_results=config.MAX_RESULTS
        )

        results = store.search(query="test query")

        # Check what limit was used
        call_kwargs = mock_collection.query.call_args.kwargs
        n_results = call_kwargs.get('n_results')

        print(f"   VectorStore searched with n_results = {n_results}")

        if n_results == 0:
            print("❌ FAIL: VectorStore is searching with n_results=0!")
            print("   This means NO results will ever be returned")
            return False
        else:
            print(f"✅ PASS: VectorStore searches with n_results={n_results}")
            return True


def test_course_search_tool_with_real_vector_store():
    """Test CourseSearchTool with actual VectorStore (mocked ChromaDB)"""
    print("\n[TEST 3] Testing CourseSearchTool with real VectorStore configuration...")

    mock_chroma_client = Mock()
    mock_collection = Mock()

    # Mock returns empty results (as would happen with MAX_RESULTS=0)
    mock_collection.query.return_value = {
        'documents': [[]],
        'metadatas': [[]],
        'distances': [[]]
    }
    mock_collection.get.return_value = {'ids': []}

    mock_chroma_client.get_or_create_collection.return_value = mock_collection

    with patch('vector_store.chromadb.PersistentClient', return_value=mock_chroma_client):
        store = VectorStore(
            chroma_path="./test_db",
            embedding_model=config.EMBEDDING_MODEL,
            max_results=config.MAX_RESULTS
        )

        tool = CourseSearchTool(store)
        result = tool.execute(query="What is Python?")

        print(f"   Search result: '{result}'")

        if "No relevant content found" in result:
            if config.MAX_RESULTS == 0:
                print("❌ FAIL: Got 'No relevant content found' because MAX_RESULTS=0")
                print("   This confirms the bug: searches return 0 results by design")
                return False
            else:
                print("⚠️  WARNING: No results found (but MAX_RESULTS is configured)")
                print("   This might be due to empty database")
                return True
        else:
            print("✅ PASS: Search returned content")
            return True


def test_tool_manager_integration():
    """Test ToolManager with registered tools"""
    print("\n[TEST 4] Testing ToolManager integration...")

    # Create mock vector store
    mock_store = Mock()
    mock_store.search.return_value = SearchResults(
        documents=["Test content"],
        metadata=[{"course_title": "Test", "lesson_number": 1}],
        distances=[0.5],
        error=None
    )
    mock_store.get_lesson_link.return_value = None

    # Create tool manager and register tool
    tool_manager = ToolManager()
    search_tool = CourseSearchTool(mock_store)
    tool_manager.register_tool(search_tool)

    # Get tool definitions
    tool_defs = tool_manager.get_tool_definitions()

    assert len(tool_defs) >= 1, "Should have at least one tool"
    assert any(t['name'] == 'search_course_content' for t in tool_defs), "Should have search tool"

    # Execute tool
    result = tool_manager.execute_tool(
        "search_course_content",
        query="test"
    )

    assert "Test content" in result

    # Check sources
    sources = tool_manager.get_last_sources()
    assert len(sources) == 1

    print("✅ PASS: ToolManager integration works correctly")
    return True


def test_rag_system_components():
    """Test that RAG system initializes all components"""
    print("\n[TEST 5] Testing RAG system component initialization...")

    try:
        # Mock ChromaDB to avoid file system operations
        mock_chroma_client = Mock()
        mock_collection = Mock()
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        with patch('vector_store.chromadb.PersistentClient', return_value=mock_chroma_client):
            rag = RAGSystem(config)

            # Check components exist
            assert rag.vector_store is not None, "Vector store should be initialized"
            assert rag.ai_generator is not None, "AI generator should be initialized"
            assert rag.tool_manager is not None, "Tool manager should be initialized"
            assert rag.search_tool is not None, "Search tool should be initialized"

            # Check tool is registered
            tool_defs = rag.tool_manager.get_tool_definitions()
            assert len(tool_defs) >= 1, "Should have tools registered"

            print("✅ PASS: RAG system components initialized correctly")
            return True

    except Exception as e:
        print(f"❌ FAIL: RAG system initialization failed: {e}")
        return False


def run_all_tests():
    """Run all integration tests"""
    print("="*70)
    print("TESTING: RAG System Integration (will expose MAX_RESULTS=0 bug)")
    print("="*70)

    tests = [
        test_config_max_results,
        test_vector_store_search_with_config,
        test_course_search_tool_with_real_vector_store,
        test_tool_manager_integration,
        test_rag_system_components
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
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
