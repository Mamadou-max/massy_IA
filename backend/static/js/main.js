let TOKEN = null;

// Tabs
document.querySelectorAll(".tab-btn").forEach(btn=>{
  btn.addEventListener("click",()=>{
    document.querySelectorAll(".tab-content").forEach(c=>c.classList.remove("show"));
    document.querySelectorAll(".tab-btn").forEach(b=>b.classList.remove("border-blue-500"));
    const tab = document.getElementById(btn.dataset.tab);
    tab.classList.add("show");
    btn.classList.add("border-blue-500");
    if(btn.dataset.tab==="map"){ setTimeout(initMap,300); }
  });
});

// Auth
async function register(){
  const firstName=document.getElementById("reg-first-name").value.trim();
  const lastName=document.getElementById("reg-last-name").value.trim();
  const email=document.getElementById("reg-email").value.trim();
  const pass=document.getElementById("reg-pass").value.trim();
  const msg=document.getElementById("auth-msg");
  if(!firstName||!lastName||!email||!pass){ msg.innerText="Tous les champs sont requis"; return;}
  try{
    const res=await fetch("/api/auth/register",{method:"POST", headers:{ "Content-Type":"application/json" }, body:JSON.stringify({first_name:firstName,last_name:lastName,email,password:pass})});
    const data=await res.json();
    if(res.ok){ msg.classList.remove("text-red-500"); msg.classList.add("text-green-500"); msg.innerText="Inscription réussie ! Connectez-vous."; }
    else{ msg.classList.remove("text-green-500"); msg.classList.add("text-red-500"); msg.innerText=data.message||"Erreur inscription";}
  }catch(err){ msg.classList.remove("text-green-500"); msg.classList.add("text-red-500"); msg.innerText="Erreur serveur";}
}

async function login(){
  const email=document.getElementById("log-email").value.trim();
  const pass=document.getElementById("log-pass").value.trim();
  const msg=document.getElementById("auth-msg");
  if(!email||!pass){ msg.innerText="Tous les champs sont requis"; return;}
  try{
    const res=await fetch("/api/auth/login",{method:"POST", headers:{ "Content-Type":"application/json" }, body:JSON.stringify({email,password:pass})});
    const data=await res.json();
    if(res.ok){ TOKEN=data.data.access_token; msg.classList.remove("text-red-500"); msg.classList.add("text-green-500"); msg.innerText="Connexion réussie !"; document.getElementById("auth").classList.remove("show"); document.getElementById("chatbot").classList.add("show"); }
    else{ msg.classList.remove("text-green-500"); msg.classList.add("text-red-500"); msg.innerText=data.message||"Erreur connexion";}
  }catch(err){ msg.classList.remove("text-green-500"); msg.classList.add("text-red-500"); msg.innerText="Erreur serveur";}
}

// OAuth social
function oauthLogin(provider){
  window.location.href=`/api/auth/oauth/${provider}`;
}

// Chatbot
const chatContainer = document.getElementById("chat-container");
function addMessage(role,content="",typing=false){
  const msgDiv=document.createElement("div");
  msgDiv.className="flex gap-2 "+(role==="user"?"justify-end":"justify-start");
  const avatar=document.createElement("div");
  avatar.className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-white "+(role==="user"?"bg-blue-500":"bg-gray-500");
  avatar.textContent=role==="user"?"U":"AI";
  const bubble=document.createElement("div");
  bubble.className="rounded-lg px-4 py-2 max-w-[70%] whitespace-pre-wrap message "+(role==="user"?"bg-blue-600":"bg-gray-700 text-white");
  if(typing) bubble.innerHTML=`<div class="typing"><span></span><span></span><span></span></div>`;
  else bubble.innerHTML=content;
  msgDiv.appendChild(role==="user"?bubble:avatar);
  msgDiv.appendChild(role==="user"?avatar:bubble);
  chatContainer.appendChild(msgDiv);
  chatContainer.scrollTo({top:chatContainer.scrollHeight,behavior:'smooth'});
  return bubble;
}

async function sendMessage(){
  const message=document.getElementById("message").value.trim();
  if(!message) return;
  addMessage("user",message);
  document.getElementById("message").value="";
  const typingBubble=addMessage("assistant","",true);
  if(!TOKEN){ typingBubble.innerHTML="Veuillez vous connecter"; return; }
  try{
    const res=await fetch("/api/chatbot/chat",{method:"POST", headers:{ "Content-Type":"application/json", "Authorization":"Bearer "+TOKEN }, body:JSON.stringify({message})});
    const data=await res.json();
    let responseText=data.data?.response||"Pas de réponse";
    typingBubble.innerHTML="";
    let i=0; function typeLetter(){ if(i<responseText.length){ typingBubble.innerHTML+=responseText[i]; i++; chatContainer.scrollTo({top:chatContainer.scrollHeight, behavior:'smooth'}); setTimeout(typeLetter,20); } }
    typeLetter();
  }catch(err){typingBubble.innerHTML="Erreur serveur";}
}

// Analyse marché
async function analyzeMarket(){
  const text=document.getElementById("market-text").value.trim();
  const file=document.getElementById("market-file").files[0];
  if(!text&&!file) return;
  const formData=new FormData();
  formData.append("text",text);
  if(file) formData.append("file",file);
  if(!TOKEN){ document.getElementById("market-result").textContent="Veuillez vous connecter"; return; }
  try{
    const res=await fetch("/api/market/analyze",{method:"POST", headers:{ "Authorization":"Bearer "+TOKEN }, body:formData});
    const data=await res.json();
    document.getElementById("market-result").textContent=JSON.stringify(data.data,null,2);
  }catch(err){document.getElementById("market-result").textContent="Erreur serveur";}
}

// Profil
async function getProfile(){
  if(!TOKEN){ document.getElementById("profile-result").textContent="Veuillez vous connecter"; return; }
  try{
    const res=await fetch("/api/auth/profile",{headers:{ "Authorization":"Bearer "+TOKEN }});
    const data=await res.json();
    document.getElementById("profile-result").textContent=JSON.stringify(data.data,null,2);
  }catch(err){document.getElementById("profile-result").textContent="Erreur serveur";}
}

// Carte Massy
let mapInit=false;
function initMap(){
  if(mapInit) return; mapInit=true;
  const map=L.map('mapid').setView([48.7281,2.2828],14); // Massy
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
    attribution:'© OpenStreetMap contributors'
  }).addTo(map);
  const routines=[ {lat:48.7281,lng:2.2828,info:"Routine 1"}, {lat:48.7300,lng:2.2850,info:"Routine 2"} ];
  routines.forEach(r=>{ L.marker([r.lat,r.lng]).addTo(map).bindPopup(r.info); });
}
