import random
from src.dataset import load_data


def get_few_shot_data(k=8):
    texts, labels = load_data()

    hate = []
    non_hate = []

    for t, l in zip(texts, labels):
        if l == 1:
            hate.append((t, l))
        else:
            non_hate.append((t, l))

    # shuffle
    random.shuffle(hate)
    random.shuffle(non_hate)

    # pick k samples each
    few_shot = hate[:k] + non_hate[:k]

    random.shuffle(few_shot)

    texts = [x[0] for x in few_shot]
    labels = [x[1] for x in few_shot]

    print(f"Few-shot dataset size: {len(texts)}")

    return texts, labels