# Multilingual Hate Speech Detection

A machine learning project for detecting hate speech in text using a fine-tuned DistilBERT multilingual model. The project includes training scripts, evaluation tools, and a web interface for real-time predictions.

## Features

- Multilingual hate speech detection using DistilBERT
- Support for few-shot learning scenarios
- Web application with Flask for interactive predictions
- Model comparison and evaluation tools
- Binary classification (hate speech vs. non-hate speech)

## Project Structure

```
.
├── data/
│   ├── raw/              # Raw labeled data
│   └── processed/        # Processed datasets
├── outputs/              # Saved models and results
├── src/
│   ├── config.py         # Configuration settings
│   ├── dataset.py        # Dataset loading and preprocessing
│   ├── model.py          # Model architecture
│   ├── train.py          # Training script
│   ├── fewshot_train.py  # Few-shot learning training
│   ├── evaluate.py       # Model evaluation
│   ├── predict.py        # Prediction utilities
│   ├── compare.py        # Model comparison tools
│   ├── fewshot_data.py   # Few-shot data handling
│   └── multilingual_data.py  # Multilingual data utilities
├── webapp/
│   ├── app.py            # Flask application
│   ├── static/           # CSS and JavaScript
│   └── templates/        # HTML templates
└── venv/                 # Virtual environment
```

## Requirements

- Python 3.7+
- PyTorch
- Transformers (Hugging Face)
- Flask
- pandas
- scikit-learn

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install torch transformers flask pandas scikit-learn
```

## Usage

**Note:** The pre-trained model weights are already provided in the repository via Git LFS. You do **not** need to train the model to run predictions or the web application. You can use it right out of the box!

### Running the Web Application

Start the Flask web server:

```bash
python webapp/app.py
```

Then open your browser and navigate to `http://localhost:5000`

### Use a Hugging Face Public Model Locally

The web app now runs local `transformers` inference and downloads model files from the Hub
on first run (or uses cache after that).

- Default model: `IMSyPP/hate_speech_multilingual`
- Override model: set `HF_MODEL`
- `HF_TOKEN` is not required for public models

Example:

```bash
export HF_MODEL="IMSyPP/hate_speech_multilingual"
python webapp/app.py
```

### Deploy on Vercel (API + Frontend)

This repo now includes:

- Static frontend at project root (`index.html`, `app.js`, `style.css`)
- Serverless API at `api/predict.js`

Set these environment variables in Vercel project settings:

- `HF_MODEL` = `IMSyPP/hate_speech_multilingual`
- `HF_TOKEN` = your Hugging Face access token (recommended)

After setting env vars, import this GitHub repo into Vercel and deploy.

### Optional: Training the Model

If you wish to fine-tune the model on your own dataset, train it using the standard training script:

```bash
python -m src.train
```

For few-shot learning scenarios:

```bash
python -m src.fewshot_train
```

### Evaluating the Model

Evaluate model performance:

```bash
python -m src.evaluate
```

### Making Predictions

Use the prediction script:

```bash
python -m src.predict
```

## Configuration

Edit `src/config.py` to customize:

- Model architecture (default: `distilbert-base-multilingual-cased`)
- Training hyperparameters (batch size, epochs, learning rate)
- Data paths
- Maximum sequence length
- Device (CPU/GPU)

## Model Details

- **Base Model**: DistilBERT Multilingual (cased)
- **Task**: Binary sequence classification
- **Labels**: 
  - 0: Non-hate speech
  - 1: Hate speech
- **Max Sequence Length**: 128 tokens
- **Training**: Fine-tuned on labeled tweet data with multilingual augmentation

## Data Format

The training data should be in CSV format with the following columns:
- `tweet`: The text content
- `class`: The label (2 for non-hate speech, other values for hate speech)

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Contact

[Add contact information here]
