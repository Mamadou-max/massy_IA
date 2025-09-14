const btnGenImg = document.getElementById('btn-gen-img');
const videoInput = document.getElementById('video-file');
const mediaResult = document.getElementById('media-result');

btnGenImg.addEventListener('click', generateImage);
videoInput.addEventListener('change', analyzeVideo);

async function generateImage(){
    mediaResult.textContent = "Génération en cours...";
    try {
        const res = await fetch('/api/media/generate-image', { method:'POST' });
        const data = await res.json();
        mediaResult.innerHTML = `<img src="${data.url}" class="w-full rounded-md"/>`;
    } catch(err){
        mediaResult.textContent = "Erreur lors de la génération.";
        console.error(err);
    }
}

async function analyzeVideo(){
    const file = videoInput.files[0];
    if(!file) return;
    mediaResult.textContent = "Analyse vidéo...";
    const formData = new FormData();
    formData.append('video', file);
    try {
        const res = await fetch('/api/media/analyze-video',{ method:'POST', body: formData });
        const data = await res.json();
        mediaResult.innerHTML = `<div class="p-2">${data.result}</div>`;
    } catch(err){
        mediaResult.textContent = "Erreur lors de l'analyse.";
        console.error(err);
    }
}
