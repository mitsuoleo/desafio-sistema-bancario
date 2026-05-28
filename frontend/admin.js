const ADMIN_TOKEN_KEY = "admin_token";

function getAdminToken() {
  return sessionStorage.getItem(ADMIN_TOKEN_KEY);
}

function setAdminToken(token) {
  sessionStorage.setItem(ADMIN_TOKEN_KEY, token);
}

function clearAdminToken() {
  sessionStorage.removeItem(ADMIN_TOKEN_KEY);
}

async function adminRequest(path, options = {}) {
  const token = getAdminToken();
  if (!token) throw new Error("Sessão administrativa expirada.");

  return request(path, {
    ...options,
    headers: {
      "X-Admin-Token": token,
      ...options.headers,
    },
  });
}

function entrarAdmin(usuario) {
  $("#admin-user-label").textContent = usuario;
  showScreen("screen-admin-app");
  showAdminView("resumo");
  carregarResumo();
}

function showAdminView(name) {
  $$(".admin-view").forEach((v) => v.classList.remove("active"));
  $(`#admin-view-${name}`)?.classList.add("active");
  $$(".sidebar--admin .nav-item").forEach((n) => {
    n.classList.toggle("active", n.dataset.adminView === name);
  });
  const titles = { resumo: "Visão geral", busca: "Buscar por CPF", excluir: "Excluir contas e clientes" };
  $("#admin-page-title").textContent = titles[name] || name;
}

$$(".sidebar--admin .nav-item").forEach((btn) => {
  btn.addEventListener("click", () => showAdminView(btn.dataset.adminView));
});

async function carregarResumo() {
  try {
    const data = await adminRequest("/admin/resumo");
    $("#admin-stats").innerHTML = `
      <div class="stat-card card">
        <span class="stat-label">Clientes</span>
        <strong class="stat-value">${data.total_clientes}</strong>
      </div>
      <div class="stat-card card">
        <span class="stat-label">Contas</span>
        <strong class="stat-value">${data.total_contas}</strong>
      </div>
      <div class="stat-card card">
        <span class="stat-label">Saldo total</span>
        <strong class="stat-value">${formatMoney(data.saldo_total)}</strong>
      </div>
    `;

    const tbody = $("#tabela-admin-contas");
    if (!data.contas.length) {
      tbody.innerHTML =
        '<tr><td colspan="5" class="empty">Nenhuma conta cadastrada.</td></tr>';
      return;
    }

    tbody.innerHTML = data.contas
      .map(
        (c) => `
      <tr>
        <td>${c.agencia} / ${c.numero}</td>
        <td>${c.titular}</td>
        <td>${c.cpf_formatado}</td>
        <td>${formatMoney(c.saldo)}</td>
        <td>${c.transacoes_hoje}</td>
      </tr>`
      )
      .join("");
  } catch (err) {
    toast(err.message, "error");
    if (err.message.includes("autorizado") || err.message.includes("401")) {
      clearAdminToken();
      showScreen("screen-admin-login");
    }
  }
}

