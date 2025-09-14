const chatArea = document.getElementById('chat-area');
const chatInput = document.getElementById('chat-input');
const btnSend = document.getElementById('btn-send');

btnSend.addEventListener('click', sendMessage);
chatInput.addEventListener('keydown', e=>{ if(e.key==='Enter') sendMessage(); });

async function sendMessage(){
  const msg = chatInput.value.trim();
  if(!msg) return;
  appendMessage('user', msg);
  chatInput.value='';
  const res = await fetch('/api/chatbot/query',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query:msg})});
  const data = await res.json();
  appendMessage('bot', data.answer);
}

function appendMessage(role,text){
  const div = document.createElement('div');
  div.className=`p-2 rounded-md ${role==='user'?'bg-blue-700 self-end':'bg-slate-700/50 self-start'}`;
  div.textContent=text;
  chatArea.appendChild(div);
  chatArea.scrollTop = chatArea.scrollHeight;
}
