import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load the .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in .env file")
else:
    print(f"API Key found: {api_key[:10]}...")
    genai.configure(api_key=api_key)
    
    print("\nFetching available models for your API key...")
    try:
        models = genai.list_models()
        embedding_models = [m.name for m in models if 'embedContent' in m.supported_generation_methods]
        
        print("\n--- AVAILABLE EMBEDDING MODELS ---")
        for model_name in embedding_models:
            print(f"- {model_name}")
            
        if not embedding_models:
            print("NO embedding models found. Your API key might be restricted or the Generative Language API is not enabled.")
    except Exception as e:
        print(f"ERROR fetching models: {e}")