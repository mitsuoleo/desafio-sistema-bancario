const STORAGE_KEY = "cliente_sessao";

const clienteState = {
  sessao: null,
};

const clienteTitles = {
  inicio: "Início",
  depositar: "Depositar",
  sacar: "Sacar",
  extrato: "Extrato",
};

function salvarSessao(sessao) {
  clienteState.sessao = sessao;
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(sessao));
}

function carregarSessaoArmazenada() {
  const raw = sessionStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function limparSessao() {
  clienteState.sessao = null;
  sessionStorage.removeItem(STORAGE_KEY);
  setPortalToken(null);
}

function aplicarRespostaPortal(res) {
  if (res.token) setPortalToken(res.token);
  entrarNoApp(res.sessao);
}

function entrarNoApp(sessao) {
  salvarSessao(sessao);
  $("#sidebar-nome").textContent = sessao.nome;
  $("#sidebar-cpf").textContent = sessao.cpf_formatado;
  renderContasCliente();
  preencherSelectsConta();
  showScreen("screen-app");
  showClienteView("inicio");
}

function renderContasCliente() {
  const lista = $("#lista-contas-cliente");
  const contas = clienteState.sessao?.contas || [];

  if (!contas.length) {
    lista.innerHTML = '<p class="empty card">Nenhuma conta vinculada ao seu CPF.</p>';
    return;
  }

  lista.innerHTML = contas
    .map(
      (c) => `
    <article class="account-card account-card--highlight">
      <header>
        <div>
          <strong>Ag. ${c.agencia}</strong>
          <div class="meta">Conta ${c.numero}</div>
        </div>
        <span class="meta">${c.transacoes_hoje}/${c.limite_transacoes_dia} trans. hoje</span>
      </header>
      <div class="saldo">${formatMoney(c.saldo)}</div>
      <div class="meta">Limite saque: ${formatMoney(c.limite_saque)} · ${c.limite_saques_dia} saques/dia</div>
    </article>`
    )
    .join("");
}

function preencherSelectsConta() {
  const contas = clienteState.sessao?.contas || [];
  const html = contas
    .map(
      (c) =>
        `<option value="${c.numero}">Conta ${c.numero} — ${formatMoney(c.saldo)}</option>`
    )
    .join("");

  ["deposito-conta", "saque-conta", "extrato-conta"].forEach((id) => {
    const el = $(`#${id}`);
    if (el) el.innerHTML = html;
  });
}

function showClienteView(name) {
  $$(".cliente-view").forEach((v) => v.classList.remove("active"));
  $(`#view-${name}`)?.classList.add("active");
  $$(".sidebar--cliente .nav-item").forEach((n) => {
    n.classList.toggle("active", n.dataset.view === name);
  });
  $("#cliente-page-title").textContent = clienteTitles[name] || name;
}

$$(".sidebar--cliente .nav-item").forEach((btn) => {
  btn.addEventListener("click", () => showClienteView(btn.dataset.view));
});

$("#input-cpf-login")?.addEventListener("input", (e) => {
  e.target.value = formatCpfInput(e.target.value);
});

$("#form-login-cpf")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const cpf = cpfSomenteDigitos(new FormData(e.target).get("cpf"));
  if (cpf.length !== 11) {
    toast("Informe um CPF com 11 dígitos.", "error");
    return;
  }

  try {
    const res = await request(`/portal/sessao/${cpf}`);
    aplicarRespostaPortal(res);
    toast(`Bem-vindo(a), ${res.sessao.nome}!`);
  } catch (err) {
    if (err.message.includes("não cadastrado")) {
      $("#input-cpf-cadastro").value = formatCpfInput(cpf);
      showScreen("screen-cadastro");
      return;
    }
    toast(err.message, "error");
  }
});

$("#voltar-login")?.addEventListener("click", (e) => {
  e.preventDefault();
  showScreen("screen-login");
});

$("#form-cadastro")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  try {
    const res = await request("/portal/cadastro", {
      method: "POST",
      body: JSON.stringify({
        cpf: cpfSomenteDigitos(fd.get("cpf")),
        nome: fd.get("nome"),
        data_nascimento: fd.get("data_nascimento"),
        endereco: fd.get("endereco"),
      }),
    });
    aplicarRespostaPortal(res);
    toast(res.mensagem);
  } catch (err) {
    toast(err.message, "error");
  }
});

$("#btn-nova-conta")?.addEventListener("click", async () => {
  if (!clienteState.sessao) return;
  try {
    const res = await portalRequest("/portal/contas", { method: "POST" });
    aplicarRespostaPortal(res);
    toast(res.mensagem);
  } catch (err) {
    toast(err.message, "error");
  }
});

$("#btn-sair")?.addEventListener("click", () => {
  limparSessao();
  showScreen("screen-login");
  $("#form-login-cpf").reset();
  toast("Sessão encerrada.");
});

$("#form-deposito")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  try {
    const res = await portalRequest("/portal/depositos", {
      method: "POST",
      body: JSON.stringify({
        cpf: clienteState.sessao.cpf,
        valor: parseFloat(fd.get("valor")),
        numero_conta: parseInt(fd.get("numero_conta"), 10),
      }),
    });
    aplicarRespostaPortal(res);
    e.target.reset();
    preencherSelectsConta();
    toast(res.mensagem);
  } catch (err) {
    toast(err.message, "error");
  }
});

$("#form-saque")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  try {
    const res = await portalRequest("/portal/saques", {
      method: "POST",
      body: JSON.stringify({
        cpf: clienteState.sessao.cpf,
        valor: parseFloat(fd.get("valor")),
        numero_conta: parseInt(fd.get("numero_conta"), 10),
      }),
    });
    aplicarRespostaPortal(res);
    e.target.reset();
    preencherSelectsConta();
    toast(res.mensagem);
  } catch (err) {
    toast(err.message, "error");
  }
});

$("#form-extrato")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const numero = parseInt(new FormData(e.target).get("numero_conta"), 10);
  try {
    const data = await portalRequest(`/portal/extrato?numero_conta=${numero}`);
    const box = $("#extrato-resultado");
    box.classList.remove("hidden");

    const itens = data.transacoes.length
      ? data.transacoes
          .map(
            (t) => `
        <div class="extrato-item ${t.tipo.toLowerCase()}">
          <span>${t.tipo}</span>
          <span>${formatMoney(t.valor)} · ${t.data}</span>
        </div>`
          )
          .join("")
      : '<p class="meta">Nenhuma movimentação registrada.</p>';

    box.innerHTML = `
      <h3>Conta ${data.conta} · Ag. ${data.agencia}</h3>
      <p class="meta">${data.titular} · ${data.cpf_formatado}</p>
      ${itens}
      <p class="extrato-saldo">Saldo: <strong>${formatMoney(data.saldo)}</strong></p>
      <p class="meta">Transações hoje: ${data.transacoes_hoje}/${data.limite_transacoes_dia}</p>
    `;
  } catch (err) {
    toast(err.message, "error");
  }
});

const sessaoSalva = carregarSessaoArmazenada();
if (sessaoSalva && getPortalToken()) {
  entrarNoApp(sessaoSalva);
} else {
  limparSessao();
  showScreen("screen-login");
}
