const $ = (s) => document.querySelector(s);

const API_URL =
  "https://projeto-pi-6yop.onrender.com";


// =========================
// ESCAPE HTML
// =========================

function escapeHtml(str) {

  return String(str)

    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}


// =========================
// MENSAGENS
// =========================

function setMsg(text, type) {

  const el = $("#msg");

  el.className =
    "msg " + (type || "");

  el.textContent =
    text || "";
}


// =========================
// API
// =========================

async function api(
  path,
  options = {}
) {

  const res = await fetch(

    API_URL + path,

    {
      headers: {
        "Content-Type":
          "application/json",
      },

      ...options,
    }
  );

  const data =
    await res.json()
      .catch(() => ({}));

  if (!res.ok) {

    throw new Error(
      data?.error ||
      `Erro HTTP ${res.status}`
    );
  }

  return data;
}


// =========================
// CARREGAR EMPRESAS
// =========================

async function carregar() {

  const empresas =
    await api("/api/empresas");

  $("#contador").textContent =
    `${empresas.length} empresa(s)`;


  $("#tbody").innerHTML =

    empresas

      .map((e) => {

        const duplicada =
          e.duplicada;

        const similaridade =
          e.maior_similaridade || 0;

        return `

        <tr class="${
          duplicada
            ? "linha-duplicada"
            : ""
        }">

          <td>
            ${e.id}
          </td>

          <td>

            ${escapeHtml(e.nome)}

            ${
              duplicada
                ? `
                <div class="duplicada-label">
                  Possível duplicata
                </div>
                `
                : ""
            }

          </td>

          <td>

            <span class="badge">
              ${escapeHtml(
                e.nome_normalizado
              )}
            </span>

          </td>

          <td>

            ${
              duplicada
                ? `
                  <span class="similaridade">
                    ${similaridade}%
                  </span>
                `
                : "-"
            }

          </td>

        </tr>
        `;
      })

      .join("");
}


// =========================
// BOTÃO RECARREGAR
// =========================

$("#btnRecarregar")

  .addEventListener(

    "click",

    () => {

      setMsg(
        "Recarregando...",
        ""
      );

      carregar()

        .then(() =>
          setMsg("", "")
        )

        .catch((e) =>
          setMsg(
            e.message,
            "err"
          )
        );
    }
  );


// =========================
// FORMULÁRIO
// =========================

$("#form")

  .addEventListener(

    "submit",

    async (e) => {

      e.preventDefault();

      const nome =

        $("#nome")
          .value
          .trim();

      if (!nome) {

        setMsg(

          "Digite um nome antes de cadastrar.",

          "err"
        );

        return;
      }

      try {

        const resposta =

          await api(

            "/api/empresas",

            {
              method: "POST",

              body: JSON.stringify({
                nome
              }),
            }
          );

        $("#nome").value = "";

        // DUPLICIDADE

        if (resposta.duplicada) {

          const listaDuplicatas =

            resposta
              .possiveis_duplicatas

              .map(
                (d) =>
                  `${d.nome} (${d.similaridade}%)`
              )

              .join(" | ");

          setMsg(

            `⚠ Empresa possivelmente duplicada: ${listaDuplicatas}`,

            "err"
          );

        } else {

          setMsg(
            "Cadastrado com sucesso.",
            "ok"
          );
        }

        await carregar();

      } catch (err) {

        setMsg(
          err.message,
          "err"
        );
      }
    }
  );


// =========================
// RESETAR BANCO
// =========================

$("#btnReset")

  .addEventListener(

    "click",

    async () => {

      const confirmar = confirm(

        "Tem certeza que deseja apagar TODAS as empresas?"
      );

      if (!confirmar) return;

      try {

        await api(

          "/api/empresas/reset",

          {
            method: "DELETE"
          }
        );

        setMsg(
          "Banco resetado com sucesso.",
          "ok"
        );

        await carregar();

      } catch (err) {

        setMsg(
          err.message,
          "err"
        );
      }
    }
  );


// =========================
// INICIAR
// =========================

carregar()

  .catch((e) =>

    setMsg(
      e.message,
      "err"
    )
  );
