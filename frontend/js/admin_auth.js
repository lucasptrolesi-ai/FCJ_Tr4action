// =========================================
// Painel Admin – TR4CTION Agent (COM AUTENTICAÇÃO)
// =========================================

const BACKEND_URL = 'http://3.235.65.249/api';
const IS_PRODUCTION = !window.location.hostname.includes('localhost') && !window.location.hostname.includes('127.0.0.1');

document.addEventListener("DOMContentLoaded", () => {
  // Verifica autenticação admin
  if (!checkAdminAuth()) {
    window.location.href = "login-admin.html";
    return;
  }

  setupAdmin();
});

function checkAdminAuth() {
  const token = localStorage.getItem('tr4ction_token');
  const role = localStorage.getItem('tr4ction_role');
  return token && role === 'admin';
}

function getAuthHeaders() {
  const token = localStorage.getItem('tr4ction_token');
  return {
    'Authorization': `Bearer ${token}`
  };
}

function logout() {
  localStorage.clear();
  window.location.href = 'login-admin.html';
}

function setupAdmin() {
  const fileInput = document.getElementById("pptxFile");
  const uploadBtn = document.getElementById("uploadBtn");
  const uploadStatus = document.getElementById("uploadStatus");

  const reloadBtn = document.getElementById("reloadKnowledgeBtn");
  const reloadStatus = document.getElementById("reloadStatus");

  const stepSelect = document.getElementById("stepUpload") || null;

  // Bot\u00e3o voltar substitui por logout
  const voltarBtn = document.getElementById("btnVoltarAgente");
  if (voltarBtn) {
    voltarBtn.textContent = 'Sair';
    voltarBtn.addEventListener("click", logout);
  }

  async function refreshStats() {
    try {
      const res = await fetch(`${BACKEND_URL}/admin/knowledge`, {
        headers: getAuthHeaders()
      });
      
      if (res.status === 401 || res.status === 403) {
        logout();
        return;
      }
      
      if (!res.ok) return;
      
      const data = await res.json();
      const msg = `Base: ${data.docs} documento(s) | Etapas: ${
        data.steps && data.steps.length ? data.steps.join(", ") : "nenhuma"
      }`;

      if (reloadStatus) reloadStatus.textContent = msg;
      if (uploadStatus && uploadStatus.textContent === "Aguardando upload...") {
        uploadStatus.textContent = msg;
      }
    } catch (err) {
      if (!IS_PRODUCTION) console.error("Erro ao consultar /admin/knowledge:", err);
    }
  }

  async function handleUpload() {
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
      uploadStatus.textContent = "Selecione ao menos um arquivo PPTX.";
      return;
    }

    const files = Array.from(fileInput.files);
    const step = stepSelect ? stepSelect.value : "diagnostico";

    const invalid = files.some(f => !f.name.toLowerCase().endsWith(".pptx"));
    if (invalid) {
      uploadStatus.textContent = "Todos os arquivos devem ser PPTX.";
      return;
    }

    uploadStatus.textContent = `Enviando ${files.length} arquivo(s)...`;

    const formData = new FormData();
    formData.append("step", step);

    files.forEach(file => {
      formData.append("files", file);
    });

    try {
      const res = await fetch(`${BACKEND_URL}/admin/upload-pptx`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: formData,
      });

      if (res.status === 401 || res.status === 403) {
        logout();
        return;
      }

      if (!res.ok) {
        const errText = await res.text();
        if (!IS_PRODUCTION) console.error("Erro upload:", res.status, errText);
        uploadStatus.textContent = "Erro ao enviar os arquivos.";
        return;
      }

      const data = await res.json();
      uploadStatus.textContent =
        `Upload concluído. ${data.added} arquivo(s) processado(s). ` +
        `Total na base: ${data.docs_total}.`;

      await refreshStats();

    } catch (err) {
      if (!IS_PRODUCTION) console.error(err);
      uploadStatus.textContent =
        "Erro de rede ao enviar arquivos. Verifique se o backend está rodando.";
    }
  }

  async function handleReload() {
    if (reloadStatus) reloadStatus.textContent = "Recarregando...";

    try {
      const res = await fetch(`${BACKEND_URL}/admin/reload`, {
        method: "POST",
        headers: getAuthHeaders(),
      });

      if (res.status === 401 || res.status === 403) {
        logout();
        return;
      }

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      if (reloadStatus) {
        reloadStatus.textContent =
          `Base recarregada! ${data.stats?.docs || "?"} documento(s).`;
      }

      await refreshStats();

    } catch (err) {
      if (!IS_PRODUCTION) console.error(err);
      if (reloadStatus) reloadStatus.textContent = "Erro ao recarregar.";
    }
  }

  if (uploadBtn) uploadBtn.addEventListener("click", handleUpload);
  if (reloadBtn) reloadBtn.addEventListener("click", handleReload);

  refreshStats();
}
