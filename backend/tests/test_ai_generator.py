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


def test_two_round_tool_calling():
    """Test that Claude can make tool calls across 2 sequential rounds"""
    print("\n[TEST 5] Testing two-round tool calling (round 1: tool_use, round 2: tool_use, final: end_turn)...")

    with patch('ai_generator.anthropic.Anthropic') as mock_anthropic:
        # Setup mock tool manager
        mock_tool_manager = Mock()
        mock_tool_manager.execute_tool.side_effect = ["Result from tool 1", "Result from tool 2"]

        # Round 1: Claude wants to use first tool
        mock_tool_use_1 = Mock()
        mock_tool_use_1.type = "tool_use"
        mock_tool_use_1.name = "get_course_outline"
        mock_tool_use_1.id = "tool_1"
        mock_tool_use_1.input = {"course_name": "Python"}

        round1_response = Mock()
        round1_response.stop_reason = "tool_use"
        round1_response.content = [mock_tool_use_1]

        # Round 2: Claude wants to use second tool
        mock_tool_use_2 = Mock()
        mock_tool_use_2.type = "tool_use"
        mock_tool_use_2.name = "search_course_content"
        mock_tool_use_2.id = "tool_2"
        mock_tool_use_2.input = {"query": "lesson 1", "course_name": "Python"}

        round2_response = Mock()
        round2_response.stop_reason = "tool_use"
        round2_response.content = [mock_tool_use_2]

        # Final: end_turn with synthesized answer
        final_response = Mock()
        final_response.stop_reason = "end_turn"
        final_response.content = [Mock(text="Final answer using both tool results")]

        mock_client = mock_anthropic.return_value
        mock_client.messages.create.side_effect = [
            round1_response,
            round2_response,
            final_response
        ]

        # Execute
        generator = AIGenerator(api_key="test-key", model="claude-sonnet-4-20250514")
        tools = [
            {"name": "get_course_outline"},
            {"name": "search_course_content"}
        ]

        result = generator.generate_response(
            query="What lessons are in Python course and what does lesson 1 cover?",
            tools=tools,
            tool_manager=mock_tool_manager
        )

        # Verify external behavior
        assert mock_client.messages.create.call_count == 3, "Should make 3 API calls"
        assert mock_tool_manager.execute_tool.call_count == 2, "Should execute 2 tools"
        assert "Final answer" in result, "Should return final synthesized response"

        print("✅ PASS: Two-round tool calling works correctly")
        return True


def test_max_rounds_hit_forces_synthesis():
    """Test that after 2 tool rounds, a final call is made without tools"""
    print("\n[TEST 6] Testing max rounds hit (all responses request tools, forces final synthesis)...")

    with patch('ai_generator.anthropic.Anthropic') as mock_anthropic:
        mock_tool_manager = Mock()
        mock_tool_manager.execute_tool.side_effect = ["Result 1", "Result 2"]

        # Round 1: tool_use
        mock_tool_use_1 = Mock()
        mock_tool_use_1.type = "tool_use"
        mock_tool_use_1.name = "search_course_content"
        mock_tool_use_1.id = "tool_1"
        mock_tool_use_1.input = {"query": "test1"}

        round1_response = Mock()
        round1_response.stop_reason = "tool_use"
        round1_response.content = [mock_tool_use_1]

        # Round 2: tool_use (hits max rounds)
        mock_tool_use_2 = Mock()
        mock_tool_use_2.type = "tool_use"
        mock_tool_use_2.name = "search_course_content"
        mock_tool_use_2.id = "tool_2"
        mock_tool_use_2.input = {"query": "test2"}

        round2_response = Mock()
        round2_response.stop_reason = "tool_use"
        round2_response.content = [mock_tool_use_2]

        # Final synthesis call (without tools)
        final_response = Mock()
        final_response.stop_reason = "end_turn"
        final_response.content = [Mock(text="Synthesized answer after max rounds")]

        mock_client = mock_anthropic.return_value
        mock_client.messages.create.side_effect = [
            round1_response,
            round2_response,
            final_response
        ]

        # Execute
        generator = AIGenerator(api_key="test-key", model="claude-sonnet-4-20250514")
        tools = [{"name": "search_course_content"}]

        result = generator.generate_response(
            query="Complex query",
            tools=tools,
            tool_manager=mock_tool_manager
        )

        # Verify 3 API calls (2 rounds + 1 final)
        assert mock_client.messages.create.call_count == 3, "Should make 3 API calls"

        # Verify 2 tool executions
        assert mock_tool_manager.execute_tool.call_count == 2, "Should execute 2 tools"

        # Verify that final call does NOT include tools parameter
        final_call_kwargs = mock_client.messages.create.call_args_list[2].kwargs
        assert "tools" not in final_call_kwargs, "Final synthesis call should not include tools"

        assert "Synthesized answer" in result

        print("✅ PASS: Max rounds forces final synthesis without tools")
        return True


def test_early_termination_single_round():
    """Test that if Claude doesn't request tools in round 2, we terminate early"""
    print("\n[TEST 7] Testing early termination (round 1: tool_use, round 2: end_turn)...")

    with patch('ai_generator.anthropic.Anthropic') as mock_anthropic:
        mock_tool_manager = Mock()
        mock_tool_manager.execute_tool.return_value = "Tool result"

        # Round 1: tool_use
        mock_tool_use = Mock()
        mock_tool_use.type = "tool_use"
        mock_tool_use.name = "search_course_content"
        mock_tool_use.id = "tool_1"
        mock_tool_use.input = {"query": "test"}

        round1_response = Mock()
        round1_response.stop_reason = "tool_use"
        round1_response.content = [mock_tool_use]

        # Round 2: end_turn (early termination)
        round2_response = Mock()
        round2_response.stop_reason = "end_turn"
        round2_response.content = [Mock(text="Direct answer after one tool use")]

        mock_client = mock_anthropic.return_value
        mock_client.messages.create.side_effect = [
            round1_response,
            round2_response
        ]

        # Execute
        generator = AIGenerator(api_key="test-key", model="claude-sonnet-4-20250514")
        tools = [{"name": "search_course_content"}]

        result = generator.generate_response(
            query="Simple query",
            tools=tools,
            tool_manager=mock_tool_manager
        )

        # Verify only 2 API calls (not 3)
        assert mock_client.messages.create.call_count == 2, "Should make 2 API calls"

        # Verify 1 tool execution
        assert mock_tool_manager.execute_tool.call_count == 1, "Should execute 1 tool"

        assert "Direct answer" in result

        print("✅ PASS: Early termination works correctly")
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
        test_conversation_history_included,
        test_two_round_tool_calling,
        test_max_rounds_hit_forces_synthesis,
        test_early_termination_single_round
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
