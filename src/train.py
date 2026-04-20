import torch
from transformers import TrainingArguments, Trainer

from src.config import Config
from src.dataset import get_dataset
from src.model import get_model


# =========================
# LOAD DATA
# =========================
full_dataset = get_dataset()

train_size = int(0.8 * len(full_dataset))
val_size = len(full_dataset) - train_size

train_dataset, val_dataset = torch.utils.data.random_split(
    full_dataset, [train_size, val_size]
)

print(f"Train size: {len(train_dataset)}")
print(f"Validation size: {len(val_dataset)}")


# =========================
# MODEL
# =========================
model = get_model()


# =========================
# TRAINING CONFIG (FULLY COMPATIBLE)
# =========================
training_args = TrainingArguments(
    output_dir="outputs/model",
    per_device_train_batch_size=Config.BATCH_SIZE,
    per_device_eval_batch_size=Config.BATCH_SIZE,
    num_train_epochs=Config.EPOCHS,
    learning_rate=Config.LEARNING_RATE,
    logging_steps=50,
    save_steps=500
)


# =========================
# TRAINER
# =========================
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)


# =========================
# TRAIN
# =========================
trainer.train()


# =========================
# SAVE MODEL
# =========================
trainer.save_model("outputs/model")
print("Model saved successfully!")