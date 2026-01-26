# VIZJA-TECH E-commerce Store (AI-Powered)

A professional, high-performance Django e-commerce platform designed for computer hardware. This project distinguishes itself by using **AI-driven Semantic Search** and **Vector Database** technology to provide a modern shopping experience.

## 🚀 Advanced Features
* **AI Semantic Search:** Implements the `all-MiniLM-L6-v2` Transformer model to understand the *intent* behind user queries (e.g., searching "gaming visuals" finds Graphics Cards).
* **Vector Database:** Powered by **PostgreSQL** and the `pgvector` extension to store and query 384-dimensional embeddings.
* **Hybrid Search Logic:** Combines Natural Language Processing (NLP) with traditional keyword matching and price filtering.
* **Domain-Specific Spellcheck:** Custom "Did you mean?" logic that prioritizes hardware terminology (e.g., correcting "maniter" to "monitor" instead of "matter").
* **Professional Storefront:** Category management, product tracking, shopping cart, and secure checkout processing.

---

## 💻 Developer Cheat Sheet (Installation & Setup)

### 1. Environment Management
To activate your virtual environment:
source env/Scripts/activate

### 2. Install Dependencies
pip install -r requirements.txt

### 3. Database Initialization
Ensure PostgreSQL is running with the pgvector extension enabled, then run:
python manage.py migrate

### 4. AI Model Initialization
To generate the AI embeddings for the product catalog, you must trigger the save method in the Django shell:
python manage.py shell
# Inside the shell, run:
from store.models import Product
for p in Product.objects.all():
    p.save()
exit()

### 5. Run Server
python manage.py runserver


📁 Technical Project Structure
store/: The core "Smart" module.

models.py: Defines the VectorField for 384-D embeddings.

views.py: Contains the Hybrid Retrieval logic and Cosine Distance calculations.

accounts/: Custom user model (Account) with email-based authentication.

carts/ & orders/: Logic for session-based shopping and order fulfillment.

category/: Organizational structure for the hardware catalog.

🎓 Academic Implementation Details
Model: Sentence-Transformers (BERT architecture).

Similarity Metric: Cosine Distance via pgvector.

Backend: Django 6.0 + PostgreSQL.