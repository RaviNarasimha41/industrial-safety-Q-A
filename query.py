import requests

url = "http://127.0.0.1:8000/ask"
payload = {
    "q": "What are the key safety requirements for machines?",
    "k": 3,
    "mode": "hybrid"
}

response = requests.post(url, json=payload)
data = response.json()

print("Answer:", data["answer"])
print("\nSources:")
for ctx in data["contexts"]:
    print(f"- {ctx['source_title']}: {ctx['source_url']}")
