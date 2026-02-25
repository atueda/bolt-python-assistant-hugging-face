import json
import logging
import os

import openai
from openai.types.responses import ResponseInputParam
from slack_sdk.models.messages.chunk import TaskUpdateChunk
from slack_sdk.web.chat_stream import ChatStream

from agent.tools.dice import roll_dice, roll_dice_definition

logger = logging.getLogger(__name__)


def _format_slack_response(response: str) -> str:
    """Format AI response for Slack with proper markdown"""

    # Clean up the response
    response = response.strip()

    # Remove common AI response prefixes
    prefixes_to_remove = ["Response:", "Assistant:", "AI:", "Bot:", "Here's", "Here is"]

    for prefix in prefixes_to_remove:
        if response.startswith(prefix):
            response = response[len(prefix) :].strip()
            break

    # Ensure code blocks are properly formatted for Slack
    import re

    # Convert triple backticks to Slack format if needed
    response = re.sub(
        r"```(\w+)?\n(.*?)\n```", r"```\1\n\2\n```", response, flags=re.DOTALL
    )

    # Ensure single backticks for inline code
    response = re.sub(r"`([^`\n]+)`", r"`\1`", response)

    # Add emoji for better visual appeal
    if any(
        keyword in response.lower()
        for keyword in ["code", "function", "class", "method", "variable"]
    ):
        return f"💻 {response}"
    elif any(
        keyword in response.lower() for keyword in ["error", "bug", "issue", "problem"]
    ):
        return f"🐛 {response}"
    elif any(
        keyword in response.lower()
        for keyword in ["optimize", "improve", "better", "performance"]
    ):
        return f"⚡ {response}"
    else:
        return f"🤖 {response}"


def _call_huggingface_chat_completion(
    system_prompt: str, user_message: str, conversation_history: list
) -> str:
    """Call Hugging Face Chat Completion API using the same approach as Node.js sample"""

    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        logger.warning("HUGGINGFACE_API_KEY not found")
        return ""
    try:
        from huggingface_hub import InferenceClient

        logger.info("Using Hugging Face Chat Completion API")

        # Create inference client using the new router endpoint
        client = InferenceClient(token=api_key, base_url="https://router.huggingface.co/v1")

        # Build messages array like in Node.js sample
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        logger.info(
            f"Calling Qwen/Qwen2.5-Coder-32B-Instruct with message: {user_message[:100]}..."
        )

        # Use the same model as Node.js sample
        result = client.chat_completion(
            model="Qwen/Qwen2.5-Coder-32B-Instruct",
            messages=messages,
            max_tokens=2000,
            temperature=0.7,
        )

        logger.info("Received response from Hugging Face API")

        # Extract response content
        response_content = None
        if result and getattr(result, "choices", None) and len(result.choices) > 0:
            choice = result.choices[0]
            # Defensive: some APIs return message, some just content
            if hasattr(choice, "message") and hasattr(choice.message, "content"):
                response_content = choice.message.content
            elif hasattr(choice, "content"):
                response_content = choice.content
        if isinstance(response_content, str):
            logger.info(f"Response content: {response_content[:200]}...")
            return response_content.strip()
        else:
            logger.warning("No valid response from Hugging Face API")
            return ""

    except Exception as e:
        logger.error(f"Error calling Hugging Face Chat Completion API: {e}")
        import traceback

        logger.error(f"Full traceback: {traceback.format_exc()}")

        # Fallback to contextual responses if API fails
        logger.info("DEBUG: Falling back to contextual response generation")

        # Analyze the user message for context and intent
        user_message_lower = user_message.lower()
        logger.info(
            f"DEBUG: user_message_lower for contextual responses: {user_message_lower}"
        )

        # Code-related questions
        code_keywords = [
            "python",
            "javascript",
            "java",
            "c++",
            "react",
            "node",
            "html",
            "css",
            "function",
            "method",
            "class",
            "variable",
            "array",
            "object",
            "string",
            "code",
            "programming",
            "syntax",
            "algorithm",
            "debug",
            "error",
            "bug",
        ]

        if any(keyword in user_message_lower for keyword in code_keywords):
            logger.info("DEBUG: Found code-related keywords, processing...")

            # Check for specific Python explanation requests
            if "python" in user_message_lower and any(
                q in user_message_lower for q in ["what is", "explain", "について"]
            ):
                logger.info("DEBUG: Found Python explanation request")
                return """💻 Pythonは、シンプルで読みやすい構文を持つプログラミング言語です。

**特徴:**
- 初心者にも学びやすい
- Web開発、データ分析、AI/ML、自動化など幅広い用途
- 豊富なライブラリとフレームワーク

**基本的な例:**
```python
# Hello World
print("Hello, World!")

# 変数と関数
def greet(name):
    return f"Hello, {name}!"

message = greet("Python")
print(message)
```

何か具体的なPythonの質問があれば、お気軽にお聞きください！"""

            # Check for JavaScript
            elif "javascript" in user_message_lower or "js" in user_message_lower:
                logger.info("DEBUG: Found JavaScript keywords")
                return """💻 JavaScriptは、主にWebブラウザで動作するプログラミング言語です。

**用途:**
- Webページのインタラクティブな機能
- Node.jsによるサーバーサイド開発
- モバイルアプリ開発（React Native）

**基本例:**
```javascript
// 関数の定義
function greet(name) {
    return `Hello, ${name}!`;
}

// DOM操作
document.getElementById("myButton").addEventListener("click", function() {
    alert("ボタンがクリックされました！");
});
```

具体的なJavaScriptの質問があれば、詳しく説明します！"""

            # Optimization questions
            elif any(
                keyword in user_message_lower
                for keyword in [
                    "optimize",
                    "最適化",
                    "performance",
                    "パフォーマンス",
                    "speed",
                    "高速",
                ]
            ):
                return """⚡ コードの最適化についてお手伝いします！

**最適化のポイント:**
- アルゴリズムの計算量改善
- メモリ使用量の削減
- データ構造の選択
- キャッシュの活用

最適化したいコードを教えていただければ、具体的な改善提案をします！"""

            # General help or greeting
            elif any(
                keyword in user_message_lower
                for keyword in [
                    "hello",
                    "hi",
                    "こんにちは",
                    "はじめまして",
                    "help",
                    "ヘルプ",
                ]
            ):
                return """👋 こんにちは！コード専門のアシスタントです。

**お手伝いできること:**
💻 コードの説明と解析
🐛 エラーの診断と修正
⚡ パフォーマンス最適化
🔧 新機能の実装支援
❓ プログラミングの質問回答

何かお困りのことがあれば、お気軽にお聞きください！"""

            # Error/debugging questions
            elif any(
                keyword in user_message_lower
                for keyword in [
                    "error",
                    "エラー",
                    "bug",
                    "バグ",
                    "debug",
                    "fix",
                    "修正",
                    "解決",
                ]
            ):
                return """🐛 エラーやバグの解決をお手伝いします！

**トラブルシューティングのために以下の情報があると助かります:**
1. エラーメッセージの全文
2. 問題が発生するコード
3. 期待する動作
4. 実際に起こる動作

コードとエラーメッセージを共有していただければ、原因と解決策を提案します！"""

            # General programming response for all other code-related questions
            else:
                logger.info("DEBUG: Using general programming response")
                return """💻 プログラミングに関するご質問ですね！

コードの説明、デバッグ、最適化など、どのようなことでもお手伝いします。

**できること:**
- コードの解説と改善提案
- バグの発見と修正方法
- ベストプラクティスの提案
- アルゴリズムの説明

コードを貼り付けていただければ、詳しく分析してアドバイスします！"""

        # Fallback for non-programming questions
        else:
            return f"""🤖 「{user_message}」についてのご質問ですね。

私はプログラミング専門のアシスタントです。以下のようなことでお手伝いできます：

**得意分野:**
💻 コードの説明と解析
🐛 エラーの診断と修正
⚡ パフォーマンス最適化
🔧 新機能の実装支援
❓ プログラミングの質問回答

コードに関するご質問があれば、詳しくサポートします！"""


