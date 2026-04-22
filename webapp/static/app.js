document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('text-input');
    const analyzeBtn = document.getElementById('analyze-btn');
    const loader = document.getElementById('loader');
    const resultContainer = document.getElementById('result-container');
    const predictionBadge = document.getElementById('prediction-badge');
    const predictionProb = document.getElementById('prediction-prob');
    const confidenceFill = document.getElementById('confidence-fill');
    const classScores = document.getElementById('class-scores');
    const modelName = document.getElementById('model-name');
    const historyList = document.getElementById('history-list');
    const refreshHistoryBtn = document.getElementById('refresh-history-btn');
    const historyToggleBtn = document.getElementById('history-toggle-btn');
    const historyPanel = document.getElementById('history-panel');
    const closeHistoryBtn = document.getElementById('close-history-btn');
    const historyBackdrop = document.getElementById('history-backdrop');

    const CLASS_COLORS = {
        Appropriate: '#2f855a',
        Inappropriate: '#b7791f',
        Offensive: '#b83280',
        Violent: '#c53030'
    };

    function safeNumber(value, fallback = 0) {
        const n = Number(value);
        return Number.isFinite(n) ? n : fallback;
    }

    function setHistoryPanel(open) {
        if (!historyPanel || !historyToggleBtn || !historyBackdrop) return;
        historyPanel.classList.toggle('open', open);
        historyPanel.setAttribute('aria-hidden', String(!open));
        historyToggleBtn.setAttribute('aria-expanded', String(open));
        historyBackdrop.classList.toggle('hidden', !open);
    }

    analyzeBtn.addEventListener('click', async () => {
        const text = textInput.value.trim();
        if (!text) return;

        // Reset UI
        analyzeBtn.disabled = true;
        loader.classList.remove('hidden');
        resultContainer.classList.add('hidden');
        confidenceFill.style.width = '0%';
        classScores.innerHTML = '';

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text })
            });

            const data = await response.json();

            if (response.ok) {
                displayResult(data);
            } else {
                alert(`Error: ${data.error || 'Something went wrong.'}`);
            }
        } catch (error) {
            console.error('Error calling prediction API:', error);
            alert('Failed to communicate with the server.');
        } finally {
            analyzeBtn.disabled = false;
            loader.classList.add('hidden');
            loadHistory();
        }
    });

    function displayResult(data) {
        // Expected data:
        // {
        //   model: "owner/model",
        //   label: "LABEL_0",
        //   display_label: "Appropriate",
        //   probability: 0.95,
        //   classes: [{ label, display_label, score }]
        // }
        const topLabel = data.display_label || data.label || 'Unknown';
        const topProbability = safeNumber(data.probability, 0);
        const probPercentage = (topProbability * 100).toFixed(1);
        const topColor = CLASS_COLORS[topLabel] || '#4a5568';

        // Update badge
        predictionBadge.textContent = topLabel;
        predictionBadge.className = 'badge'; // reset
        predictionBadge.style.backgroundColor = topColor;

        // Update probability text
        predictionProb.textContent = `${probPercentage}%`;

        // Update progress bar
        confidenceFill.style.backgroundColor = topColor;
        const fullModelName = data.model || '';
        const shortModelName = fullModelName.includes('/') ? fullModelName.split('/').pop() : fullModelName;
        modelName.textContent = shortModelName || '-';

        // Render all class scores
        classScores.innerHTML = '';
        (Array.isArray(data.classes) ? data.classes : []).forEach((item) => {
            const row = document.createElement('div');
            row.className = 'class-row';

            const label = document.createElement('span');
            label.className = 'class-label';
            label.textContent = item.display_label || item.label;

            const barWrap = document.createElement('div');
            barWrap.className = 'class-bar';
            const barFill = document.createElement('div');
            barFill.className = 'class-bar-fill';
            barFill.style.backgroundColor = CLASS_COLORS[label.textContent] || '#4a5568';
            barFill.style.width = `${(safeNumber(item.score, 0) * 100).toFixed(1)}%`;
            barWrap.appendChild(barFill);

            const score = document.createElement('span');
            score.className = 'class-score';
            score.textContent = `${(safeNumber(item.score, 0) * 100).toFixed(1)}%`;

            row.appendChild(label);
            row.appendChild(barWrap);
            row.appendChild(score);
            classScores.appendChild(row);
        });

        // Reveal container and animate bar
        resultContainer.classList.remove('hidden');

        // Small delay to ensure CSS transition fires since element just became visible
        setTimeout(() => {
            confidenceFill.style.width = `${probPercentage}%`;
        }, 50);
    }

    async function loadHistory() {
        if (!historyList) return;
        try {
            const res = await fetch('/api/history');
            const data = await res.json();
            
            historyList.innerHTML = '';
            if (!Array.isArray(data) || data.length === 0) {
                historyList.innerHTML = '<p style="color:#718096;text-align:center;font-size:0.9rem;">No search history yet.</p>';
                return;
            }

            data.forEach(item => {
                const div = document.createElement('div');
                div.className = 'history-item';
                const result = item.result || {};
                const resultLabel = result.display_label || result.label || 'Unknown';
                const resultProb = safeNumber(result.probability, 0);
                div.style.borderLeft = `4px solid ${CLASS_COLORS[resultLabel] || '#cbd5e0'}`;

                const textSpan = document.createElement('div');
                textSpan.style.fontWeight = '600';
                textSpan.style.fontSize = '0.95rem';
                textSpan.textContent = item.text.length > 50 ? item.text.substring(0, 50) + '...' : item.text;
                
                const resSpan = document.createElement('div');
                resSpan.style.fontSize = '0.85rem';
                resSpan.style.color = '#4a5568';
                resSpan.style.marginTop = '4px';
                resSpan.textContent = `${resultLabel} (${(resultProb * 100).toFixed(1)}%)`;
                
                div.appendChild(textSpan);
                div.appendChild(resSpan);
                historyList.appendChild(div);
            });
        } catch (e) {
            console.error('Failed to load history', e);
        }
    }

    if (refreshHistoryBtn) {
        refreshHistoryBtn.addEventListener('click', loadHistory);
    }

    if (historyToggleBtn) {
        historyToggleBtn.addEventListener('click', async () => {
            const willOpen = !historyPanel.classList.contains('open');
            setHistoryPanel(willOpen);
            if (willOpen) {
                await loadHistory();
            }
        });
    }

    if (closeHistoryBtn) {
        closeHistoryBtn.addEventListener('click', () => setHistoryPanel(false));
    }

    if (historyBackdrop) {
        historyBackdrop.addEventListener('click', () => setHistoryPanel(false));
    }

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            setHistoryPanel(false);
        }
    });

    // Load initially
    loadHistory();
});
