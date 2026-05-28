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
    lista.innerHTML = '<div class="empty card"><p>Nenhuma conta vinculada ao seu CPF.</p></div>';
    return;
  }

  lista.innerHTML = contas
    .map(
      (c) => `
    <article class="account-card account-card--highlight">
      <header>
        <div>
          <strong>Agência ${c.agencia}</strong>
          <div class="meta">Conta nº ${c.numero}</div>
        </div>
        <span class="account-card-badge">${c.transacoes_hoje}/${c.limite_transacoes_dia} Transações</span>
      </header>
      <div class="account-card-chip"></div>
      <div class="saldo">${formatMoney(c.saldo)}</div>
      <div class="meta-footer">
        <div class="limites">
          Saque máx: <strong>${formatMoney(c.limite_saque)}</strong><br>
          Restante: <strong>${c.limite_saques_dia} saques/dia</strong>
        </div>
        <span class="account-card-brand">◇ DIO Bank</span>
      </div>
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
  
  // Concatenar os campos de endereço
  const rua = fd.get("rua").trim();
  const numero = fd.get("numero").trim();
  const complemento = fd.get("complemento") ? fd.get("complemento").trim() : "";
  const bairro = fd.get("bairro").trim();
  const cidade = fd.get("cidade").trim();
  const estado = fd.get("estado");
  
  const enderecoCompleto = `${rua}, nº ${numero}${complemento ? ` - ${complemento}` : ""} - ${bairro} - ${cidade}/${estado}`;

  try {
    const res = await request("/portal/cadastro", {
      method: "POST",
      body: JSON.stringify({
        cpf: cpfSomenteDigitos(fd.get("cpf")),
        nome: fd.get("nome"),
        data_nascimento: fd.get("data_nascimento"),
        endereco: enderecoCompleto,
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
      ? `<div class="extrato-itens-container">` +
        data.transacoes
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
      : '<div class="empty" style="padding: 1.5rem;"><p>Nenhuma movimentação registrada nesta conta.</p></div>';

    box.innerHTML = `
      <h3>Conta ${data.conta} · Agência ${data.agencia}</h3>
      <p class="meta">${data.titular} · ${data.cpf_formatado}</p>
      ${itens}
      <div class="extrato-saldo" style="margin-top: 1.5rem;">
        <span>Saldo Disponível</span>
        <strong>${formatMoney(data.saldo)}</strong>
      </div>
      <p class="meta" style="margin-top: 0.5rem; font-size: 0.8rem;">Transações hoje: ${data.transacoes_hoje}/${data.limite_transacoes_dia}</p>
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

function formatDataNascimentoInput(value) {
  const digits = value.replace(/\D/g, "").slice(0, 8);
  if (digits.length <= 2) return digits;
  if (digits.length <= 4) return `${digits.slice(0, 2)}/${digits.slice(2)}`;
  return `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`;
}

$("#input-nascimento")?.addEventListener("input", (e) => {
  e.target.value = formatDataNascimentoInput(e.target.value);
});