def call_llm(
    streamer: ChatStream,
    prompts: ResponseInputParam,
):
    """
    Stream an LLM response to prompts with fallback to Hugging Face chat completion
    Tries OpenAI first, falls back to Hugging Face if OpenAI fails

    https://docs.slack.dev/tools/python-slack-sdk/web#sending-streaming-messages
    https://platform.openai.com/docs/guides/text
    https://platform.openai.com/docs/guides/streaming-responses
    https://platform.openai.com/docs/guides/function-calling
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if openai_api_key:
        # Try OpenAI first
        try:
            logger.info("Trying OpenAI API")
            _call_openai_llm(streamer, prompts)
            return
        except Exception as openai_error:
            logger.warning(
                f"OpenAI API failed: {openai_error}, falling back to Hugging Face"
            )
    else:
        logger.info("No OpenAI API key found, using Hugging Face directly")

    # Fallback to Hugging Face chat completion
    try:
        logger.info("Using Hugging Face chat completion API")
        streamer.append(markdown_text="🤖 Using Hugging Face AI...\n\n")
        _call_huggingface_fallback(streamer, prompts)
    except Exception as hf_error:
        logger.error(f"Hugging Face chat completion failed: {hf_error}")
        streamer.append(
            markdown_text="❌ Sorry, all AI services are currently unavailable. Please try again later."
        )


def _call_openai_llm(streamer: ChatStream, prompts: ResponseInputParam):
    """Original OpenAI implementation"""
    llm = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    tool_calls = []
    response = llm.responses.create(
        model="gpt-4o-mini",
        input=prompts,
        tools=[
            roll_dice_definition,
        ],
        stream=True,
    )
    for event in response:
        # Markdown text from the LLM response is streamed in chat as it arrives
        if event.type == "response.output_text.delta":
            streamer.append(markdown_text=f"{event.delta}")

        # Function calls are saved for later computation and a new task is shown
        if event.type == "response.output_item.done":
            if event.item.type == "function_call":
                tool_calls.append(event.item)
                if event.item.name == "roll_dice":
                    args = json.loads(event.item.arguments)
                    streamer.append(
                        chunks=[
                            TaskUpdateChunk(
                                id=f"{event.item.call_id}",
                                title=f"Rolling a {args['count']}d{args['sides']}...",
                                status="in_progress",
                            ),
                        ],
                    )

    # Tool calls are performed and tasks are marked as completed in Slack
    if tool_calls:
        for call in tool_calls:
            if call.name == "roll_dice":
                args = json.loads(call.arguments)
                prompts.append(
                    {
                        "id": str(call.id) if call.id else "",
                        "call_id": call.call_id,
                        "type": "function_call",
                        "name": "roll_dice",
                        "arguments": call.arguments,
                    }
                )
                result = roll_dice(**args)
                prompts.append(
                    {
                        "type": "function_call_output",
                        "call_id": call.call_id,
                        "output": json.dumps(result),
                    }
                )
                if result.get("error") is not None:
                    streamer.append(
                        chunks=[
                            TaskUpdateChunk(
                                id=f"{call.call_id}",
                                title=f"{result['error']}",
                                status="error",
                            ),
                        ],
                    )
                else:
                    streamer.append(
                        chunks=[
                            TaskUpdateChunk(
                                id=f"{call.call_id}",
                                title=f"{result['description']}",
                                status="complete",
                            ),
                        ],
                    )

        # Complete the LLM response after making tool calls
        _call_openai_llm(streamer, prompts)


def _call_huggingface_fallback(streamer: ChatStream, prompts: ResponseInputParam):
    """Hugging Face API fallback implementation with system prompt"""

    logger.info("DEBUG: _call_huggingface_fallback called")
    logger.info(f"DEBUG: prompts = {prompts}")

    # System prompt for code assistant (matching Node.js sample)
    system_prompt = """You're an AI assistant specialized in answering questions about code.
