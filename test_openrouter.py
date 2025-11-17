from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

response = client.chat.completions.create(
    model="google/gemma-7b-it:free",  # Бесплатная модель
    messages=[{"role": "user", "content": "Привет! Скажи привет в ответ"}],
)

print("Ответ:", response.choices[0].message.content)