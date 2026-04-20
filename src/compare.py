import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from src.config import Config

device = Config.DEVICE

tokenizer = AutoTokenizer.from_pretrained(Config.MODEL_NAME)

# load both models
base_model = AutoModelForSequenceClassification.from_pretrained("outputs/model").to(device)
fewshot_model = AutoModelForSequenceClassification.from_pretrained("outputs/model_fewshot").to(device)

base_model.eval()
fewshot_model.eval()


def predict(model, text):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=Config.MAX_LENGTH
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)
        return probs[0][1].item()


texts = [
    "You are a disgusting human",
    "I will destroy you",
    "You are very kind",
    "I hate your existence",
    "Have a nice day"
]

print("\n===== COMPARISON =====\n")

for t in texts:
    base = predict(base_model, t)
    few = predict(fewshot_model, t)

    print(f"{t}")
    print(f"  BEFORE: {base:.2f}")
    print(f"  AFTER : {few:.2f}")
    print()