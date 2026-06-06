import requests
import json

url = "http://localhost:4000/v1/chat/completions"
headers = {"Content-Type": "application/json"}

data = {
    "model": "local-llama",
    "messages": [
        {"role": "user", "content": "Hello! Give me a 1-sentence definition of what an MLOps engineer does."}
    ]
}

print("Sending request to our Dockerized LiteLLM Gateway...")
try:
    response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
    if response.status_code == 200:
        print("\n--- Response from Local Llama Model ---")
        print(response.json()['choices'][0]['message']['content'])
    else:
        print(f"Gateway Error Code: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"\nCould not connect to gateway: {e}")
