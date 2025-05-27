from flask import Flask, request, jsonify, render_template_string
import requests
import uuid
from queue import Queue
from threading import Thread

app = Flask(__name__)

# 🔁 Fila de mensagens
message_queue = Queue()

# 🔗 Função para se comunicar com o Ollama
def chat_with_ollama(message, session_id=None):
    url = "http://127.0.0.1:11434/api/generate"
    payload = {
        "model": "phi",  # ou 'phi' ou outro modelo que você tenha
        "prompt": message,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "⚠️ Sem resposta da IA.")
    except requests.exceptions.ConnectionError:
        return "🚫 Não foi possível conectar ao Ollama. Verifique se ele está rodando."
    except requests.exceptions.Timeout:
        return "⏳ A requisição demorou muito para responder."
    except requests.exceptions.HTTPError as err:
        return f"❌ Erro HTTP: {err.response.status_code} - {err.response.text}"
    except Exception as e:
        return f"⚠️ Erro inesperado: {e}"

# 🧠 Dicionário para armazenar respostas por sessão
response_store = {}

# 🚀 Worker que processa a fila
def process_queue():
    while True:
        session_id, message = message_queue.get()
        print(f"➡️ Processando mensagem: {message}")
        response = chat_with_ollama(message, session_id)
        response_store[session_id] = response
        message_queue.task_done()

# 🏃 Inicia o worker em background
worker = Thread(target=process_queue, daemon=True)
worker.start()

# 🎨 Interface HTML do chat
CHAT_TEMPLATE = '''
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>AtendAI Local</title>
  <style>
    body { background-color: #1e1e1e; color: white; font-family: Arial; margin: 2rem; }
    #chat { border:1px solid #444; padding:1rem; height:400px; overflow-y:scroll; background:#2d2d2d; }
    .user{color: #4EA1D3;} .bot{color:#84C318;}
    input { width: 80%; padding: 0.5rem; }
    button { padding: 0.5rem; }
  </style>
</head>
<body>
  <h1>🧠 AtendAI</h1>
  <div id="chat"></div>
  <input type="text" id="input" placeholder="Sua mensagem..."/>
  <button onclick="sendMessage()">Enviar</button>

  <script>
    const chatDiv = document.getElementById('chat');
    const input = document.getElementById('input');

    function appendMessage(sender, text) {
      const p = document.createElement('p');
      p.className = sender;
      p.textContent = text;
      chatDiv.appendChild(p);
      chatDiv.scrollTop = chatDiv.scrollHeight;
    }

    async function sendMessage() {
      const message = input.value.trim();
      if (!message) return;
      appendMessage('user', message);
      input.value = '';

      const response = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message})
      });

      const data = await response.json();

      if (data.answer === 'PENDENTE') {
        appendMessage('bot', '⏳ Mensagem recebida! Processando...');
        // Checa a resposta a cada 2 segundos
        checkResponse(data.session_id);
      } else {
        appendMessage('bot', data.answer);
      }
    }

    async function checkResponse(sessionId) {
      const response = await fetch(`/response/${sessionId}`);
      const data = await response.json();

      if (data.answer === 'PENDENTE') {
        setTimeout(() => checkResponse(sessionId), 2000);
      } else {
        appendMessage('bot', data.answer);
      }
    }

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') sendMessage();
    });
  </script>
</body>
</html>
'''

# 🚪 Página principal
@app.route('/')
def home():
    return render_template_string(CHAT_TEMPLATE)

# 📨 Endpoint para envio de mensagem
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    session_id = str(uuid.uuid4())

    # Coloca a mensagem na fila
    message_queue.put((session_id, message))

    # Responde imediatamente que a mensagem está na fila
    return jsonify({'answer': 'PENDENTE', 'session_id': session_id})

# 🔍 Endpoint para consultar resposta
@app.route('/response/<session_id>', methods=['GET'])
def get_response(session_id):
    answer = response_store.get(session_id, 'PENDENTE')
    return jsonify({'answer': answer})

# 🚀 Iniciar servidor
if __name__ == '__main__':
    app.run(port=5000, debug=True)
