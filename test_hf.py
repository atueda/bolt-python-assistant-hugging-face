#!/usr/bin/env python3

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.llm_caller import _call_huggingface_chat_completion

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_huggingface_fallback():
    """Test the Hugging Face chat completion functionality"""

    # Test messages in Japanese (like in the logs)
    test_messages = [
        "抹茶ケーキの作りかた",
        "プログラミングについて教えて",
        "Hello, how can you help me with code?"
    ]

    system_prompt = """You're an AI assistant specialized in answering questions about code.
You'll analyze code-related questions and provide clear, accurate responses.
When you include markdown text, convert them to Slack compatible ones.
When you include code examples, convert them to Slack compatible ones. (There must be an empty line before a code block.)
When a prompt has Slack's special syntax like <@USER_ID> or <#CHANNEL_ID>, you must keep them as-is in your response."""

    for i, message in enumerate(test_messages, 1):
        print(f"\n{'='*50}")
        print(f"TEST {i}: {message}")
        print('='*50)

        try:
            response = _call_huggingface_chat_completion(
                system_prompt=system_prompt,
                user_message=message,
                conversation_history=[f"User: {message}"]
            )

            if response:
                print(f"✅ SUCCESS: Got response ({len(response)} characters)")
                print(f"Response preview: {response[:200]}...")
            else:
                print("❌ FAILURE: Empty response")

        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("Testing Hugging Face Chat Completion...")
    test_huggingface_fallback()