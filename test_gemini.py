from app.gemini_client import generate_with_fallback


response = generate_with_fallback(
    "Say hello in one sentence.",
    config={
        "temperature": 0.2,
        "tools": []
    }
)

print("\n====================")
print("GEMINI RESPONSE")
print("====================")

print(response.text)