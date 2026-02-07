"""
Tests for AIGenerator tool calling functionality
Tests if AIGenerator correctly invokes tools when needed
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import Mock, patch, MagicMock
from ai_generator import AIGenerator


def test_tools_passed_to_api():
    """Test that tools are passed to Anthropic API correctly"""
    print("\n[TEST 1] Testing that tools are passed to Anthropic API...")

    with patch('ai_generator.anthropic.Anthropic') as mock_anthropic:
        # Setup mock response
        mock_response = Mock()
        mock_response.stop_reason = "end_turn"
        mock_response.content = [Mock(text="Answer")]

        mock_client = mock_anthropic.return_value
        mock_client.messages.create.return_value = mock_response

        # Create generator and call with tools
        generator = AIGenerator(api_key="test-key", model="claude-sonnet-4-20250514")

        tools = [{
            "name": "search_course_content",
            "description": "Search courses",
            "input_schema": {"type": "object", "properties": {}}
        }]

        generator.generate_response(
            query="Test query",
            tools=tools,
            tool_manager=Mock()
        )

        # Verify API was called with tools
        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert "tools" in call_kwargs, "Tools should be passed to API"
        assert call_kwargs["tools"] == tools, "Tools should match"
        assert call_kwargs["tool_choice"] == {"type": "auto"}, "tool_choice should be auto"

        print("✅ PASS: Tools are passed to API correctly")
        return True


def test_tool_execution_flow():
    """Test the two-step tool execution flow"""
    print("\n[TEST 2] Testing tool execution flow (call 1: tool_use, call 2: final answer)...")

    with patch('ai_generator.anthropic.Anthropic') as mock_anthropic:
        # Setup mock tool manager
        mock_tool_manager = Mock()
        mock_tool_manager.execute_tool.return_value = "Search results: Python info"

        # First response: Claude wants to use tool
        mock_tool_use = Mock()
        mock_tool_use.type = "tool_use"
        mock_tool_use.name = "search_course_content"
        mock_tool_use.id = "tool_123"
        mock_tool_use.input = {"query": "Python"}

        mock_first_response = Mock()
        mock_first_response.stop_reason = "tool_use"
        mock_first_response.content = [mock_tool_use]

        # Second response: Final answer
        mock_final_response = Mock()
        mock_final_response.stop_reason = "end_turn"
        mock_final_response.content = [Mock(text="Python is a programming language")]

        mock_client = mock_anthropic.return_value
        mock_client.messages.create.side_effect = [
            mock_first_response,
            mock_final_response
        ]

        # Execute
        generator = AIGenerator(api_key="test-key", model="claude-sonnet-4-20250514")
        tools = [{"name": "search_course_content"}]

        result = generator.generate_response(
            query="What is Python?",
            tools=tools,
            tool_manager=mock_tool_manager
        )

        # Verify tool was executed
        mock_tool_manager.execute_tool.assert_called_once_with(
            "search_course_content",
            query="Python"
        )

        # Verify two API calls were made
        assert mock_client.messages.create.call_count == 2, "Should make 2 API calls"

        # Verify final result
        assert "Python is a programming language" in result

        print("✅ PASS: Two-step tool execution works correctly")
        return True


def test_no_tool_execution_without_stop_reason():
    """Test that tools aren't executed if stop_reason != 'tool_use'"""
    print("\n[TEST 3] Testing that tools aren't executed without tool_use stop_reason...")

    with patch('ai_generator.anthropic.Anthropic') as mock_anthropic:
        mock_response = Mock()
        mock_response.stop_reason = "end_turn"  # Not tool_use
        mock_response.content = [Mock(text="Direct answer")]

        mock_client = mock_anthropic.return_value
        mock_client.messages.create.return_value = mock_response

        mock_tool_manager = Mock()

        generator = AIGenerator(api_key="test-key", model="claude-sonnet-4-20250514")
        result = generator.generate_response(
            query="What is 2+2?",
            tools=[{"name": "search_course_content"}],
            tool_manager=mock_tool_manager
        )

        # Verify tool was NOT executed
        mock_tool_manager.execute_tool.assert_not_called()

        # Verify only one API call
        assert mock_client.messages.create.call_count == 1

        print("✅ PASS: Tools not executed when stop_reason != tool_use")
        return True


def test_conversation_history_included():
    """Test that conversation history is included in system prompt"""
    print("\n[TEST 4] Testing conversation history inclusion...")

    with patch('ai_generator.anthropic.Anthropic') as mock_anthropic:
        mock_response = Mock()
        mock_response.stop_reason = "end_turn"
        mock_response.content = [Mock(text="Answer")]

        mock_client = mock_anthropic.return_value
        mock_client.messages.create.return_value = mock_response

        generator = AIGenerator(api_key="test-key", model="claude-sonnet-4-20250514")

        history = "User: Hello\nAssistant: Hi there!"

        generator.generate_response(
            query="How are you?",
            conversation_history=history
        )

        # Verify history in system prompt
        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert "Hello" in call_kwargs["system"]
        assert "Hi there" in call_kwargs["system"]

        print("✅ PASS: Conversation history included in system prompt")
        return True


def run_all_tests():
    """Run all AIGenerator tests"""
    print("="*70)
    print("TESTING: AIGenerator tool calling functionality")
    print("="*70)

    tests = [
        test_tools_passed_to_api,
        test_tool_execution_flow,
        test_no_tool_execution_without_stop_reason,
        test_conversation_history_included
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
