import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from src.config import Config
from src.fewshot_data import get_few_shot_data


device = Config.DEVICE

texts, labels = get_few_shot_data(k=8)

tokenizer = AutoTokenizer.from_pretrained(Config.MODEL_NAME)


class FewShotDataset(Dataset):
    def __init__(self, texts, labels):
        self.texts = texts
        self.labels = labels

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        enc = tokenizer(
            self.texts[idx],
            padding="max_length",
            truncation=True,
            max_length=Config.MAX_LENGTH,
            return_tensors="pt"
        )

        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels": torch.tensor(self.labels[idx], dtype=torch.long)
        }


dataset = FewShotDataset(texts, labels)
loader = DataLoader(dataset, batch_size=4, shuffle=True)


# =========================
# LOAD MODEL
# =========================
model = AutoModelForSequenceClassification.from_pretrained("outputs/model").to(device)

# 🔥 FREEZE BASE MODEL
for param in model.base_model.parameters():
    param.requires_grad = False

optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
loss_fn = torch.nn.CrossEntropyLoss()


# =========================
# TRAIN
# =========================
epochs = 5

for epoch in range(epochs):
    model.train()
    total_loss = 0

    for batch in loader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        loss = loss_fn(outputs.logits, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Few-shot Epoch {epoch+1}, Loss: {total_loss:.4f}")


model.save_pretrained("outputs/model_fewshot")
print("Few-shot model saved!")