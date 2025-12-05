// =========================================
// Front do TR4CTION Agent (página principal)
// =========================================

// Ajuste aqui se o backend estiver em outro host/porta
const BACKEND_URL = 'http://3.235.65.249/api';

// 🚀 ROTA CORRETA DO BACKEND
const CHAT_ENDPOINT = `${BACKEND_URL}/agent/ask`;

const KNOWLEDGE_ENDPOINT = `${BACKEND_URL}/admin/knowledge`;
const TEMPLATE_SUGGEST_ENDPOINT = `${BACKEND_URL}/templates/suggest`;

document.addEventListener("DOMContentLoaded", () => {
  // Verifica autenticação
  if (!checkAuth()) {
    window.location.href = "login.html";
    return;
  }
  
  setupAdminButton();
  setupTabs();
  setupConfigPersistence();
  setupChat();
  refreshKnowledgeStats();
  displayUserInfo();
});

// Verificação de autenticação
function checkAuth() {
  const token = localStorage.getItem('tr4ction_token');
  const role = localStorage.getItem('tr4ction_role');
  return token && role === 'founder';
}

function getAuthHeaders() {
  const token = localStorage.getItem('tr4ction_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
}

function logout() {
  localStorage.removeItem('tr4ction_token');
  localStorage.removeItem('tr4ction_role');
  localStorage.removeItem('tr4ction_startup');
  localStorage.removeItem('tr4ction_founder');
  window.location.href = 'login.html';
}

function displayUserInfo() {
  const founderName = localStorage.getItem('tr4ction_founder');
  const startupName = localStorage.getItem('tr4ction_startup');
  
  // Preenche automaticamente os campos
  const startupInput = document.getElementById('startupInput');
  const founderInput = document.getElementById('founderInput');
  
  if (startupInput && startupName) startupInput.value = startupName;
  if (founderInput && founderName) founderInput.value = founderName;
}

// ----------------------------------------
// Navegação – botão para painel admin
// ----------------------------------------
function setupAdminButton() {
  const adminBtn = document.getElementById("btnAdmin");
  if (adminBtn) {
    adminBtn.style.display = 'none'; // Founders não veem botão admin
  }
  
  // Adiciona botão de logout
  const nav = document.querySelector('.fcj-header__nav');
  if (nav) {
    const logoutBtn = document.createElement('button');
    logoutBtn.className = 'btn-outline';
    logoutBtn.textContent = 'Sair';
    logoutBtn.addEventListener('click', logout);
    nav.appendChild(logoutBtn);
  }
}

// ----------------------------------------
// Tabs (Agente / Templates)
// ----------------------------------------
function setupTabs() {
  const tabButtons = document.querySelectorAll(".fcj-tab");
  const panels = document.querySelectorAll(".fcj-panel");

  if (!tabButtons.length || !panels.length) return;

  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-tab");
      if (!target) return;

      tabButtons.forEach((b) => b.classList.remove("fcj-tab--active"));
      panels.forEach((p) => p.classList.remove("fcj-panel--active"));

      btn.classList.add("fcj-tab--active");
      const panel = document.getElementById(target);
      if (panel) panel.classList.add("fcj-panel--active");
    });
  });
}

// ----------------------------------------
// Configuração salva em localStorage
// ----------------------------------------
const CONFIG_STORAGE_KEY = "tr4ction_agent_config";

function setupConfigPersistence() {
  const startupInput = document.getElementById("startupInput");
  const stepSelect = document.getElementById("stepSelect");

  if (!startupInput || !stepSelect) return;

  try {
    const raw = localStorage.getItem(CONFIG_STORAGE_KEY);
    if (raw) {
      const saved = JSON.parse(raw);
      if (saved.startup) startupInput.value = saved.startup;
      if (saved.step) stepSelect.value = saved.step;
    }
  } catch (err) {
    console.warn("Erro ao carregar config do localStorage:", err);
  }

  function saveConfig() {
    const config = {
      startup: startupInput.value.trim(),
      step: stepSelect.value,
    };
    try {
      localStorage.setItem(CONFIG_STORAGE_KEY, JSON.stringify(config));
    } catch (err) {
      console.warn("Erro ao salvar config:", err);
    }
  }

  startupInput.addEventListener("change", saveConfig);
  stepSelect.addEventListener("change", saveConfig);
}

function getCurrentConfig() {
  const startupInput = document.getElementById("startupInput");
  const stepSelect = document.getElementById("stepSelect");

  return {
    startup: startupInput ? startupInput.value.trim() : "",
    step: stepSelect ? stepSelect.value : "todas",
  };
}

