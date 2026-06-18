import requests
import json
import csv
import os

# ================== НАСТРОЙКИ ==================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your_openrouter_api_key_here")

MODEL = "openrouter/free"
URL = "https://openrouter.ai/api/v1/chat/completions"


def call_llm(prompt: str):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 0.3,
        "max_tokens": 900
    }

    try:
        response = requests.post(URL, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"❌ Ошибка API {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return None


# ===================== ОСНОВНОЙ КОД =====================

# Читаем отзывы
reviews = []
with open('reviews.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        reviews.append(row)

print(f"Загружено {len(reviews)} отзывов\n")

results = []
for review in reviews:
    prompt = f"""Проанализируй отзыв на русском языке:

"{review['review_text']}"

Верни **только** чистый JSON без каких-либо комментариев:

{{
  "id": {review.get('id', 'unknown')},
  "sentiment": "positive" | "negative" | "neutral",
  "topic": "основные темы через запятую",
  "summary": "подробное краткое содержание отзыва (2-4 предложения)",
  "pros": ["список преимуществ"],
  "cons": ["список недостатков"]
}}
"""

    print(f"Обработка отзыва {review.get('id')}...")
    llm_response = call_llm(prompt.strip())

    if llm_response:
        try:
            parsed = json.loads(llm_response)
            results.append(parsed)
            print(f"✓ Успешно: {parsed.get('sentiment', 'N/A')}")
        except json.JSONDecodeError:
            results.append({
                "id": review.get('id'),
                "error": "JSON parse failed",
                "raw": llm_response[:500]
            })
            print("⚠️ Ошибка парсинга JSON")
    else:
        results.append({"id": review.get('id'), "error": "LLM request failed"})

# Сохранение результата
with open('results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n🎉 Готово! Результат сохранён в results.json")