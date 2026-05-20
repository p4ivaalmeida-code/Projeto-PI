const $ = (s) => document.querySelector(s);

const API_URL = "https://projeto-pi-6yop.onrender.com";

function escapeHtml(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function setMsg(text, type) {
  const el = $("#msg");
  el.className = "msg " + (type || "");
  el.textContent = text || "";
}

async function api(path, options = {}) {
  const res = await fetch(API_URL + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data?.error || `Erro HTTP ${res.status}`);
  }

  return data;
}

async function carregar() {
  const empresas = await api("/api/empresas");

  $("#contador").textContent = `${empresas.length} empresa(s)`;

  $("#tbody").innerHTML = empresas
    .map(
      (e) => `
      <tr>
        <td>${e.id}</td>
        <td>${escapeHtml(e.nome)}</td>
        <td><span class="badge">${escapeHtml(e.nome_normalizado)}</span></td>
      </tr>
    `
    )
    .join("");
}

$("#btnRecarregar").addEventListener("click", () => {
  setMsg("Recarregando...", "");

  carregar()
    .then(() => setMsg("", ""))
    .catch((e) => setMsg(e.message, "err"));
});

$("#form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const nome = $("#nome").value.trim();

  if (!nome) {
    setMsg("Digite um nome antes de cadastrar.", "err");
    return;
  }

  try {
    await api("/api/empresas", {
      method: "POST",
      body: JSON.stringify({ nome }),
    });

    $("#nome").value = "";

    setMsg("Cadastrado com sucesso.", "ok");

    await carregar();
  } catch (err) {
    setMsg(err.message, "err");
  }
});

carregar().catch((e) => setMsg(e.message, "err"));
