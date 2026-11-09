const $ = (s) => document.querySelector(s);

// Vazio = chama a API no mesmo endereço (o Flask que está rodando aqui)
const API_URL = "";

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
  if (!res.ok) throw new Error(data?.error || `Erro HTTP ${res.status}`);
  return data;
}

async function carregar() {
  const empresas = await api("/api/empresas");

  $("#contador").textContent = `${empresas.length} empresa(s)`;

  $("#tbody").innerHTML = empresas
    .map((e) => {
      // só os cadastros do usuário recebem o aviso de duplicata
      const duplicada = e.duplicada && e.origem === "cadastro";
      const similaridade = e.maior_similaridade || 0;

      return `
      <tr class="${duplicada ? "linha-duplicada" : ""}">
        <td>${e.id}</td>
        <td>
          ${escapeHtml(e.nome)}
          ${e.origem === "base" ? '<span class="badge">base</span>' : ""}
          ${duplicada ? '<div class="duplicada-label">Possível duplicata</div>' : ""}
        </td>
        <td><span class="badge">${escapeHtml(e.nome_normalizado)}</span></td>
        <td>${duplicada ? `<span class="similaridade">${similaridade}%</span>` : "-"}</td>
      </tr>
    `;
    })
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
    const resposta = await api("/api/empresas", {
      method: "POST",
      body: JSON.stringify({ nome }),
    });

    $("#nome").value = "";

    if (resposta.duplicada) {
      const lista = resposta.possiveis_duplicatas
        .map((d) => `${d.nome} (${d.similaridade}%)`)
        .join(" | ");
      setMsg(`⚠ Empresa possivelmente duplicada: ${lista}`, "err");
    } else {
      setMsg("Cadastrado com sucesso.", "ok");
    }

    await carregar();
  } catch (err) {
    setMsg(err.message, "err");
  }
});

$("#btnReset").addEventListener("click", async () => {
  const confirmar = confirm(
    "Apagar os cadastros feitos por você? (A base de grandes empresas será mantida.)"
  );
  if (!confirmar) return;

  try {
    await api("/api/empresas/reset", { method: "DELETE" });
    setMsg("Cadastros apagados. A base foi mantida.", "ok");
    await carregar();
  } catch (err) {
    setMsg(err.message, "err");
  }
});

carregar().catch((e) => setMsg(e.message, "err"));