const API = "/api";

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

function formatMoney(value) {
  return Number(value).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

function formatCpfInput(value) {
  const digits = value.replace(/\D/g, "").slice(0, 11);
  if (digits.length <= 3) return digits;
  if (digits.length <= 6) return `${digits.slice(0, 3)}.${digits.slice(3)}`;
  if (digits.length <= 9) {
    return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6)}`;
  }
  return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6, 9)}-${digits.slice(9)}`;
}

function cpfSomenteDigitos(cpf) {
  return cpf.replace(/\D/g, "");
}

function toast(message, type = "success") {
  let container = $("#toasts");
  if (!container) {
    container = document.createElement("div");
    container.id = "toasts";
    container.className = "toast-container";
    container.setAttribute("aria-live", "polite");
    document.body.append(container);
  }
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = message;
  container.append(el);
  setTimeout(() => el.remove(), 4200);
}

const PORTAL_TOKEN_KEY = "portal_token";

function getPortalToken() {
  return sessionStorage.getItem(PORTAL_TOKEN_KEY);
}

function setPortalToken(token) {
  if (token) sessionStorage.setItem(PORTAL_TOKEN_KEY, token);
  else sessionStorage.removeItem(PORTAL_TOKEN_KEY);
}

async function request(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    let msg = data.detail || data.message || "Erro na requisição.";
    if (typeof msg !== "string") {
      msg = Array.isArray(msg) ? msg.map((e) => e.msg || e).join(", ") : JSON.stringify(msg);
    }
    throw new Error(msg);
  }
  return data;
}

async function portalRequest(path, options = {}) {
  const token = getPortalToken();
  if (!token) throw new Error("Sessão do cliente não encontrada. Entre com seu CPF.");

  return request(path, {
    ...options,
    headers: {
      "X-Portal-Token": token,
      ...options.headers,
    },
  });
}

function showScreen(id) {
  $$(".screen").forEach((s) => s.classList.remove("active"));
  $(`#${id}`)?.classList.add("active");
}
