const marketInput = document.getElementById('market-text');
const marketBtn = document.getElementById('btn-analyze');
const marketResult = document.getElementById('market-result');

marketBtn.addEventListener('click', analyzeMarket);

async function analyzeMarket() {
    const text = marketInput.value.trim();
    if(!text) return;
    marketResult.textContent = "Analyse en cours...";
    try {
        const res = await fetch('/api/market/analyze', {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({text})
        });
        const data = await res.json();
        marketResult.innerHTML = data.analysis
            .map(item => `<div class="p-2 border-b border-gray-700">${item}</div>`).join('');
    } catch(err) {
        marketResult.textContent = "Erreur lors de l'analyse.";
        console.error(err);
    }
}
