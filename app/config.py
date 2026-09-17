import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model


load_dotenv()

if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY"):
    raise RuntimeError(
        "Falta GOOGLE_API_KEY. Copia .env.example a .env y agrega tu clave de Google AI Studio."
    )


model = init_chat_model(
    "gemini-2.5-flash",
    model_provider="google_genai",
    temperature=0,
)