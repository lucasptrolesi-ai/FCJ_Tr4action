// =========================================
// Painel Admin – TR4CTION Agent
// Upload de PPTX + Recarregar base RAG
// =========================================

const BACKEND_URL = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("pptxFile");
  const uploadBtn = document.getElementById("uploadBtn");
  const uploadStatus = document.getElementById("uploadStatus");

  const reloadBtn = document.getElementById("reloadKnowledgeBtn");
  const reloadStatus = document.getElementById("reloadStatus");

  const stepSelect = document.getElementById("stepUpload") || null;

  const voltarBtn = document.getElementById("btnVoltarAgente");
  if (voltarBtn) {
    voltarBtn.addEventListener("click", () => {
      window.location.href = "index.html";
    });
  }

  async function refreshStats() {
    try {
      const res = await fetch(`${BACKEND_URL}/admin/knowledge`);
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
      console.error("Erro ao consultar /admin/knowledge:", err);
    }
  }

  // ===========================================================
  // NOVA FUNÇÃO — SUPORTA MÚLTIPLOS ARQUIVOS PPTX AO MESMO TEMPO
  // ===========================================================
  async function handleUpload() {
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
      uploadStatus.textContent = "Selecione ao menos um arquivo PPTX.";
      return;
    }

    const files = Array.from(fileInput.files); // <-- pega todos os arquivos
    const step = stepSelect ? stepSelect.value : "diagnostico";

    // Validação (todos precisam ser .pptx)
    const invalid = files.some(f => !f.name.toLowerCase().endsWith(".pptx"));
    if (invalid) {
      uploadStatus.textContent = "Todos os arquivos devem ser PPTX.";
      return;
    }

    uploadStatus.textContent = `Enviando ${files.length} arquivo(s)...`;

    const formData = new FormData();
    formData.append("step", step);

    // Adiciona todos os arquivos ao FormData
    files.forEach(file => {
      formData.append("files", file);
    });

    try {
      const res = await fetch(`${BACKEND_URL}/admin/upload-pptx`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errText = await res.text();
        console.error("Erro upload:", res.status, errText);
        uploadStatus.textContent = "Erro ao enviar os arquivos.";
        return;
      }

      const data = await res.json();
      uploadStatus.textContent =
        `Upload concluído. ${data.added} arquivo(s) processado(s). ` +
        `Total na base: ${data.docs_total}.`;

      await refreshStats();

    } catch (err) {
      console.error(err);
      uploadStatus.textContent =
        "Erro de rede ao enviar arquivos. Verifique se o backend está rodando.";
    }
  }

  // ----------------------------------------
  // Recarregar Base
  // ----------------------------------------
  async function handleReload() {
    if (reloadStatus) {
      reloadStatus.textContent = "Recarregando base do disco...";
    }

    try {
      const res = await fetch(`${BACKEND_URL}/admin/reload`, {
        method: "POST",
      });

      if (!res.ok) {
        const errText = await res.text();
        console.error("Erro reload:", res.status, errText);
        reloadStatus.textContent =
          "Erro ao recarregar base. Veja o console.";
        return;
      }

      const data = await res.json();
      reloadStatus.textContent =
        `Base recarregada. Documentos: ${data.stats.docs}.`;

      await refreshStats();
    } catch (err) {
      console.error(err);
      reloadStatus.textContent =
        "Erro ao recarregar base. Verifique backend.";
    }
  }

  if (uploadBtn) uploadBtn.addEventListener("click", handleUpload);
  if (reloadBtn) reloadBtn.addEventListener("click", handleReload);

  // Carrega status inicial
  refreshStats();
});
