#!/usr/bin/env python3
"""
Test script to verify Hugging Face InferenceClient works directly
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_inference_client():
    """Test Hugging Face InferenceClient directly"""
    try:
        from huggingface_hub import InferenceClient

        api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            print("ERROR: HUGGINGFACE_API_KEY not found")
            return

        print(f"Using API Key: {api_key[:10]}...")

        # Test emotion detection
        print("\n=== Testing Emotion Detection ===")
        client = InferenceClient(model="SamLowe/roberta-base-go_emotions", token=api_key)
        result = client.text_classification("I am feeling very happy and excited about this project!")
        print(f"Result: {result}")

        # Test sentiment analysis
        print("\n=== Testing Sentiment Analysis ===")
        client = InferenceClient(model="cardiffnlp/twitter-roberta-base-sentiment-latest", token=api_key)
        result = client.text_classification("This product is really good and I love using it every day!")
        print(f"Result: {result}")

        # Test language detection
        print("\n=== Testing Language Detection ===")
        client = InferenceClient(model="papluca/xlm-roberta-base-language-detection", token=api_key)
        result = client.text_classification("こんにちは、今日はいい天気ですね。")
        print(f"Result: {result}")

        # Test text generation
        print("\n=== Testing Text Generation ===")
        client = InferenceClient(model="microsoft/DialoGPT-medium", token=api_key)
        result = client.text_generation("Hello, how are you?", max_new_tokens=50)
        print(f"Result: {result}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_inference_client()