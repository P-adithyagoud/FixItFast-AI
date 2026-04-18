document.addEventListener('DOMContentLoaded', () => {
    const incidentInput = document.getElementById('incidentInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resetBtn = document.getElementById('resetBtn');
    const resultsSection = document.getElementById('results');
    const loadingSection = document.getElementById('loading');
    const errorSection = document.getElementById('error');
    const charCountEl = document.getElementById('charCount');

    // Character counter
    incidentInput.addEventListener('input', () => {
        const length = incidentInput.value.length;
        charCountEl.textContent = `${length} / 5000`;
        
        if (length > 5000) {
            incidentInput.value = incidentInput.value.substring(0, 5000);
            charCountEl.textContent = '5000 / 5000';
        }
    });

    // Analyze incident
    analyzeBtn.addEventListener('click', async () => {
        const incident = incidentInput.value.trim();

        if (!incident) {
            showError('Please enter an incident description');
            return;
        }

        await analyzeIncident(incident);
    });

    // Reset form
    resetBtn.addEventListener('click', () => {
        incidentInput.value = '';
        charCountEl.textContent = '0 / 5000';
        resultsSection.style.display = 'none';
        errorSection.style.display = 'none';
        incidentInput.focus();
    });

    // Allow Enter to submit (Ctrl+Enter)
    incidentInput.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            analyzeBtn.click();
        }
    });

    async function analyzeIncident(incident) {
        analyzeBtn.disabled = true;
        errorSection.style.display = 'none';
        resultsSection.style.display = 'none';
        loadingSection.style.display = 'block';

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ incident })
            });

            const data = await response.json();

            if (!response.ok) {
                showError(data.error || 'Failed to analyze incident');
                loadingSection.style.display = 'none';
                analyzeBtn.disabled = false;
                return;
            }

            loadingSection.style.display = 'none';
            displayResults(data.result);
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

        } catch (error) {
            showError(`Network error: ${error.message}`);
            loadingSection.style.display = 'none';
        } finally {
            analyzeBtn.disabled = false;
        }
    }

    function displayResults(result) {
        // Root Cause
        document.getElementById('rootCause').innerHTML = formatText(result.root_cause);

        // Immediate Fix
        document.getElementById('immediateFix').innerHTML = formatText(result.immediate_fix);

        // Prevention
        document.getElementById('prevention').innerHTML = formatText(result.prevention);

        // Similar Incident
        document.getElementById('similarIncident').innerHTML = formatText(result.similar_incident);

        // Similarity Score
        document.getElementById('similarityScore').innerHTML = formatText(result.similarity_score);

        // Confidence Level
        document.getElementById('confidenceLevel').innerHTML = formatText(result.confidence_level);
    }

    function formatText(text) {
        if (!text) return '<p style="color: var(--text-secondary); font-style: italic;">No information available</p>';

        // If 'text' is an array (common in JSON mode for list fields), join it
        if (Array.isArray(text)) {
            text = text.join('\n');
        }

        // Ensure we are working with a string
        text = String(text);

        // Convert numbered lists to <ol>
        text = text.replace(/^\s*(\d+)\.\s+/gm, '<li>');
        
        // Check if we need to wrap in <ol>
        if (text.includes('<li>')) {
            text = '<ol>' + text.replace(/<li>/g, '<li>') + '</ol>';
        }

        // Convert bullet points to <ul>
        text = text.replace(/^\s*[-•]\s+/gm, '<li style="margin-left: 20px;">');
        if (text.includes('<li style="margin-left: 20px;">')) {
            const parts = text.split('<li style="margin-left: 20px;">');
            if (parts.length > 1) {
                text = '<ul style="margin-left: 0;">' + 
                       '<li style="margin-left: 0;">' + parts.slice(1).join('</li><li style="margin-left: 0;">') + 
                       '</li></ul>';
            }
        }

        // Bold important keywords
        const keywords = ['critical', 'urgent', 'immediately', 'must', 'prevent', 'error', 'failed', 'timeout', 'memory', 'cpu'];
        keywords.forEach(keyword => {
            const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
            text = text.replace(regex, `<strong>$&</strong>`);
        });

        // Convert line breaks
        text = text.replace(/\n\n/g, '</p><p>');
        text = text.replace(/\n/g, '<br>');

        // Wrap in paragraphs if not already
        if (!text.includes('<p>')) {
            text = `<p>${text}</p>`;
        }

        return text;
    }

    function showError(message) {
        errorSection.textContent = message;
        errorSection.style.display = 'block';
        errorSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
});
