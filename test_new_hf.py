#!/usr/bin/env python3
"""
Test the new Hugging Face Chat Completion implementation
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

def test_new_implementation():
    """Test new Chat Completion implementation"""
    print("Testing new Hugging Face Chat Completion implementation...")

    test_message = "Can you write a Python function to calculate fibonacci numbers?"
    system_prompt = "You are a helpful coding assistant."
    conversation_history = []

    result = _call_huggingface_chat_completion(system_prompt, test_message, conversation_history)
    print(f"Result: {result}")

if __name__ == "__main__":
    test_new_implementation()