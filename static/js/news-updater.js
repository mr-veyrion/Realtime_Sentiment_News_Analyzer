let lastVersions = {};

function createNewsElement(item) {
    const div = document.createElement('div');
    div.className = 'news-item';
    div.innerHTML = `
        <h3>${item.headline}</h3>
        <p>${item.source} • ${item.timestamp}</p>
        ${item.subheading ? `<p>${item.subheading}</p>` : ''}
        <a href="${item.link}" target="_blank">Read more →</a>
    `;
    return div;
}

async function updateNews() {
    try {
        const res = await fetch('/news-data');
        const {news, error} = await res.json();
        
        if(error) throw new Error(error);
        
        news.forEach(cityData => {
            const container = document.getElementById(`${cityData.name}-news`);
            if(!container) return;

            // News items
            const itemsContainer = container.querySelector('.news-items');
            const currentItems = Array.from(itemsContainer.children);
            
            // Clear only if server has newer data
            if(Number(itemsContainer.dataset.version || 0) < cityData.updated) {
                itemsContainer.innerHTML = '';
                cityData.items.forEach(item => {
                    itemsContainer.appendChild(createNewsElement(item));
                });
                itemsContainer.dataset.version = cityData.updated;
            }

            // Analysis
            const analysisContainer = container.querySelector('.analysis-result');
            if(analysisContainer.dataset.version !== cityData.updated.toString()) {
                analysisContainer.innerHTML = cityData.analysis || 'Analysis pending...';
                analysisContainer.dataset.version = cityData.updated;
                // Add sentiment color
                const sentimentColor = getSentimentColor(cityData.analysis);
                container.querySelector('.sentiment-indicator').style.backgroundColor = sentimentColor;
            }
        });
        
    } catch(e) {
        console.error('Update error:', e);
    }
    setTimeout(updateNews, 1000); // Continue polling
}

// Initial call
updateNews();

// Remove old polling code and keep only the sentiment color function
function getSentimentColor(analysis) {
    const positiveWords = ['positive', 'optimistic', 'bullish', 'favorable'];
    const negativeWords = ['negative', 'pessimistic', 'bearish', 'unfavorable'];
    
    const score = positiveWords.filter(w => analysis.toLowerCase().includes(w)).length -
                  negativeWords.filter(w => analysis.toLowerCase().includes(w)).length;

    if (score > 0) return '#4CAF50';  // Green
    if (score < 0) return '#F44336';  // Red
    return '#FFC107';  // Amber
} 