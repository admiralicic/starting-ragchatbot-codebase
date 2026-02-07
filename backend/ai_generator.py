import anthropic
from typing import List, Optional, Dict, Any
from config import config

class AIGenerator:
    """Handles interactions with Anthropic's Claude API for generating responses"""
    
    # Static system prompt to avoid rebuilding on each call
    SYSTEM_PROMPT = """ You are an AI assistant specialized in course materials and educational content with access to tools for querying course information.

Tool Usage Guidelines:
- **Search Tool** (`search_course_content`): Use for questions about specific course content, concepts, or detailed materials
- **Outline Tool** (`get_course_outline`): Use when users ask about course structure, lesson list, table of contents, or "what's in this course"
- **Maximum two tool rounds per query** - you can make tool calls across multiple rounds if needed
- Use sequential tool calls when one result informs the next search:
  - Example: First get course outline to learn lesson titles, then search specific lesson content
  - Example: Compare topics by searching multiple courses sequentially
- Synthesize tool results into accurate, fact-based responses
- If tools yield no results, state this clearly without offering alternatives

Outline vs Search Decision:
- "What lessons are in X?" → Use outline tool
- "Tell me about X concept" → Use search tool
- "Show me course outline" → Use outline tool
- "What does lesson Y cover?" → Use search tool with lesson filter

Response Protocol:
- **General knowledge questions**: Answer using existing knowledge without searching
- **Course-specific questions**: Search first, then answer
- **No meta-commentary**:
 - Provide direct answers only — no reasoning process, search explanations, or question-type analysis
 - Do not mention "based on the search results"


All responses must be:
1. **Brief, Concise and focused** - Get to the point quickly
2. **Educational** - Maintain instructional value
3. **Clear** - Use accessible language
4. **Example-supported** - Include relevant examples when they aid understanding
Provide only the direct answer to what was asked.
"""
    
    def __init__(self, api_key: str, model: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        
        # Pre-build base API parameters
        self.base_params = {
            "model": self.model,
            "temperature": 0,
            "max_tokens": 800
        }
    
    def generate_response(self, query: str,
                         conversation_history: Optional[str] = None,
                         tools: Optional[List] = None,
                         tool_manager=None) -> str:
        """
        Generate AI response with optional tool usage and conversation context.

        Args:
            query: The user's question or request
            conversation_history: Previous messages for context
            tools: Available tools the AI can use
            tool_manager: Manager to execute tools

        Returns:
            Generated response as string
        """

        # Build system content efficiently - avoid string ops when possible
        system_content = (
            f"{self.SYSTEM_PROMPT}\n\nPrevious conversation:\n{conversation_history}"
            if conversation_history
            else self.SYSTEM_PROMPT
        )

        # Initialize messages
        messages = [{"role": "user", "content": query}]

        # Prepare base API call parameters
        api_params = {
            **self.base_params,
            "system": system_content
        }

        # Add tools if available
        if tools:
            api_params["tools"] = tools
            api_params["tool_choice"] = {"type": "auto"}

        # Multi-round tool calling loop
        for round_num in range(config.MAX_TOOL_ROUNDS):
            # Make API call (with tools included for all rounds)
            api_params["messages"] = messages
            response = self.client.messages.create(**api_params)

            # Check termination condition
            if response.stop_reason != "tool_use":
                # No tools needed - return final answer
                return response.content[0].text

            # Tools requested - execute and continue
            if tool_manager:
                messages = self._execute_tools_and_update_messages(
                    response, messages, tool_manager
                )
            else:
                # No tool manager but tools requested - return text anyway
                return response.content[0].text

        # Hit max rounds - make final synthesis call WITHOUT tools
        final_params = {
            **self.base_params,
            "messages": messages,
            "system": system_content
        }
        final_response = self.client.messages.create(**final_params)
        return final_response.content[0].text
    
    def _execute_tools_and_update_messages(
        self,
        response,
        messages: List[Dict],
        tool_manager
    ) -> List[Dict]:
        """
        Execute all tools from response and append results to messages.

        Args:
            response: The response containing tool use requests
            messages: Current message history
            tool_manager: Manager to execute tools

        Returns:
            Updated messages list with tool use and tool results appended
        """
        # Append assistant's tool_use
        messages.append({"role": "assistant", "content": response.content})

        # Execute all tools and collect results
        tool_results = []
        for content_block in response.content:
            if hasattr(content_block, 'type') and content_block.type == "tool_use":
                result = tool_manager.execute_tool(
                    content_block.name,
                    **content_block.input
                )
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": content_block.id,
                    "content": result
                })

        # Append tool results
        if tool_results:
            messages.append({"role": "user", "content": tool_results})

        return messages