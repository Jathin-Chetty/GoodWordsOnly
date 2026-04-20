from transformers import AutoModelForSequenceClassification
from src.config import Config


def get_model():
    model = AutoModelForSequenceClassification.from_pretrained(
        Config.MODEL_NAME,
        num_labels=Config.NUM_LABELS
    )
    return model