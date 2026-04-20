import os
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, TextClassificationPipeline

HF_MODEL = os.getenv("HF_MODEL", "IMSyPP/hate_speech_multilingual")

# Label order follows the model card from the original model.
LABEL_NAMES = {
    "LABEL_0": "Appropriate",
    "LABEL_1": "Inappropriate",
    "LABEL_2": "Offensive",
    "LABEL_3": "Violent",
}

_pipeline = None


def _get_pipeline():
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(HF_MODEL)

    # Transformers pipeline uses -1 for CPU, >=0 for CUDA GPU index.
    device = 0 if torch.cuda.is_available() else -1
    _pipeline = TextClassificationPipeline(
        model=model,
        tokenizer=tokenizer,
        top_k=None,
        task="sentiment_analysis",
        function_to_apply="softmax",
        device=device,
    )
    return _pipeline


def _normalize_scores(raw_output):
    """
    Normalize Hugging Face inference output into a sorted list:
    [{"label": str, "display_label": str, "score": float}, ...]
    """
    if not isinstance(raw_output, list) or not raw_output:
        raise ValueError("Unexpected model response format")

    # HF text-classification can return either:
    # - [{"label": "...", "score": ...}] or
    # - [[{"label": "...", "score": ...}, ...]] with return_all_scores=True
    if isinstance(raw_output[0], list):
        scores = raw_output[0]
    else:
        scores = raw_output

    normalized = []
    for item in scores:
        if not isinstance(item, dict):
            continue
        label = item.get("label")
        score = float(item.get("score", 0.0))
        if not label:
            continue
        normalized.append(
            {
                "label": label,
                "display_label": LABEL_NAMES.get(label, label.replace("_", " ").title()),
                "score": score,
            }
        )

    if not normalized:
        raise ValueError("Model returned no class scores")

    return sorted(normalized, key=lambda x: x["score"], reverse=True)


def predict(text):
    try:
        classifier = _get_pipeline()
        response_data = classifier(text)
    except Exception as err:
        raise RuntimeError(f"Local model inference failed: {err}") from err

    classes = _normalize_scores(response_data)
    top = classes[0]

    return {
        "model": HF_MODEL,
        "label": top["label"],
        "display_label": top["display_label"],
        "probability": top["score"],
        "classes": classes,
    }