#!/usr/bin/env python3
"""
Quick test to check the debug logging
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.llm_caller import _call_huggingface_chat_completion

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def test_debug_logging():
    """Test debug logging with a simple message"""
    print("Testing debug logging...")

    test_message = "I am feeling happy today"
    system_prompt = "You are a helpful assistant."
    conversation_history = []

    result = _call_huggingface_chat_completion(system_prompt, test_message, conversation_history)
    print(f"Result: {result}")

if __name__ == "__main__":
    test_debug_logging()