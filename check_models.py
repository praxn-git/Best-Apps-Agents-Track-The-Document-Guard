import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1",
    api_key=os.getenv("NEBIUS_API_KEY")
)

# Fetching all models currently active on my Nebius token factory account
models = client.models.list()
for model in models.data:
    if "nvidia" in model.id.lower() or "nemotron" in model.id.lower():
        print(f"MATCH: {model.id}")