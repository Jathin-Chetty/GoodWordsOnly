import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer
from src.config import Config
from src.multilingual_data import get_multilingual_data


class HateDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            str(self.texts[idx]),
            padding="max_length",
            truncation=True,
            max_length=Config.MAX_LENGTH,
            return_tensors="pt"
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels": torch.tensor(self.labels[idx], dtype=torch.long)
        }


def load_data():
    # =========================
    # LOAD ENGLISH DATA
    # =========================
    df = pd.read_csv(Config.DATA_PATH)

    df["label"] = df["class"].apply(lambda x: 0 if x == 2 else 1)

    texts = df["tweet"].tolist()
    labels = df["label"].tolist()

    # =========================
    # ADD MULTILINGUAL DATA
    # =========================
    multi_texts, multi_labels = get_multilingual_data()

    texts.extend(multi_texts)
    labels.extend(multi_labels)

    print(f"Total dataset size (with multilingual): {len(texts)}")

    return texts, labels


def get_dataset():
    texts, labels = load_data()
    tokenizer = AutoTokenizer.from_pretrained(Config.MODEL_NAME)
    return HateDataset(texts, labels, tokenizer)