// ----------------------------------------
// Chat com backend (AGENTE)
// ----------------------------------------
function setupChat() {
  const sendBtn = document.getElementById("sendBtn");
  const chatInput = document.getElementById("chatInput");
  const chatWindow = document.getElementById("chatWindow");

  if (!sendBtn || !chatInput || !chatWindow) return;

  addMessage(
    chatWindow,
    "Olá! Eu sou o TR4CTION Agent. Configure sua startup ao lado e faça perguntas sobre a trilha oficial FCJ.",
    "agent"
  );

  let isSending = false;
  let typingEl = null;
  let history = [];

  async function handleSend() {
    const text = chatInput.value.trim();
    if (!text || isSending) return;

    const config = getCurrentConfig();

    addMessage(chatWindow, text, "user");
    chatInput.value = "";

    history.push({ role: "user", content: text });

    typingEl = addTypingIndicator(chatWindow);
    isSending = true;
    sendBtn.disabled = true;

    try {
      const payload = {
        startup_id: config.startup || "Minha Startup",
        step: config.step || "todas",
        history: history,
        user_input: text,
      };

      const res = await fetch(CHAT_ENDPOINT, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      const answer = data.response || "O backend não retornou resposta.";

      removeTypingIndicator(chatWindow, typingEl);
      typingEl = null;

      addMessage(chatWindow, answer, "agent");
      history.push({ role: "assistant", content: answer });

    } catch (err) {
      console.error("Erro ao chamar backend /agent/ask:", err);
      removeTypingIndicator(chatWindow, typingEl);
      typingEl = null;

      addMessage(
        chatWindow,
        "Não consegui falar com o backend. Verifique se o servidor está rodando em http://127.0.0.1:8000",
        "system"
      );
    } finally {
      isSending = false;
      sendBtn.disabled = false;
    }
  }

  sendBtn.addEventListener("click", handleSend);

  chatInput.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter" && !ev.shiftKey) {
      ev.preventDefault();
      handleSend();
    }
  });

  setupTemplateSuggestions();
}

// Mensagens -------------------------------------------------

function addMessage(container, text, sender = "user") {
  const wrapper = document.createElement("div");
  wrapper.classList.add("chat-msg");

  if (sender === "agent") wrapper.classList.add("msg-agent");
  else if (sender === "system") wrapper.classList.add("msg-system");
  else wrapper.classList.add("msg-user");

  const bubble = document.createElement("div");
  bubble.classList.add("chat-bubble");
  bubble.textContent = text;

  wrapper.appendChild(bubble);
  container.appendChild(wrapper);
  container.scrollTop = container.scrollHeight;
}

function addTypingIndicator(container) {
  const wrapper = document.createElement("div");
  wrapper.classList.add("chat-msg", "msg-agent");

  const bubble = document.createElement("div");
  bubble.classList.add("chat-bubble", "typing");
  bubble.innerHTML = "<span></span><span></span><span></span>";

  wrapper.appendChild(bubble);
  container.appendChild(wrapper);
  container.scrollTop = container.scrollHeight;
  return wrapper;
}

function removeTypingIndicator(container, el) {
  if (el && container.contains(el)) {
    container.removeChild(el);
    container.scrollTop = container.scrollHeight;
  }
}

// ----------------------------------------
// Base de Conhecimento
// ----------------------------------------
async function refreshKnowledgeStats() {
  const docsEl = document.getElementById("statsDocs");
  const stepsEl = document.getElementById("statsLoaded");

  if (!docsEl || !stepsEl) return;

  try {
    const res = await fetch(KNOWLEDGE_ENDPOINT, {
      headers: getAuthHeaders()
    });
    if (res.status === 401 || res.status === 403) {
      // Founders não têm acesso a stats admin, ignora erro
      docsEl.textContent = "Documentos: –";
      stepsEl.textContent = "Etapas: –";
      return;
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    docsEl.textContent = `Documentos: ${data.docs ?? "–"}`;
    const steps =
      data.steps && data.steps.length
        ? data.steps.join(", ")
        : "nenhuma etapa cadastrada";
    stepsEl.textContent = `Etapas: ${steps}`;
  } catch (err) {
    console.error("Erro ao buscar /admin/knowledge:", err);
    docsEl.textContent = "Documentos: erro";
    stepsEl.textContent = "Etapas: erro";
  }
}

// ----------------------------------------
// Sugestões de Template
// ----------------------------------------
function setupTemplateSuggestions() {
  const suggestBtns = document.querySelectorAll(".fcj-template-suggest-btn");
  if (!suggestBtns.length) return;

  suggestBtns.forEach((btn) => {
    btn.addEventListener("click", async () => {
      const targetId = btn.getAttribute("data-target");
      const fieldName = document
        .getElementById(targetId)
        ?.getAttribute("data-field-name");

      const textarea = document.getElementById(targetId);
      if (!textarea) return;

      textarea.value = "Gerando sugestão...";
      btn.disabled = true;

      try {
        const res = await fetch(TEMPLATE_SUGGEST_ENDPOINT, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            field: fieldName || targetId,
            step: document.getElementById("templateStepSelect")?.value,
            config: getCurrentConfig(),
          }),
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data = await res.json();
        textarea.value =
          data.suggestion ||
          data.text ||
          "Backend não retornou sugestão.";

      } catch (err) {
        console.error("Erro na sugestão:", err);
        textarea.value =
          "Não consegui gerar sugestão. Verifique o backend.";
      } finally {
        btn.disabled = false;
      }
    });
  });
}
