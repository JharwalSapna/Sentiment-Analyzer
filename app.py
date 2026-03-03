from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer
import re
import os
import string

# Download required NLTK data
def download_nltk_data():
    packages = ['vader_lexicon', 'punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger', 'punkt_tab']
    for package in packages:
        try:
            nltk.download(package, quiet=True)
        except Exception as e:
            print(f"Warning: Could not download {package}: {e}")

download_nltk_data()

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Initialize NLP components
sia = SentimentIntensityAnalyzer()
lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()
try:
    stop_words = set(stopwords.words('english'))
except:
    stop_words = set()


class TextPreprocessor:
    """Text preprocessing class for NLP"""
    
    def __init__(self):
        self.lemmatizer = lemmatizer
        self.stemmer = stemmer
        self.stop_words = stop_words
    
    def clean_text(self, text):
        """Remove URLs and extra whitespace"""
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'<.*?>', '', text)
        text = ' '.join(text.split())
        return text
    
    def tokenize(self, text):
        """Tokenize text into words"""
        try:
            return word_tokenize(text.lower())
        except:
            return text.lower().split()
    
    def remove_stopwords(self, tokens):
        return [token for token in tokens if token not in self.stop_words]
    
    def remove_punctuation(self, tokens):
        return [token for token in tokens if token not in string.punctuation]
    
    def lemmatize(self, tokens):
        return [self.lemmatizer.lemmatize(token) for token in tokens]
    
    def stem(self, tokens):
        return [self.stemmer.stem(token) for token in tokens]
    
    def preprocess(self, text, use_lemmatization=True, use_stemming=False):
        """Full preprocessing pipeline"""
        cleaned = self.clean_text(text)
        tokens = self.tokenize(cleaned)
        tokens = self.remove_punctuation(tokens)
        tokens = self.remove_stopwords(tokens)
        
        tokens_before = tokens.copy()
        lemmatized_tokens = self.lemmatize(tokens_before)
        stemmed_tokens = self.stem(tokens_before)
        
        if use_stemming:
            final_tokens = stemmed_tokens
        else:
            final_tokens = lemmatized_tokens
        
        return {
            'original_text': text,
            'cleaned_text': cleaned,
            'tokens': final_tokens,
            'lemmatized_tokens': lemmatized_tokens,
            'stemmed_tokens': stemmed_tokens,
            'preprocessed_text': ' '.join(final_tokens)
        }


class SentimentAnalyzer:
    """Sentiment Analysis using NLTK VADER"""
    
    def __init__(self):
        self.analyzer = sia
        self.preprocessor = TextPreprocessor()
    
    def analyze_sentiment(self, text):
        if not text or not text.strip():
            return {
                'error': 'Empty text provided',
                'sentiment': 'neutral',
                'scores': {'neg': 0, 'neu': 1, 'pos': 0, 'compound': 0}
            }
        
        preprocessing_result = self.preprocessor.preprocess(text)
        scores = self.analyzer.polarity_scores(text)
        
        compound = scores['compound']
        if compound >= 0.05:
            sentiment = 'positive'
            confidence = min(abs(compound) * 100, 100)
        elif compound <= -0.05:
            sentiment = 'negative'
            confidence = min(abs(compound) * 100, 100)
        else:
            sentiment = 'neutral'
            confidence = (1 - abs(compound)) * 100
        
        sentences_analysis = []
        try:
            sentences = sent_tokenize(text)
            for sent in sentences[:10]:
                sent_scores = self.analyzer.polarity_scores(sent)
                sent_sentiment = 'positive' if sent_scores['compound'] >= 0.05 else \
                                'negative' if sent_scores['compound'] <= -0.05 else 'neutral'
                sentences_analysis.append({
                    'sentence': sent[:200],
                    'sentiment': sent_sentiment,
                    'compound': round(sent_scores['compound'], 4)
                })
        except:
            sentences_analysis = []
        
        return {
            'sentiment': sentiment,
            'confidence': round(confidence, 2),
            'scores': {
                'positive': round(scores['pos'] * 100, 2),
                'negative': round(scores['neg'] * 100, 2),
                'neutral': round(scores['neu'] * 100, 2),
                'compound': round(scores['compound'], 4)
            },
            'preprocessing': {
                'original_length': len(text),
                'token_count': len(preprocessing_result['tokens']),
                'cleaned_text': preprocessing_result['cleaned_text'][:500],
                'sample_tokens': preprocessing_result['tokens'][:20],
                'lemmatized_sample': preprocessing_result.get('lemmatized_tokens', [])[:10],
                'stemmed_sample': preprocessing_result.get('stemmed_tokens', [])[:10]
            },
            'sentence_analysis': sentences_analysis
        }


analyzer = SentimentAnalyzer()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    try:
        if request.is_json:
            data = request.get_json()
            text = data.get('text', '')
        else:
            text = request.form.get('text', '')
            if 'file' in request.files:
                file = request.files['file']
                if file.filename:
                    text = file.read().decode('utf-8', errors='ignore')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        result = analyzer.analyze_sentiment(text)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("=" * 50)
    print("  Sentiment Analysis Application")
    print("  Starting at http://localhost:5001")
    print("=" * 50)
    
    os.environ['FLASK_SKIP_DOTENV'] = '1'
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5001, app, use_reloader=False, use_debugger=True)
