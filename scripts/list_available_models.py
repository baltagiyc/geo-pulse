#!/usr/bin/env python3
"""
List available LLM models for OpenAI and Google Gemini.

This script helps verify which models are available with your API keys.
Run with: uv run python scripts/list_available_models.py
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv()


def list_openai_models():
    """List available OpenAI models."""
    print("=" * 60)
    print("OpenAI Models")
    print("=" * 60)

    try:
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY not found in environment variables")
            return

        client = OpenAI(api_key=api_key)

        # List models
        models = client.models.list()
        print(f"✅ Found {len(models.data)} models\n")

        # Filter and display relevant models
        relevant_models = [
            model
            for model in models.data
            if any(
                keyword in model.id.lower()
                for keyword in ["gpt-4", "gpt-3.5", "gpt-5", "o1", "o3"]
            )
        ]

        if relevant_models:
            print("Relevant models (GPT-4, GPT-5, O1, O3):")
            for model in sorted(relevant_models, key=lambda x: x.id):
                print(f"  • {model.id}")
                if hasattr(model, "created"):
                    print(f"    Created: {model.created}")
        else:
            print("No relevant GPT models found")

        print()

    except ImportError:
        print("❌ openai package not installed.")
        print("   Note: langchain-openai might include it. Try: uv add openai")
    except Exception as e:
        print(f"❌ Error listing OpenAI models: {e}\n")


def list_google_models():
    """List available Google Gemini models."""
    print("=" * 60)
    print("Google Gemini Models")
    print("=" * 60)

    try:
        import google.generativeai as genai

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in environment variables")
            return

        genai.configure(api_key=api_key)

        print("✅ Listing models with 'generateContent' support:\n")

        models = list(genai.list_models())
        if not models:
            print("❌ No models found")
            return

        for m in models:
            if "generateContent" in m.supported_generation_methods:
                print(f"Name: {m.name}")
                if hasattr(m, "display_name") and m.display_name:
                    print(f"Display Name: {m.display_name}")
                if hasattr(m, "description") and m.description:
                    print(f"Description: {m.description}")
                print("-" * 40)

    except ImportError:
        print("❌ google-generativeai package not installed.")
        print("   Install with: uv add google-generativeai")
        print("   Note: This is separate from langchain-google-genai")
    except Exception as e:
        print(f"❌ Error listing Google models: {e}\n")


def main():
    """Main function to list all available models."""
    print("\n🔍 Checking available LLM models...\n")

    list_openai_models()
    list_google_models()

    print("=" * 60)
    print("✅ Done!")
    print("=" * 60)
    print("\n💡 Tip: Use these model names in your llm_factory.py mapping")


if __name__ == "__main__":
    main()
