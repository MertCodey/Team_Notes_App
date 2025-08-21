// Basic front-end to interact with your Flask API
// Assumes endpoints: /register, /login, /logout, /notes (GET/POST/DELETE)

const apiBase = (window.APP_CONFIG && window.APP_CONFIG.apiBase) || "";
let accessToken = localStorage.getItem("access_token") || null;
let refreshToken = localStorage.getItem("refresh_token") || null;
let currentUserId = null; // filled after login/refresh by decoding JWT
let firstUnauthorized = (localStorage.getItem("first_unauth_done") === null);

const el = (sel, root=document) => root.querySelector(sel);
const els = (sel, root=document) => [...root.querySelectorAll(sel)];

function setTokens({ access, refresh }={}){
  if (access) {
    accessToken = access;
    localStorage.setItem("access_token", access);
    try {
      const payload = JSON.parse(atob(access.split(".")[1]));
      currentUserId = payload.sub ?? currentUserId;
    } catch(_) { /* ignore */ }
  }
  if (refresh) {
    refreshToken = refresh;
    localStorage.setItem("refresh_token", refresh);
  }
}

function headers(jwt=true){
  const h = { "Content-Type": "application/json" };
  if(jwt && accessToken) h["Authorization"] = `Bearer ${accessToken}`;
  return h;
}

function showLogin(){
  // tabs
  const lv = el("#loginView");
  const rv = el("#registerView");
  if (lv && rv){ lv.style.display = "block"; rv.style.display = "none"; }
  openModal("#loginModal");
}
function showRegister(){
  const lv = el("#loginView");
  const rv = el("#registerView");
  if (lv && rv){ lv.style.display = "none"; rv.style.display = "block"; }
  openModal("#loginModal");
}

async function tryRefresh(){
  if (!refreshToken) return false;
  try{
    const res = await fetch(apiBase + "/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${refreshToken}` }
    });
    if (res.ok){
      const data = await res.json();
      setTokens({ access: data.access_token });
      // show logged-in controls
      el("#loginBtn").style.display = "none";
      el("#logoutBtn").style.display = "inline-flex";
      return true;
    }
  }catch(_){ /* ignore */ }
  return false;
}

async function api(path, {method="GET", body, jwt=false}={}){
  const doFetch = async () => fetch(apiBase + path, {
    method,
    headers: headers(jwt),
    body: body ? JSON.stringify(body) : undefined,
  });

  let res = await doFetch();
  if (res.status === 401 && jwt) {
    const refreshed = await tryRefresh();
    if (refreshed) res = await doFetch();
  }

  if(!res.ok){
    if (res.status === 401) {
      if (firstUnauthorized){
        showRegister();
        localStorage.setItem("first_unauth_done", "1");
        firstUnauthorized = false;
      } else {
        showLogin();
      }
    }
    const txt = await res.text();
    throw new Error(txt || res.statusText);
  }
  const ct = res.headers.get("content-type") || "";
  return ct.includes("application/json") ? res.json() : res.text();
}

function openModal(id){ el(id).classList.remove("hidden"); el(id).setAttribute("aria-hidden","false"); }
function closeModal(id){ el(id).classList.add("hidden"); el(id).setAttribute("aria-hidden","true"); }

function groupByUser(notes){
  const map = new Map();
  for(const n of notes){
    const uid = String(n.user_id ?? "unknown");
    if(!map.has(uid)) map.set(uid, []);
    map.get(uid).push(n);
  }
  // Ensure current user gets a board even with 0 notes
  if (currentUserId != null) {
    const key = String(currentUserId);
    if (!map.has(key)) map.set(key, []);
  }
  return map;
}

function usernameFor(userId){
  // Placeholder: if API exposes usernames per note later, replace with that
  return String(userId) === String(currentUserId) ? "You" : `User #${userId}`;
}

