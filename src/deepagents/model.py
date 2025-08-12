import os
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA


def get_default_model():
    """Return the default chat model used by DeepAgents.

    Defaults to NVIDIA's GPT-OSS 20B via the LangChain NVIDIA AI Endpoints integration.
    Reads API key from environment (preferred), but can also work if the NVIDIA
    client is configured globally.
    """

    # Load environment variables from a .env file if present
    load_dotenv()

    # Prefer environment variables rather than hardcoding secrets
    api_key = os.getenv("NVIDIA_API_KEY")
    

    init_kwargs = {
        "model": "openai/gpt-oss-20b",
        "api_key": api_key,
        "temperature": 1,
        "top_p": 1,
        "max_tokens": 4096,
    }

    return ChatNVIDIA(**init_kwargs)
