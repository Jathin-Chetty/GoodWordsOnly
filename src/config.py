import torch

class Config:
    # paths
    DATA_PATH = "data/raw/labeled_data.csv"
    MODEL_SAVE_PATH = "outputs/model/"

    # model
    MODEL_NAME = "distilbert-base-multilingual-cased"
    MAX_LENGTH = 128

    # training
    BATCH_SIZE = 16
    EPOCHS = 3
    LEARNING_RATE = 2e-5

    # device
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    # labels
    NUM_LABELS = 2