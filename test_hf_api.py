import requests
import sys

API_URL = "https://api-inference.huggingface.co/models/Jathin-ch/hate_speech_multilingual"
headers = {} # No token for now, let's see if it works at all

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

output = query({"inputs": "I hate you so much!"})
print("Result for Jathin-ch:", output)

API_URL2 = "https://api-inference.huggingface.co/models/IMSyPP/hate_speech_multilingual"
output2 = requests.post(API_URL2, headers=headers, json={"inputs": "I hate you so much!"}).json()
print("Result for IMSyPP:", output2)
