from google import genai

from app.core.config import get_settings

settings = get_settings()
if not settings.gemini_api_key:
    raise SystemExit("GEMINI_API_KEY is missing in backend/.env")

client = genai.Client(api_key=settings.gemini_api_key)

print("Models your key can use for generating text:\n")
for model in client.models.list():
    actions = getattr(model, "supported_actions", None) or []
    if "generateContent" in actions:
        print(model.name.replace("models/", ""))