You'll analyze code-related questions and provide clear, accurate responses.
When you include markdown text, convert them to Slack compatible ones.
When you include code examples, convert them to Slack compatible ones. (There must be an empty line before a code block.)
When a prompt has Slack's special syntax like <@USER_ID> or <#CHANNEL_ID>, you must keep them as-is in your response."""

    # Extract conversation history from prompts
    conversation_history = []
    user_message = ""

    for prompt in prompts:
        logger.info(f"DEBUG: Processing prompt: {prompt}")
        if isinstance(prompt, dict) and prompt.get("role") == "user":
            content = prompt.get("content", "")
            user_message = str(content) if content else ""
            conversation_history.append(f"User: {user_message}")
            logger.info(f"DEBUG: Extracted user_message: {user_message}")
        elif isinstance(prompt, dict) and prompt.get("role") == "assistant":
            content = prompt.get("content", "")
            if content:
                conversation_history.append(f"Assistant: {str(content)}")

    if not user_message:
        user_message = "Hello! How can I help you today?"
        logger.info("DEBUG: Using default user_message")

    logger.info(f"DEBUG: Final user_message: {user_message}")
    logger.info(f"DEBUG: conversation_history: {conversation_history}")

    # Use system prompt as context for question-answering model

    # Check if this is a dice roll request
    if any(word in user_message.lower() for word in ["roll", "dice", "random"]):
        # Handle dice rolling manually since Hugging Face doesn't support function calls
        import re

        dice_pattern = r"(\d+)d(\d+)"
        matches = re.findall(dice_pattern, user_message.lower())

        if matches:
            total_result = []
            for count_str, sides_str in matches:
                count, sides = int(count_str), int(sides_str)
                result = roll_dice(sides=sides, count=count)
                total_result.append(result)

            if total_result:
                dice_results = []
                for result in total_result:
                    if result.get("error"):
                        dice_results.append(f"Error: {result['error']}")
                    else:
                        dice_results.append(result["description"])

                response_text = f"🎲 {', '.join(dice_results)}\n\nAnything else I can help you with?"
                streamer.append(markdown_text=response_text)
                return

    # Use Hugging Face chat completion API (using existing function)
    logger.info("DEBUG: Calling _call_huggingface_chat_completion")
    api_response = _call_huggingface_chat_completion(
        system_prompt, user_message, conversation_history
    )
    logger.info(f"DEBUG: api_response = {api_response}")

    if api_response:
        logger.info("DEBUG: API response received, formatting for Slack")
        formatted_response = _format_slack_response(api_response)
        logger.info(f"DEBUG: formatted_response = {formatted_response}")
        streamer.append(markdown_text=formatted_response)
    else:
        logger.warning("DEBUG: No API response, using fallback message")
        # If contextual response generation fails, use simple fallback
        fallback_response = "🤖 申し訳ございません。現在、システムに一時的な問題が発生しています。プログラミングに関するご質問であれば、再度お試しください。"
        streamer.append(markdown_text=fallback_response)
