"""
Train a document classifier model for invoice, CV, ID card, and receipt classification.
Run this script to generate the classifier.pkl model file.
"""
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import numpy as np

# Sample training data (in production, you'd have much more data)
training_data = [
    # Invoices
    ("Invoice Number INV-001 Date 01/15/2024 Total Amount $1,500.00 Tax $150.00 Company ABC Traders", "invoice"),
    ("INVOICE Company XYZ Corp Date: 03/22/2024 Subtotal: $2,300 Tax: $230 Total: $2,530", "invoice"),
    ("Bill To: Customer Name Invoice #12345 Date: 05/10/2024 Amount Due: $4,200.00", "invoice"),
    ("Invoice Date 06/15/2024 Invoice Total $890.50 Tax $89.05 Company Tech Solutions", "invoice"),
    ("Purchase Order Total $3,450 Tax $345 Invoice Date 07/20/2024", "invoice"),
    
    # CVs/Resumes
    ("John Doe Skills: Python, JavaScript, React Experience: 5 years Education: Computer Science", "cv"),
    ("Resume Software Engineer Skills Java Python AWS 8 years experience Bachelor's Degree", "cv"),
    ("CV Name: Jane Smith Programming Languages: C++, Go, Rust 3+ years professional experience", "cv"),
    ("Professional Summary 10 years experience Skills: Machine Learning, AI, Deep Learning PhD", "cv"),
    ("Technical Skills Python Django Flask PostgreSQL 6 years software development", "cv"),
    
    # ID Cards
    ("National ID Card Name: Michael Brown Date of Birth: 01-05-1990 Address: 123 Main St", "id_card"),
    ("Driver License Name John Smith DOB 03-15-1985 Address 456 Oak Avenue", "id_card"),
    ("Identity Card Full Name: Sarah Johnson Date of Birth: 12-25-1992 Residential Address", "id_card"),
    ("Passport Name Robert Wilson Date of Birth 07-10-1988 Place of Birth New York", "id_card"),
    ("ID Number 123456789 Name David Lee DOB 09-20-1995 Address 789 Pine Road", "id_card"),
    
    # Receipts
    ("Receipt Store: SuperMart Date: 08/01/2024 Total: $45.67 Thank you for shopping", "receipt"),
    ("RECEIPT Grocery Store Items purchased Total Amount $67.89 Date 08/15/2024", "receipt"),
    ("Purchase Receipt Restaurant Name Total $125.00 Date 08/20/2024 Payment: Credit Card", "receipt"),
    ("Receipt Coffee Shop Date 08/25/2024 Amount $8.50 Transaction ID 98765", "receipt"),
    ("Store Receipt Gas Station Total $52.30 Date 08/30/2024 Payment Method Cash", "receipt"),
]

def train_classifier():
    """Train and save the document classifier model."""
    
    # Separate texts and labels
    texts = [text for text, label in training_data]
    labels = [label for text, label in training_data]
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=1000,
        ngram_range=(1, 2),
        stop_words='english',
        lowercase=True
    )
    
    # Train vectorizer
    X = vectorizer.fit_transform(texts)
    
    # Train classifier
    classifier = MultinomialNB(alpha=0.1)
    classifier.fit(X, labels)
    
    # Create model directory if it doesn't exist
    os.makedirs("app/model_artifacts", exist_ok=True)
    
    # Save model and vectorizer
    model_path = "app/model_artifacts/classifier.pkl"
    with open(model_path, "wb") as f:
        pickle.dump((classifier, vectorizer), f)
    
    print(f"✅ Model trained and saved to {model_path}")
    print(f"   Classes: {classifier.classes_}")
    print(f"   Training samples: {len(training_data)}")
    
    # Test predictions
    print("\n🧪 Testing predictions:")
    test_samples = [
        "Invoice Total $500 Tax $50 Company ABC",
        "Skills Python Java 5 years experience",
        "Name John Doe DOB 01-01-1990",
        "Receipt Total $25.50 Thank you"
    ]
    
    for sample in test_samples:
        vec = vectorizer.transform([sample])
        prediction = classifier.predict(vec)[0]
        probabilities = classifier.predict_proba(vec)[0]
        confidence = max(probabilities)
        print(f"   '{sample[:40]}...' → {prediction} ({confidence:.2%})")

if __name__ == "__main__":
    train_classifier()
