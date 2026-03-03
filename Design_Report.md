# Design Report
## Sentiment Analysis Application

---

## 1. Design Choices

### 1.1 Technology Selection

**Backend Framework: Flask**
- Chose Flask over Django because the application is simple and doesn't need Django's heavy features
- Flask is lightweight and easy to set up for API development
- Good documentation and community support

**NLP Library: NLTK with VADER**
- Selected VADER (Valence Aware Dictionary and sEntiment Reasoner) because:
  - Works well out-of-the-box without training data
  - Handles social media text, slang, and emoticons well
  - Provides compound score along with individual sentiment scores
  - Fast inference time suitable for real-time web applications
- Considered alternatives:
  - TextBlob: Simpler but less accurate
  - Transformers (BERT): More accurate but requires GPU and more setup
  - spaCy: Good for NER but sentiment analysis needs extra plugins

**Frontend: Vanilla HTML/CSS/JavaScript**
- No framework dependencies (React, Vue, etc.) to keep it simple
- Easy to understand and modify
- Works in any modern browser without build tools

### 1.2 Architecture Decisions

**Text Preprocessing Pipeline:**
```
Input Text → Clean (URLs, HTML) → Tokenize → Remove Stopwords → Lemmatize → Analyze
```

Why this order:
1. Cleaning first removes noise that could affect tokenization
2. Tokenization breaks text into analyzable units
3. Stopword removal reduces irrelevant words
4. Lemmatization normalizes words (running → run) for better matching

**API Design:**
- Single endpoint `/api/analyze` for simplicity
- JSON request/response format for easy integration
- Returns both sentiment label and numeric scores for flexibility

### 1.3 UI Design Choices

- Dark theme: Reduces eye strain, looks modern
- Progress bars for scores: Easy to understand at a glance
- Color coding: Green (positive), Yellow (neutral), Red (negative) - intuitive
- File upload support: Handles bulk text analysis use cases

---

## 2. Challenges Faced

### 2.1 NLTK Data Download
**Problem:** NLTK requires downloading lexicon data before first use, which can fail silently.

**Solution:** Added automatic download in `app.py` with error handling:
```python
def download_nltk_data():
    packages = ['vader_lexicon', 'punkt', 'stopwords', 'wordnet']
    for package in packages:
        try:
            nltk.download(package, quiet=True)
        except Exception as e:
            print(f"Warning: Could not download {package}")
```

### 2.2 Port Conflict on macOS
**Problem:** Port 5000 is used by AirPlay Receiver on macOS Monterey and later.

**Solution:** Changed default port to 5001.

### 2.3 Handling Edge Cases
**Problem:** Empty text, very long text, special characters could break analysis.

**Solutions implemented:**
- Empty text check returns neutral sentiment
- Text length limits on preprocessing display
- URL and HTML tag removal in preprocessing

### 2.4 Flask dotenv Permission Issue
**Problem:** Flask's auto-loading of .env files caused permission errors in some environments.

**Solution:** Disabled dotenv loading and used werkzeug's run_simple directly.

### 2.5 Balancing Accuracy vs Speed
**Problem:** More sophisticated models (BERT) are accurate but slow; simple models are fast but less accurate.

**Decision:** Chose VADER because:
- Response time < 100ms (acceptable for web app)
- Accuracy is good enough for general sentiment (not domain-specific)
- No GPU required for deployment

---

## 3. Limitations

1. **English Only:** VADER is trained on English text only
2. **Context Limitations:** Can miss sarcasm and complex context
3. **Domain Specific:** May not perform well on specialized domains (medical, legal) without fine-tuning
4. **No Aspect-Based Analysis:** Analyzes overall sentiment, not sentiment toward specific aspects

---

## 4. Future Improvements

1. Add support for multiple languages
2. Implement aspect-based sentiment analysis
3. Add option to use transformer models for higher accuracy
4. Store analysis history for tracking sentiment over time

---
