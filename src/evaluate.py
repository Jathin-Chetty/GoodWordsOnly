import torch
from sklearn.metrics import accuracy_score, f1_score
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from src.dataset import get_dataset
from src.config import Config


dataset = get_dataset()

model = AutoModelForSequenceClassification.from_pretrained("outputs/model")
model.eval()

tokenizer = AutoTokenizer.from_pretrained(Config.MODEL_NAME)

preds = []
labels = []

for i in range(500):  # sample evaluation
    item = dataset[i]

    input_ids = item["input_ids"].unsqueeze(0)
    attention_mask = item["attention_mask"].unsqueeze(0)

    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        pred = torch.argmax(outputs.logits, dim=1).item()

    preds.append(pred)
    labels.append(item["labels"].item())

print("Accuracy:", accuracy_score(labels, preds))
print("F1 Score:", f1_score(labels, preds))