function renderDetalheCliente(data) {
  const box = $("#resultado-busca");
  box.classList.remove("hidden");

  const contasHtml = data.contas
    .map((c) => {
      const transHtml = c.transacoes.length
        ? `<div class="extrato-itens-container">` +
          c.transacoes
            .map(
              (t) => `
          <div class="extrato-item ${t.tipo.toLowerCase()}">
            <div class="extrato-item-meta">
              <span class="extrato-item-title">${t.tipo}</span>
              <span class="extrato-item-date">${t.data}</span>
            </div>
            <span class="extrato-item-value">${t.tipo.toLowerCase() === 'deposito' ? '+' : '-'} ${formatMoney(t.valor)}</span>
          </div>`
            )
            .join("") +
          `</div>`
        : '<div class="empty" style="padding: 1rem;"><p>Sem movimentações registradas para esta conta.</p></div>';

      return `
      <article class="card admin-conta-detalhe">
        <header class="admin-conta-header">
          <div>
            <h4>Conta nº ${c.numero} · Agência ${c.agencia}</h4>
            <div class="saldo-inline">${formatMoney(c.saldo)}</div>
          </div>
          <span class="meta">${c.transacoes_hoje}/${c.limite_transacoes_dia} Transações Hoje</span>
        </header>
        <p class="meta">Limites operacionais: Saque diário de <strong>${formatMoney(c.limite_saque)}</strong> · Máx <strong>${c.limite_saques_dia} saques</strong>/dia</p>
        <h5 style="margin-top: 1rem; margin-bottom: 0.5rem;">Registro de Transações</h5>
        ${transHtml}
      </article>`;
    })
    .join("");

  box.innerHTML = `
    <article class="card admin-cliente-detalhe">
      <h3>Perfil Cadastral: ${data.nome}</h3>
      <div class="meta-grid" style="margin-top: 1.5rem;">
        <div><span>CPF</span><strong>${data.cpf_formatado}</strong></div>
        <div><span>Nascimento</span><strong>${data.data_nascimento}</strong></div>
        <div class="span-2"><span>Endereço Residencial</span><strong>${data.endereco}</strong></div>
      </div>
    </article>
    <h3 class="section-title" style="margin-top: 1rem; margin-bottom: 0.5rem;">${data.contas.length} conta(s) vinculada(s)</h3>
    ${contasHtml || '<div class="empty card"><p>Este cliente não possui contas bancárias vinculadas.</p></div>'}
  `;
}

$("#form-admin-login")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  try {
    const res = await request("/admin/login", {
      method: "POST",
      body: JSON.stringify({
        usuario: fd.get("usuario"),
        senha: fd.get("senha"),
      }),
    });
    setAdminToken(res.token);
    entrarAdmin(res.usuario);
    toast(res.mensagem);
  } catch (err) {
    toast(err.message, "error");
  }
});

$("#input-cpf-busca")?.addEventListener("input", (e) => {
  e.target.value = formatCpfInput(e.target.value);
});

$("#form-busca-cpf")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const cpf = cpfSomenteDigitos(new FormData(e.target).get("cpf"));
  if (cpf.length !== 11) {
    toast("Informe um CPF com 11 dígitos.", "error");
    return;
  }
  try {
    const data = await adminRequest(`/admin/clientes/${cpf}`);
    renderDetalheCliente(data);
  } catch (err) {
    toast(err.message, "error");
    $("#resultado-busca")?.classList.add("hidden");
  }
});

$("#btn-admin-refresh")?.addEventListener("click", () => carregarResumo());

$("#btn-admin-sair")?.addEventListener("click", () => {
  clearAdminToken();
  showScreen("screen-admin-login");
  $("#form-admin-login").reset();
  toast("Sessão administrativa encerrada.");
});

$("#excluir-cliente-cpf")?.addEventListener("input", (e) => {
  e.target.value = formatCpfInput(e.target.value);
});

$("#form-excluir-cliente")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const cpf = cpfSomenteDigitos(new FormData(e.target).get("cpf"));
  if (cpf.length !== 11) {
    toast("Informe um CPF com 11 dígitos.", "error");
    return;
  }
  if (!confirm("CUIDADO: Tem certeza absoluta que deseja excluir este cliente e todas as suas contas permanentemente? Esta ação não pode ser desfeita!")) {
    return;
  }
  try {
    const res = await adminRequest(`/admin/clientes/${cpf}`, {
      method: "DELETE",
    });
    toast(res.mensagem);
    e.target.reset();
    carregarResumo();
  } catch (err) {
    toast(err.message, "error");
  }
});

$("#form-excluir-conta")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const numero = parseInt(new FormData(e.target).get("numero"), 10);
  if (!numero) {
    toast("Informe um número de conta válido.", "error");
    return;
  }
  if (!confirm(`CUIDADO: Tem certeza que deseja excluir a conta nº ${numero} permanentemente? Todos os registros de saldo e transações desta conta serão perdidos!`)) {
    return;
  }
  try {
    const res = await adminRequest(`/admin/contas/${numero}`, {
      method: "DELETE",
    });
    toast(res.mensagem);
    e.target.reset();
    carregarResumo();
  } catch (err) {
    toast(err.message, "error");
  }
});

if (getAdminToken()) {
  entrarAdmin("admin");
} else {
  showScreen("screen-admin-login");
}
