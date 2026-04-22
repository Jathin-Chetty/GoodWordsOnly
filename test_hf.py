import requests

model = "IMSyPP/hate_speech_multilingual"
url1 = f"https://api-inference.huggingface.co/models/{model}"
url2 = f"https://router.huggingface.co/hf-inference/models/{model}"

headers = {"Content-Type": "application/json"}
payload = {"inputs": "I hate you"}

print("Testing url1:", url1)
r1 = requests.post(url1, headers=headers, json=payload)
print(r1.status_code, r1.text)

print("Testing url2:", url2)
r2 = requests.post(url2, headers=headers, json=payload)
print(r2.status_code, r2.text)
