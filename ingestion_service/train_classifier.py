import json
import os
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

LOG_PATH = "logs/reranker_log.jsonl"
MODEL_PATH = "models/router_classifier.joblib"

def load_data(log_path):
    questions = []
    labels = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                questions.append(entry["question"])
                labels.append(entry["selected_collection"])
            except Exception as e:
                print(f"⚠️ Skipping line due to error: {e}")
    return questions, labels

def train_model():
    print("📚 Carregando dados do log...")
    X, y = load_data(LOG_PATH)

    print(f"✅ Total de amostras: {len(X)}")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("🧠 Treinando pipeline TF-IDF + LogisticRegression...")
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1,2), max_features=3000)),
        ("clf", LogisticRegression(max_iter=1000))
    ])
    pipe.fit(X_train, y_train)

    score = pipe.score(X_test, y_test)
    print(f"🎯 Acurácia no conjunto de teste: {score:.4f}")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(pipe, MODEL_PATH)
    print(f"💾 Modelo salvo em {MODEL_PATH}")

if __name__ == "__main__":
    train_model()