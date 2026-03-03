document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('textInput');
    const charCount = document.getElementById('charCount');
    const fileInput = document.getElementById('fileInput');
    const dropZone = document.getElementById('dropZone');
    const fileName = document.getElementById('fileName');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultsSection = document.getElementById('resultsSection');

    let uploadedFileContent = null;
    const sentimentEmojis = { positive: '😊', neutral: '😐', negative: '😔' };

    textInput.addEventListener('input', () => charCount.textContent = textInput.value.length);

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.style.borderColor = '#4ECDC4'; });
    dropZone.addEventListener('dragleave', () => dropZone.style.borderColor = '');
    dropZone.addEventListener('drop', e => {
        e.preventDefault();
        dropZone.style.borderColor = '';
        if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', e => { if (e.target.files[0]) handleFile(e.target.files[0]); });

    function handleFile(file) {
        const reader = new FileReader();
        reader.onload = e => {
            uploadedFileContent = e.target.result;
            fileName.textContent = '📄 ' + file.name;
            fileName.classList.remove('hidden');
            textInput.value = uploadedFileContent.substring(0, 5000);
            charCount.textContent = textInput.value.length;
        };
        reader.readAsText(file);
    }

    analyzeBtn.addEventListener('click', async () => {
        const text = uploadedFileContent || textInput.value.trim();
        if (!text) { alert('Please enter text to analyze'); return; }

        analyzeBtn.querySelector('.btn-text').textContent = 'Analyzing...';
        analyzeBtn.disabled = true;

        try {
            const res = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            const result = await res.json();
            displayResults(result);
        } catch (err) {
            alert('Error analyzing text');
        } finally {
            analyzeBtn.querySelector('.btn-text').textContent = '🔍 Analyze Sentiment';
            analyzeBtn.disabled = false;
        }
    });

    function displayResults(result) {
        resultsSection.classList.add('visible');
        setTimeout(() => resultsSection.scrollIntoView({ behavior: 'smooth' }), 100);

        const sentiment = result.sentiment;
        document.getElementById('sentimentEmoji').textContent = sentimentEmojis[sentiment] || '🤔';
        const label = document.getElementById('sentimentLabel');
        label.textContent = sentiment;
        label.className = 'sentiment-label ' + sentiment;
        document.getElementById('confidenceValue').textContent = result.confidence;

        const scores = result.scores;
        setTimeout(() => {
            document.querySelector('#positiveBar .score-fill').style.width = scores.positive + '%';
            document.getElementById('positiveValue').textContent = scores.positive + '%';
        }, 100);
        setTimeout(() => {
            document.querySelector('#neutralBar .score-fill').style.width = scores.neutral + '%';
            document.getElementById('neutralValue').textContent = scores.neutral + '%';
        }, 200);
        setTimeout(() => {
            document.querySelector('#negativeBar .score-fill').style.width = scores.negative + '%';
            document.getElementById('negativeValue').textContent = scores.negative + '%';
        }, 300);

        setTimeout(() => {
            const gaugePos = ((scores.compound + 1) / 2) * 100;
            document.getElementById('gaugePointer').style.left = gaugePos + '%';
            const compoundEl = document.getElementById('compoundValue');
            compoundEl.textContent = scores.compound.toFixed(4);
            compoundEl.style.color = scores.compound >= 0.05 ? 'var(--positive)' : scores.compound <= -0.05 ? 'var(--negative)' : 'var(--neutral)';
        }, 400);

        if (result.preprocessing) {
            document.getElementById('originalLength').textContent = result.preprocessing.original_length;
            document.getElementById('tokenCount').textContent = result.preprocessing.token_count;
            
            const lemList = document.getElementById('lemmatizedList');
            lemList.innerHTML = '';
            (result.preprocessing.lemmatized_sample || []).forEach(t => {
                const el = document.createElement('span');
                el.className = 'token';
                el.textContent = t;
                lemList.appendChild(el);
            });

            const stemList = document.getElementById('stemmedList');
            stemList.innerHTML = '';
            (result.preprocessing.stemmed_sample || []).forEach(t => {
                const el = document.createElement('span');
                el.className = 'token';
                el.textContent = t;
                stemList.appendChild(el);
            });
        }

        if (result.sentence_analysis && result.sentence_analysis.length > 0) {
            document.getElementById('sentenceAnalysis').classList.remove('hidden');
            const list = document.getElementById('sentencesList');
            list.innerHTML = '';
            result.sentence_analysis.forEach(s => {
                const div = document.createElement('div');
                div.className = 'sentence-item ' + s.sentiment;
                div.innerHTML = `
                    <span class="sentence-indicator">${sentimentEmojis[s.sentiment]}</span>
                    <div>
                        <p class="sentence-text">${s.sentence}</p>
                        <span class="sentence-score">Score: ${s.compound}</span>
                    </div>
                `;
                list.appendChild(div);
            });
        }
    }

    resultsSection.classList.remove('visible');
});