function renderBoards(notes){
  const container = el("#boards");
  container.innerHTML = "";
  const grouped = groupByUser(notes);
  for(const [userId, userNotes] of grouped){
    const isMe = String(userId) === String(currentUserId);
    const board = document.createElement("article");
    board.className = "board";
    if (isMe) board.id = `user-board-${String(userId)}`;
    board.innerHTML = `
      <div class="board-header">
        <h3 class="board-title">${usernameFor(userId)}'s Window</h3>
        ${isMe ? '<button class="btn addBtn">Add</button>' : ''}
      </div>
      <div class="board-body">
        <div class="notes"></div>
        ${isMe ? `
        <form class="add-note">
          <input name="title" placeholder="Note title" required />
          <textarea name="content" placeholder="Note content" required></textarea>
          <button class="btn primary" type="submit">Save</button>
        </form>` : ''}
      </div>
    `;
    const list = el(".notes", board);
    for(const n of userNotes){
      const item = document.createElement("div");
      item.className = "note-title";
      item.textContent = n.title;
      item.addEventListener("click", () => {
        el("#noteTitle").textContent = n.title;
        el("#noteContent").textContent = n.content;
        openModal("#noteModal");
      });
      list.appendChild(item);
    }

    // handle add
    const form = el("form.add-note", board);
    if(form){
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const fd = new FormData(form);
        try{
          await api("/notes", {
            method:"POST",
            jwt:true,
            body:{ title: fd.get("title"), content: fd.get("content") }
          });
          await bootstrap();
          form.reset();
        }catch(err){
          alert("Could not add note: " + err.message);
        }
      });
    }

    container.appendChild(board);
  }
}

async function bootstrap(){
  // load notes for everyone
  try{
    const notes = await api("/notes");
    renderBoards(notes);
  }catch(err){
    console.error(err);
  }
}

async function focusMyBoard(){
  await bootstrap();
  const my = document.getElementById(`user-board-${String(currentUserId)}`);
  if (my) my.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function login(username, password){
  const data = await api("/login", {method:"POST", body:{username, password}});
  setTokens({ access: data.access_token, refresh: data.refresh_token });
  el("#loginBtn").style.display = "none";
  el("#logoutBtn").style.display = "inline-flex";
  await focusMyBoard();
}

function logout(){
  accessToken = null;
  refreshToken = null;
  currentUserId = null;
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  el("#loginBtn").style.display = "inline-flex";
  el("#logoutBtn").style.display = "none";
  bootstrap();
}

// Wire UI
window.addEventListener("DOMContentLoaded", async () => {
  // Restore session
  if (accessToken) {
    try {
      const payload = JSON.parse(atob(accessToken.split(".")[1]));
      currentUserId = payload.sub;
      el("#loginBtn").style.display = "none";
      el("#logoutBtn").style.display = "inline-flex";
    } catch(_) {
      accessToken = null;
      localStorage.removeItem("access_token");
    }
  }
  // If no access but we do have a refresh, silently refresh
  if (!accessToken && refreshToken) {
    await tryRefresh();
  }

  await bootstrap();

  el("#loginBtn").addEventListener("click", () => showLogin());
  el("#closeLogin").addEventListener("click", () => closeModal("#loginModal"));
  el("#closeNote").addEventListener("click", () => closeModal("#noteModal"));

  const tabLogin = el("#tabLogin");
  const tabRegister = el("#tabRegister");
  tabLogin?.addEventListener("click", showLogin);
  tabRegister?.addEventListener("click", showRegister);

  el("#loginForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    try {
      await login(fd.get("username"), fd.get("password"));
      closeModal("#loginModal");
    } catch(err) {
      alert("Login failed: " + err.message);
    }
  });

  el("#registerForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    try{
      await api("/register", { method:"POST", body:{
        username: fd.get("username"),
        email: fd.get("email"),
        password: fd.get("password")
      }});
      alert("Registered! Please log in.");
      showLogin();
    }catch(err){
      alert("Register failed: " + err.message);
    }
  });

  // CTA
  const cta = el("#createWindowBtn");
  cta?.addEventListener("click", async () => {
    if (!accessToken && !refreshToken) {
      showRegister();
    } else if (!accessToken && refreshToken) {
      const ok = await tryRefresh();
      if (ok) await focusMyBoard(); else showLogin();
    } else {
      await focusMyBoard();
    }
  });
});

el("#logoutBtn")?.addEventListener("click", logout);
