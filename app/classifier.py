import pickle
import os
try:
    from .config import CLASSIFIER_MODEL_PATH
except ImportError:
    from config import CLASSIFIER_MODEL_PATH

model = None
vectorizer = None

def load_model():
    """Load the classifier model if not already loaded."""
    global model, vectorizer
    if model is None:
        if not os.path.exists(CLASSIFIER_MODEL_PATH):
            raise FileNotFoundError(
                f"Classifier model not found at {CLASSIFIER_MODEL_PATH}. "
                "Run 'python app/train_classifier.py' to train the model."
            )
        with open(CLASSIFIER_MODEL_PATH, "rb") as f:
            model, vectorizer = pickle.load(f)

def classify_document(text: str):
    """Classify document type and return prediction with confidence."""
    load_model()
    vec = vectorizer.transform([text])
    pred = model.predict(vec)[0]
    probabilities = model.predict_proba(vec)[0]
    confidence = float(max(probabilities))
    return pred, confidence
