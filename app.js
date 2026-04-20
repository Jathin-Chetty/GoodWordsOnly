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

    const CLASS_COLORS = {
        Appropriate: '#2f855a',
        Inappropriate: '#b7791f',
        Offensive: '#b83280',
        Violent: '#c53030'
    };

    analyzeBtn.addEventListener('click', async () => {
        const text = textInput.value.trim();
        if (!text) return;

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
        }
    });

    function displayResult(data) {
        const topLabel = data.display_label || data.label;
        const probPercentage = (data.probability * 100).toFixed(1);
        const topColor = CLASS_COLORS[topLabel] || '#4a5568';

        predictionBadge.textContent = topLabel;
        predictionBadge.className = 'badge';
        predictionBadge.style.backgroundColor = topColor;

        predictionProb.textContent = `${probPercentage}%`;
        confidenceFill.style.backgroundColor = topColor;
        const fullModelName = data.model || '';
        const shortModelName = fullModelName.includes('/') ? fullModelName.split('/').pop() : fullModelName;
        modelName.textContent = shortModelName || '-';

        classScores.innerHTML = '';
        (data.classes || []).forEach((item) => {
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
            barFill.style.width = `${(item.score * 100).toFixed(1)}%`;
            barWrap.appendChild(barFill);

            const score = document.createElement('span');
            score.className = 'class-score';
            score.textContent = `${(item.score * 100).toFixed(1)}%`;

            row.appendChild(label);
            row.appendChild(barWrap);
            row.appendChild(score);
            classScores.appendChild(row);
        });

        resultContainer.classList.remove('hidden');
        setTimeout(() => {
            confidenceFill.style.width = `${probPercentage}%`;
        }, 50);
    }
});
