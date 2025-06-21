# 📘 DefineMe.md — Concepts Behind UFSM RAG

This document defines and explains key mathematical and conceptual foundations of Retrieval-Augmented Generation (RAG), focusing on **embeddings**, **vector similarity**, and **vector database storage**.

---

## 📑 Table of Contents

- [🧠 Embeddings](#-embeddings)
  - [🔤 What is an Embedding?](#-what-is-an-embedding)
  - [📐 Embedding as a Vector](#-embedding-as-a-vector)
  - [📏 Measuring Similarity: Cosine Distance](#-measuring-similarity-cosine-distance)
  - [📊 Embeddings in Vector Space (Diagram)](#-embeddings-in-vector-space-diagram)
  - [✍️ Why Chunking Improves Embedding Quality](#️-why-chunking-improves-embedding-quality)
  - [🧮 Vector Distance: Similar vs Dissimilar Texts](#-vector-distance-similar-vs-dissimilar-texts)
  - [🧬 Eigenvectors and Vector Projections](#-eigenvectors-and-vector-projections)
  - [📉 SVD vs PCA for Embedding Reduction](#-svd-vs-pca-for-embedding-reduction)
  - [📈 t-SNE / UMAP Visualizations](#-t-sne--umap-visualizations)
  - [📐 Angular vs Euclidean Distance in High Dimensions](#-angular-vs-euclidean-distance-in-high-dimensions)
- [💾 Vector Databases](#-vector-databases)
  - [💾 How a Vector is Stored in Qdrant](#-how-a-vector-is-stored-in-qdrant)
  - [🔁 Vector Indexes in Practice](#-vector-indexes-in-practice)
  - [🕸️ HNSW Internals (Hierarchical Navigable Small World)](#️-hnsw-internals-hierarchical-navigable-small-world)
- [🎯 Semantic Search](#-semantic-search)
  - [🎯 Metric Learning (Why Some Distances Work Better)](#-metric-learning-why-some-distances-work-better)
  - [🔍 When a User Asks a Question](#-when-a-user-asks-a-question)
- [🔮 Coming Next](#-coming-next)

---

## 🧠 Embeddings

### 🔤 What is an Embedding?

An **embedding** is a numerical representation of a text (sentence, document, word) in a continuous vector space.

- Embeddings allow **semantic similarity** to be computed as **vector distance**.
- Generated using language models like OpenAI (`text-embedding-3-small`), HuggingFace Transformers, etc.

---

### 📐 Embedding as a Vector

An embedding is a list of floating-point numbers. For example:

```python
[0.041, -0.238, 0.501, ..., 0.019]
```

- Typical size: 384, 768, 1536, or 3072 dimensions depending on model.

---

### 📏 Measuring Similarity: Cosine Distance

Let vectors **A** and **B** represent two texts. Their similarity is:

```math
cos(θ) = (A · B) / (||A|| * ||B||)
```

- `A · B` is the dot product
- `||A||` and `||B||` are vector magnitudes

```math
cosine_distance = 1 - cosine_similarity
```

---

### 📊 Embeddings in Vector Space (Diagram)

Imagine texts placed in a 3D space (simplified):

```
           📘 Text A ("How to enroll")
              *
             / \
            /   \
           *     * 📙 Text B ("Steps to register")
          📕 Text C ("Pizza toppings")
```

- Text A and B are **close**, high semantic similarity
- Text C is **far**, different topic
- In actual models this occurs in 1536D space, not 3D

---

### ✍️ Why Chunking Improves Embedding Quality

**Chunking** breaks long texts into smaller segments, helping in:

- Preserving context size within LLM token limits
- Enhancing vector precision (more specific = better embeddings)
- Avoiding dilution: "big blobs" often confuse the embedding model

Example:

```
Long text (bad):
"UFSM offers many courses including architecture, law, biology..."

Chunked (good):
"Architecture is a course at UFSM focused on..."

"Law at UFSM prepares students for..."

"Biology involves research on ecosystems..."
```

---

### 🧮 Vector Distance: Similar vs Dissimilar Texts

Let’s compare cosine distances:

| Text A vs B                                    | Cosine Distance |
|------------------------------------------------|------------------|
| "How to apply for architecture?" vs "How to enroll in UFSM?" | **0.12** *(very close)* |
| "Architecture course details" vs "Pizza recipe instructions" | **0.87** *(very far)* |

Lower = closer in meaning.  
Higher = semantically different.

---

### 🧬 Eigenvectors and Vector Projections

While embeddings are high-dimensional vectors, they can be understood through linear algebra.

- **Eigenvectors** describe the *directions* along which transformations (like PCA or matrix ops) scale without rotating.
- In embeddings, **principal components** can be derived using eigenvectors of the covariance matrix — useful for visualization and compression.

#### 🔢 Projection onto Direction

Project vector **v** onto direction **u** (unit vector):

```math
proj_u(v) = (v · u) * u
```

---

### 📉 SVD vs PCA for Embedding Reduction

## 🔹 SVD — Singular Value Decomposition

Uma técnica matemática geral que decompõe qualquer matriz em três partes:

```math
X = U · Σ · Vᵀ
```

- **X**: matriz original (ex: embeddings de documentos)
- **U**: vetores ortogonais que representam direções dos dados
- **Σ**: valores singulares — quanto cada direção contribui
- **Vᵀ**: rotação e alinhamento final

✅ Usado em álgebra linear para compressão, redução de ruído, recomendação, etc.  
✅ Pode ser aplicado mesmo em matrizes não centradas ou retangulares.

---

## 🔹 PCA — Principal Component Analysis

Uma técnica estatística que identifica as direções com maior variância nos dados (componentes principais).

- PCA encontra **vetores próprios (eigenvectors)** da matriz de covariância dos dados.
- Esses vetores **maximizam a variação** dos dados projetados.
- Funciona basicamente como um **SVD da matriz centrada** (X - média).

✅ PCA é um **caso específico de SVD**, onde os dados são centrados e reduzidos a componentes mais informativos.

---

## 🧠 Na prática para embeddings:

|                     | PCA         | SVD         |
|---------------------|-------------|-------------|
| Para dados centrados| ✅ Ideal    | ✅ Funciona |
| Dados esparsos      | ❌ Não ideal| ✅ Sim      |
| Redução de dimensões| ✅ Sim      | ✅ Sim      |
| Interpretação estatística | ✅ Boa | ❌ Matemática apenas |
---
**Overview**
| Method | Description |
|--------|-------------|
| **PCA** | Finds directions (principal components) that maximize variance. |
| **SVD** | General matrix decomposition: X = UΣVᵗ. More flexible than PCA. |

Used to reduce high-dimensional embeddings into fewer, denser dimensions for performance or visualization.

---

### 📈 t-SNE / UMAP Visualizations

**t-SNE** and **UMAP** are nonlinear dimensionality reduction techniques for visualizing embeddings.

| Method | Notes |
|--------|-------|
| t-SNE  | Great for local structure, less on global | 
| UMAP   | Better balance between local/global, faster |

---

### 📐 Angular vs Euclidean Distance in High Dimensions

| Feature         | Cosine         | Euclidean     |
|----------------|----------------|---------------|
| Magnitude-sensitive | ❌ No           | ✅ Yes         |
| Direction-sensitive | ✅ Yes         | ✅ Yes         |
| Works well in NLP   | ✅ Yes         | ❌ No          |
| RAG-recommended     | ✅ Yes         | ❌ Not ideal   |

---

## 💾 Vector Databases

### 💾 How a Vector is Stored in Qdrant

```json
{
  "id": 3281,
  "vector": [0.041, -0.238, 0.501, ...],
  "payload": {
    "curso": "Arquitetura e Urbanismo",
    "source": "https://www.ufsm.br/...",
    "text": "...",
    "timestamp": "2025-06-20T14:30:00"
  }
}
```

---

### 🔁 Vector Indexes in Practice

| Index Type | Description                                      |
|------------|--------------------------------------------------|
| HNSW       | Hierarchical Navigable Small World (graph-based) |
| IVF        | Inverted File Index (clustered)                  |
| Flat       | Brute-force (slow but exact)                     |

---

### 🕸️ HNSW Internals (Hierarchical Navigable Small World)

- Multi-layer graph for fast approximate search
- Greedy traversal from top-level entry point down
- Tunable via: `ef_construction`, `ef_search`, `m`

---

## 🎯 Semantic Search

### 🎯 Metric Learning (Why Some Distances Work Better)

Trains embedding models so that **semantic similarity = geometric closeness**.

| Type            | Description |
|-----------------|-------------|
| Supervised      | Learns from labeled pairs |
| Self-supervised | Contrastive learning (e.g. BERT-NLI, SimCLR) |

---

### 🔍 When a User Asks a Question

1. Question is embedded into a vector.
2. Qdrant retrieves nearest chunks.
3. Context is passed to LLM (e.g., GPT).
4. Response is generated grounded in context.

---

## 🔮 Coming Next

Would you like the next section to cover:

- 🧱 Embedding compression strategies?
- 🧲 Retrieval performance tuning?
- 🎯 Evaluation metrics for RAG (Precision@K, Exact Match, Recall@K)?

Let me know and I’ll add the next block!
