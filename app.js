const state = {
  items: [],
  favorites: [],
  user: null,
  users: [],
  codes: [],
  pendingVerifyEmail: null,
  notifications: [],
  filters: { text: "", genre: "", type: "" },
  editingId: null
}

const FALLBACK_IMAGE = 'https://placehold.co/900x600/14141c/ffffff?text=NIRO'
const ACCESS_CODE = 'NIRO-2025'
const API_BASE = `${location.protocol}//${location.hostname}:8001`

// Persistencia en IndexedDB (kv store)
let db
const storage = {
  async init() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open('niroDB', 1)
      req.onupgradeneeded = () => {
        const d = req.result
        if (!d.objectStoreNames.contains('kv')) {
          d.createObjectStore('kv', { keyPath: 'key' })
        }
      }
      req.onsuccess = () => { db = req.result; resolve() }
      req.onerror = () => reject(req.error)
    })
  },
  async get(key) {
    if (!db) return null
    return new Promise((resolve, reject) => {
      const tx = db.transaction('kv', 'readonly')
      const store = tx.objectStore('kv')
      const r = store.get(key)
      r.onsuccess = () => resolve(r.result ? r.result.value : null)
      r.onerror = () => reject(r.error)
    })
  },
  async set(key, value) {
    if (!db) return
    return new Promise((resolve, reject) => {
      const tx = db.transaction('kv', 'readwrite')
      const store = tx.objectStore('kv')
      const r = store.put({ key, value })
      r.onsuccess = () => resolve()
      r.onerror = () => reject(r.error)
    })
  },
  async del(key) {
    if (!db) return
    return new Promise((resolve, reject) => {
      const tx = db.transaction('kv', 'readwrite')
      const store = tx.objectStore('kv')
      const r = store.delete(key)
      r.onsuccess = () => resolve()
      r.onerror = () => reject(r.error)
    })
  }
}

async function hydrateBlobUrls(items) {
  const list = items || state.items
  for (const it of list) {
    if (it.imageBlobKey) {
      try {
        const blob = await storage.get(it.imageBlobKey)
        if (blob) it.urlImage = URL.createObjectURL(blob)
      } catch {}
    }
    if (it.videoBlobKey) {
      try {
        const blob = await storage.get(it.videoBlobKey)
        if (blob) it.urlVideo = URL.createObjectURL(blob)
      } catch {}
    }
    if (it.type === 'Serie' && Array.isArray(it.seasons)) {
      for (let si = 0; si < it.seasons.length; si++) {
        const s = it.seasons[si]
        if (!Array.isArray(s.episodes)) continue
        for (let ei = 0; ei < s.episodes.length; ei++) {
          const ep = s.episodes[ei]
          if (ep.videoBlobKey) {
            try {
              const blob = await storage.get(ep.videoBlobKey)
              if (blob) ep.url = URL.createObjectURL(blob)
            } catch {}
          }
        }
      }
    }
  }
}

let syncChannel
let syncTimer
function computeSnapshot() {
  return {
    items: JSON.stringify(state.items),
    users: JSON.stringify(state.users),
    favorites: JSON.stringify(state.favorites),
    notifications: JSON.stringify(state.notifications),
    user: JSON.stringify(state.user)
  }
}
async function refreshFromStore() {
  const before = computeSnapshot()
  const ok = await loadRemote()
  if (!ok) {
    await loadLocal()
    await hydrateBlobUrls()
  }
  const after = computeSnapshot()
  if (before.items !== after.items || before.users !== after.users || before.favorites !== after.favorites || before.notifications !== after.notifications || before.user !== after.user) {
    renderCarousels()
    renderHero()
    renderCatalog()
    renderAdminList()
    renderUsersList()
    renderNotifications()
  }
}
function startAutoSync() {
  try {
    syncChannel = new BroadcastChannel('niro-sync')
    syncChannel.onmessage = async (e) => { if (e.data && e.data.type === 'update') await refreshFromStore() }
  } catch {}
  clearInterval(syncTimer)
  syncTimer = setInterval(refreshFromStore, 4000)
}

const els = {
  views: document.querySelectorAll('[data-view]'),
  navLinks: document.querySelectorAll('.nav-link'),
  navAdmin: document.querySelector('.nav-admin'),
  accountNavLink: document.querySelector('.nav .nav-link[data-route="account"]'),
  navLogout: document.getElementById('navLogout'),
  navLogout: document.getElementById('navLogout'),
  catalogGrid: document.getElementById('catalogGrid'),
  emptyState: document.getElementById('emptyState'),
  searchInput: document.getElementById('searchInput'),
  genreSelect: document.getElementById('genreSelect'),
  typeSelect: document.getElementById('typeSelect'),
  clearFilters: document.getElementById('clearFilters'),
  favoritesSection: document.getElementById('favoritesSection'),
  favoritesCarousel: document.getElementById('favoritesCarousel'),
  carouselTrend: document.getElementById('carousel-trend'),
  carouselPopular: document.getElementById('carousel-popular'),
  carouselRecommended: document.getElementById('carousel-recommended'),
  modal: document.getElementById('modal'),
  modalBody: document.getElementById('modalBody'),
  modalClose: document.getElementById('modalClose'),
  toastContainer: document.getElementById('toastContainer'),
  notifPanel: document.getElementById('notifPanel'),
  notifDot: document.getElementById('notifDot'),
  menuBtn: document.querySelector('.menu-btn'),
  notifBtn: document.querySelector('.notif-btn'),
  playerVideo: document.getElementById('playerVideo'),
  playerBackdrop: document.getElementById('playerBackdrop'),
  playerTitle: document.getElementById('playerTitle'),
  playerDesc: document.getElementById('playerDesc'),
  playerUI: document.getElementById('playerUI'),
  uiPlay: document.getElementById('uiPlay'),
  uiMute: document.getElementById('uiMute'),
  uiVolume: document.getElementById('uiVolume'),
  uiFullscreen: document.getElementById('uiFullscreen'),
  uiProgress: document.getElementById('uiProgress'),
  uiFill: document.getElementById('uiFill'),
  uiBuffer: document.getElementById('uiBuffer'),
  uiTime: document.getElementById('uiTime'),
  seasonSelect: document.getElementById('seasonSelect'),
  episodeSelect: document.getElementById('episodeSelect'),
  playerBadges: document.getElementById('playerBadges'),
  qualitySelect: document.getElementById('qualitySelect'),
  loginForm: document.getElementById('loginForm'),
  emailInput: document.getElementById('emailInput'),
  passwordInput: document.getElementById('passwordInput'),
  logoutBtn: document.getElementById('logoutBtn'),
  accountStatus: document.getElementById('accountStatus'),
  emailError: document.getElementById('emailError'),
  passwordError: document.getElementById('passwordError'),
  rememberCheck: document.getElementById('rememberCheck'),
  adminForm: document.getElementById('adminForm'),
  itemId: document.getElementById('itemId'),
  titleInput: document.getElementById('titleInput'),
  yearInput: document.getElementById('yearInput'),
  genreInput: document.getElementById('genreInput'),
  typeInput: document.getElementById('typeInput'),
  descInput: document.getElementById('descInput'),
  imageFileInput: document.getElementById('imageFileInput'),
  videoFileInput: document.getElementById('videoFileInput'),
  adminList: document.getElementById('adminList'),
  seasonNameInput: document.getElementById('seasonNameInput'),
  addSeasonBtn: document.getElementById('addSeasonBtn'),
  seasonList: document.getElementById('seasonList'),
  seriesSteps: document.getElementById('seriesSteps'),
  seriesEpisodesGroup: document.getElementById('seriesEpisodesGroup'),
  seasonPickSelect: document.getElementById('seasonPickSelect'),
  episodeTitleInput: document.getElementById('episodeTitleInput'),
  episodeFileInput: document.getElementById('episodeFileInput'),
  addEpisodeBtn: document.getElementById('addEpisodeBtn'),
  episodeAdminList: document.getElementById('episodeAdminList'),
  userForm: document.getElementById('userForm'),
  usersList: document.getElementById('usersList'),
  userEmailInput: document.getElementById('userEmailInput'),
  userNameInput: document.getElementById('userNameInput'),
  userPasswordInput: document.getElementById('userPasswordInput'),
  userRoleSelect: document.getElementById('userRoleSelect'),
  userAccessCodeInput: document.getElementById('userAccessCodeInput'),
  togglePass: document.getElementById('togglePass'),
  loginError: document.getElementById('loginError'),
  supportForm: document.getElementById('supportForm'),
  supportEmailInput: document.getElementById('supportEmailInput'),
  supportSubjectInput: document.getElementById('supportSubjectInput'),
  supportMessageInput: document.getElementById('supportMessageInput'),
  adminMenuBtn: document.getElementById('adminMenuBtn'),
  adminDrawer: document.getElementById('adminDrawer'),
  adminFormContainer: document.getElementById('adminFormContainer'),
  adminContentContainer: document.getElementById('adminContentContainer'),
  adminUsersContainer: document.getElementById('adminUsersContainer'),
  adminOverlay: document.getElementById('adminOverlay'),
  adminStats: document.getElementById('adminStats'),
  heroRotator: document.getElementById('heroRotator'),
  heroBg: document.getElementById('heroBg'),
  heroFeaturedTitle: document.getElementById('heroFeaturedTitle'),
  heroPlayBtn: document.getElementById('heroPlayBtn'),
  heroInfoBtn: document.getElementById('heroInfoBtn'),
  heroDescShort: document.getElementById('heroDescShort'),
  heroChips: document.getElementById('heroChips'),
  playerTopTitle: document.getElementById('playerTopTitle'),
  playerTopMeta: document.getElementById('playerTopMeta'),
  playerOSD: document.getElementById('playerOSD'),
  signupForm: document.getElementById('signupForm'),
  signupNameInput: document.getElementById('signupNameInput'),
  signupEmailInput: document.getElementById('signupEmailInput'),
  signupPasswordInput: document.getElementById('signupPasswordInput'),
  signupConfirmInput: document.getElementById('signupConfirmInput'),
  toggleSignupPass1: document.getElementById('toggleSignupPass1'),
  toggleSignupPass2: document.getElementById('toggleSignupPass2'),
  signupTermsCheck: document.getElementById('signupTermsCheck'),
  signupSubmitBtn: document.getElementById('signupSubmitBtn'),
  signupStrength: document.getElementById('signupStrength'),
  showSignup: document.getElementById('showSignup'),
  cancelSignup: document.getElementById('cancelSignup'),
  codeVerifyPanel: document.getElementById('codeVerifyPanel'),
  codeInput: document.getElementById('codeInput'),
  verifyCodeBtn: document.getElementById('verifyCodeBtn'),
  codeError: document.getElementById('codeError'),
  newCodeInput: document.getElementById('newCodeInput'),
  addCodeBtn: document.getElementById('addCodeBtn'),
  codesList: document.getElementById('codesList'),
  verifyCodeViewInput: document.getElementById('verifyCodeViewInput'),
  verifyCodeViewBtn: document.getElementById('verifyCodeViewBtn'),
  verifyCancelBtn: document.getElementById('verifyCancelBtn'),
}

function setRoute(route) {
  els.views.forEach(v => v.style.display = v.dataset.view === route ? '' : 'none')
  els.navLinks.forEach(l => l.classList.toggle('active', l.dataset.route === route))
  updateSessionActivity()
  if (route !== 'player' && els.playerVideo) { try { els.playerVideo.pause() } catch {} }
}

function pausePlayer() {
  try { if (els.playerVideo) els.playerVideo.pause() } catch {}
}

function isAdmin() { return state.user?.role === 'admin' }

function showToast(text, type = '') {
  const t = document.createElement('div')
  t.className = 'toast' + (type ? ' ' + type : '')
  t.textContent = text
  t.setAttribute('role', 'status')
  t.setAttribute('aria-live', 'polite')
  els.toastContainer.appendChild(t)
  // Limitar a 4 toasts visibles
  const toasts = els.toastContainer.querySelectorAll('.toast')
  if (toasts.length > 4) toasts[0].remove()
  setTimeout(() => t.remove(), 3500)
}

function updateSessionActivity() {
  try {
    if (state.user) {
      localStorage.setItem('niro_session_last', String(Date.now()))
    }
  } catch {}
}

function checkSessionExpiry() {
  try {
    const last = Number(localStorage.getItem('niro_session_last') || '0')
    const maxDays = Number(localStorage.getItem('niro_session_max_days') || '10')
    const ms = maxDays * 24 * 60 * 60 * 1000
    if (state.user && last && (Date.now() - last > ms)) {
      state.user = null
      applyAuthUI()
      saveLocal()
      showToast('Tu sesión expiró por inactividad')
      setRoute('home')
    }
  } catch {}
}

async function saveLocal() {
  // Fallback en localStorage y persistencia en IndexedDB
  localStorage.setItem('niro_content', JSON.stringify(state.items))
  localStorage.setItem('niro_favorites', JSON.stringify(state.favorites))
  localStorage.setItem('niro_user', JSON.stringify(state.user))
  localStorage.setItem('niro_users', JSON.stringify(state.users))
  localStorage.setItem('niro_codes', JSON.stringify(state.codes))
  localStorage.setItem('niro_pending_verify', JSON.stringify(state.pendingVerifyEmail))
  localStorage.setItem('niro_notifications', JSON.stringify(state.notifications))
  try {
    await storage.set('items', state.items)
    await storage.set('favorites', state.favorites)
    await storage.set('user', state.user)
    await storage.set('users', state.users)
    await storage.set('codes', state.codes)
    await storage.set('pendingVerify', state.pendingVerifyEmail)
    await storage.set('notifications', state.notifications)
  } catch {}
  try { syncChannel && syncChannel.postMessage({ type: 'update' }) } catch {}
  if (els.rememberCheck && els.rememberCheck.checked && els.emailInput) {
    localStorage.setItem('niro_last_email', els.emailInput.value.trim())
  }
  // Intentar persistir en servidor (mejor para múltiples dispositivos)
  saveRemote()
}

async function loadLocal() {
  // Intentar IndexedDB primero
  try {
    const items = await storage.get('items')
    const favs = await storage.get('favorites')
    const user = await storage.get('user')
    const users = await storage.get('users')
    const codes = await storage.get('codes')
    const pendingVerify = await storage.get('pendingVerify')
    const notifs = await storage.get('notifications')
    const lsItems = JSON.parse(localStorage.getItem('niro_content') || '[]')
    state.items = Array.isArray(items) ? items : lsItems
    state.favorites = Array.isArray(favs) ? favs : JSON.parse(localStorage.getItem('niro_favorites') || '[]')
    state.user = user ?? JSON.parse(localStorage.getItem('niro_user') || 'null')
    const lsUsers = JSON.parse(localStorage.getItem('niro_users') || '[]')
    state.users = Array.isArray(users) ? users : (lsUsers.length ? lsUsers : initialUsers())
    const lsCodes = JSON.parse(localStorage.getItem('niro_codes') || '[]')
    state.codes = Array.isArray(codes) ? codes : lsCodes
    state.pendingVerifyEmail = pendingVerify ?? JSON.parse(localStorage.getItem('niro_pending_verify') || 'null')
    state.notifications = Array.isArray(notifs) ? notifs : (JSON.parse(localStorage.getItem('niro_notifications') || '[]') || [])
  } catch {
    const items = JSON.parse(localStorage.getItem('niro_content') || '[]')
    const favs = JSON.parse(localStorage.getItem('niro_favorites') || '[]')
    const user = JSON.parse(localStorage.getItem('niro_user') || 'null')
    const users = JSON.parse(localStorage.getItem('niro_users') || '[]')
    const codes = JSON.parse(localStorage.getItem('niro_codes') || '[]')
    const pendingVerify = JSON.parse(localStorage.getItem('niro_pending_verify') || 'null')
    const notifs = JSON.parse(localStorage.getItem('niro_notifications') || '[]')
    state.items = items
    state.favorites = favs
    state.user = user
    state.users = users.length ? users : initialUsers()
    state.codes = Array.isArray(codes) ? codes : []
    state.pendingVerifyEmail = pendingVerify
    state.notifications = Array.isArray(notifs) ? notifs : []
  }
  const lastEmail = localStorage.getItem('niro_last_email')
  if (lastEmail && els.emailInput) els.emailInput.value = lastEmail
  // Eliminar ejemplos si existieran
  const before = state.items.length
  state.items = state.items.filter(i => !(typeof i.urlImage === 'string' && i.urlImage.includes('picsum.photos/seed/niro')))
  if (state.items.length !== before) await saveLocal()
  await hydrateBlobUrls()
}

async function loadRemote() {
  try {
    const r = await fetch(API_BASE + '/db', { cache: 'no-store' })
    if (!r.ok) throw new Error('fail')
    const data = await r.json()
    state.items = Array.isArray(data.items) ? data.items : []
    // No sobrescribir sesión del navegador ni favoritos locales
    state.users = Array.isArray(data.users) ? data.users : initialUsers()
    state.codes = Array.isArray(data.codes) ? data.codes : []
    state.notifications = Array.isArray(data.notifications) ? data.notifications : []
    await hydrateBlobUrls()
    return true
  } catch {
    return false
  }
}

async function saveRemote() {
  try {
    const payload = {
      items: state.items,
      users: state.users,
      codes: state.codes,
      notifications: state.notifications,
    }
    await fetch(API_BASE + '/db', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
  } catch {}
}

function initialData() {
  return []
}

function initialUsers() {
  return [
    { email: 'admin@niro.com', name: 'Administrador', role: 'admin', password: 'admin123', banned: false }
  ]
}

function populateFilters() {
  const genres = [...new Set(state.items.map(i => i.genre))].sort()
  els.genreSelect.innerHTML = `<option value="">Todos</option>` + genres.map(g => `<option value="${g}">${g}</option>`).join('')
}

function cardTemplate(item) {
  const fav = state.favorites.includes(item.id)
  const bestQualityLabel = (() => {
    const sources = item.sources
    if (!Array.isArray(sources) || !sources.length) return ''
    const score = (l) => {
      const m = String(l).match(/(\d{3,4})p/i)
      return m ? Number(m[1]) : (/4k|uhd/i.test(l) ? 2160 : 0)
    }
    const sorted = [...sources].sort((a,b) => score(b.label||b.quality) - score(a.label||a.quality))
    const label = sorted[0]?.label || sorted[0]?.quality || ''
    return label ? `<span class="badge-soft">${label}</span>` : ''
  })()
  return `
    <article class="card fade-in" data-id="${item.id}">
      ${item.isNew ? '<span class="badge">Nuevo</span>' : ''}
      <span class="card-type">${item.type}</span>
      ${bestQualityLabel}
      <img class="card-img" src="${item.urlImage}" alt="${item.title}" loading="lazy" onerror="this.src='${FALLBACK_IMAGE}'" />
      <div class="card-grad"></div>
      <div class="card-actions">
        <div class="action-bar">
          <button class="btn btn-primary" data-action="play" data-id="${item.id}">Reproducir</button>
          <button class="btn btn-secondary" data-action="info" data-id="${item.id}">Más info</button>
          <button class="btn btn-ghost" data-action="fav" data-id="${item.id}">${fav ? '★' : '☆'}</button>
        </div>
      </div>
      <div class="card-info">
        <h3 class="card-title">${item.title}</h3>
        <div class="card-meta">${item.year} • ${item.genre} • ${item.type}${fav ? ' • ★' : ''}</div>
      </div>
    </article>
  `
}

function renderCarousels() {
  const trend = state.items.filter(i => i.featured?.includes('trend'))
  const popular = state.items.filter(i => i.featured?.includes('popular'))
  const recommended = state.items.filter(i => i.featured?.includes('recommended'))
  els.carouselTrend.innerHTML = trend.map(cardTemplate).join('')
  els.carouselPopular.innerHTML = popular.map(cardTemplate).join('')
  els.carouselRecommended.innerHTML = recommended.map(cardTemplate).join('')
  bindCardClicks(els.carouselTrend)
  bindCardClicks(els.carouselPopular)
  bindCardClicks(els.carouselRecommended)
}

function renderHero() {
  const trend = state.items.find(i => i.featured?.includes('trend'))
  const featured = trend || state.items[0]
  if (!featured) {
    if (els.heroBg) els.heroBg.style.backgroundImage = `url('${FALLBACK_IMAGE}')`
    if (els.heroFeaturedTitle) els.heroFeaturedTitle.textContent = 'NIRO'
    if (els.heroDescShort) els.heroDescShort.textContent = 'Explora el catálogo para comenzar'
    if (els.heroChips) els.heroChips.innerHTML = ''
    if (els.heroPlayBtn) {
      els.heroPlayBtn.disabled = false
      els.heroPlayBtn.onclick = () => { showToast('No hay contenido aún. Ve al catálogo'); setRoute('catalog') }
    }
    if (els.heroInfoBtn) {
      els.heroInfoBtn.disabled = false
      els.heroInfoBtn.onclick = () => { showToast('Conoce el catálogo disponible'); setRoute('catalog') }
    }
    return
  }
  if (els.heroBg) els.heroBg.style.backgroundImage = `url('${featured.urlImage || FALLBACK_IMAGE}')`
  if (els.heroFeaturedTitle) els.heroFeaturedTitle.textContent = featured.title
  if (els.heroDescShort) {
    const d = (featured.description || '').trim()
    const t = d.length > 160 ? (d.slice(0, 157) + '…') : d
    els.heroDescShort.textContent = t
  }
  if (els.heroChips) {
    const chips = [String(featured.year || ''), featured.genre || '', featured.type || ''].filter(Boolean)
    els.heroChips.innerHTML = chips.map(c => `<span class="chip">${c}</span>`).join('')
  }
  if (els.heroPlayBtn) {
    els.heroPlayBtn.disabled = false
    els.heroPlayBtn.onclick = () => openPlayer(featured.id)
  }
  if (els.heroInfoBtn) {
    els.heroInfoBtn.disabled = false
    els.heroInfoBtn.onclick = () => renderDetails(featured.id)
  }
}

function handleHeroParallax() {
  if (!els.heroBg) return
  const onScroll = () => {
    const y = window.scrollY || 0
    els.heroBg.style.transform = `translateY(${Math.min(y * 0.08, 24)}px)`
  }
  window.addEventListener('scroll', onScroll)
}

function bindCardClicks(container) {
  container.querySelectorAll('.card').forEach(c => c.addEventListener('click', () => renderDetails(c.dataset.id)))
  container.querySelectorAll('[data-action="play"]').forEach(b => b.addEventListener('click', e => { e.stopPropagation(); openPlayer(e.currentTarget.dataset.id) }))
  container.querySelectorAll('[data-action="info"]').forEach(b => b.addEventListener('click', e => { e.stopPropagation(); renderDetails(e.currentTarget.dataset.id) }))
  container.querySelectorAll('[data-action="fav"]').forEach(b => b.addEventListener('click', e => { e.stopPropagation(); const id=e.currentTarget.dataset.id; toggleFavorite(id); renderCatalog(); renderFavorites() }))
}

function filterCatalog() {
  const t = state.filters.text.toLowerCase()
  const g = state.filters.genre
  const tp = state.filters.type
  const list = state.items.filter(i => (
    (!t || i.title.toLowerCase().includes(t)) &&
    (!g || i.genre === g) &&
    (!tp || i.type === tp)
  ))
  els.catalogGrid.innerHTML = list.map(cardTemplate).join('')
  els.emptyState.style.display = list.length ? 'none' : ''
  bindCardClicks(els.catalogGrid)
}

function renderFavorites() {
  const favs = state.items.filter(i => state.favorites.includes(i.id))
  els.favoritesSection.style.display = favs.length ? '' : 'none'
  els.favoritesCarousel.innerHTML = favs.map(cardTemplate).join('')
  bindCardClicks(els.favoritesCarousel)
}

function renderCatalog() {
  populateFilters()
  renderFavorites()
  filterCatalog()
}

function renderDetails(id) {
  const item = state.items.find(i => i.id === id)
  if (!item) return
  pausePlayer()
  const fav = state.favorites.includes(id)
  els.modalBody.innerHTML = `
    <div class="modal-body-grid">
      <div class="modal-media"><img class="modal-img" src="${item.urlImage}" alt="${item.title}" onerror="this.src='${FALLBACK_IMAGE}'" /></div>
      <div class="modal-info">
        <h3>${item.title}</h3>
        <div>${item.year} • ${item.genre} • ${item.type}</div>
        <p>${item.description}</p>
        <div class="modal-actions">
          <button class="btn btn-primary" data-action="play">Reproducir ahora</button>
          <button class="btn btn-secondary" data-action="fav">${fav ? 'Quitar de Favoritos' : 'Agregar a Favoritos'}</button>
        </div>
      </div>
    </div>
  `
  els.modal.classList.add('show')
  els.modal.setAttribute('aria-hidden', 'false')
  els.modalBody.querySelector('[data-action="play"]').addEventListener('click', () => {
    els.modal.classList.remove('show')
    els.modal.setAttribute('aria-hidden', 'true')
    openPlayer(id)
  })
  els.modalBody.querySelector('[data-action="fav"]').addEventListener('click', () => {
    toggleFavorite(id)
    renderDetails(id)
    renderFavorites()
    filterCatalog()
  })
}

function openPlayer(id) {
  if (!state.user) { showToast('Inicia sesión para reproducir'); setRoute('account'); return }
  const item = state.items.find(i => i.id === id)
  if (!item) return
  const isSerie = item.type === 'Serie' && Array.isArray(item.seasons) && item.seasons.length
  els.playerTitle.textContent = item.title
  els.playerDesc.textContent = item.description
  if (els.playerTopTitle) els.playerTopTitle.textContent = item.title
  if (els.playerVideo) {
    try { els.playerVideo.poster = item.urlImage || FALLBACK_IMAGE } catch {}
  }
  if (els.playerBackdrop) {
    try { els.playerBackdrop.style.backgroundImage = `url('${item.urlImage || FALLBACK_IMAGE}')` } catch {}
  }
  if (els.playerTopMeta) { try { els.playerTopMeta.innerHTML = ''; els.playerTopMeta.style.display = 'none' } catch {} }
  if (els.playerBadges) { try { els.playerBadges.innerHTML = ''; els.playerBadges.style.display = 'none' } catch {} }
  // Mostrar la vista del reproductor antes de configurar la fuente
  setRoute('player')
  const setVideoSource = (url) => {
    const v = els.playerVideo
    if (!v) return
    try { v.pause() } catch {}
    try { v.removeAttribute('src'); v.load() } catch {}
    if (!url) { showToast('No se encontró fuente de video'); return }
    v.src = url
    try { v.load() } catch {}
    v.onerror = () => { showToast('No se pudo cargar el video') }
    const tryPlay = () => { try { const p = v.play(); p && p.catch(() => {}) } catch {} }
    if (v.readyState >= 2) { tryPlay() }
    else {
      const once = () => { v.removeEventListener('loadedmetadata', once); tryPlay() }
      v.addEventListener('loadedmetadata', once)
      setTimeout(tryPlay, 300)
    }
  }
  const qualityScore = (s) => {
    const l = String(s.label || s.quality || '')
    const m = l.match(/(\d{3,4})p/i)
    if (m) return Number(m[1])
    if (typeof s.quality === 'number') return s.quality
    if (/uhd|4k/i.test(l)) return 2160
    if (/full\s*hd/i.test(l)) return 1080
    if (/hd/i.test(l)) return 720
    return 0
  }
  const pickBest = (sources, fallback) => {
    if (Array.isArray(sources) && sources.length) {
      const sorted = [...sources].sort((a,b) => qualityScore(b) - qualityScore(a))
      return sorted[0]?.url || fallback
    }
    return fallback
  }
  const seasonCtrl = document.getElementById('seasonControl')
  const episodeCtrl = document.getElementById('episodeControl')
  const speedSelect = document.getElementById('speedSelect')
  const cinemaBtn = document.getElementById('cinemaBtn')
  const prevEpBtn = document.getElementById('prevEpBtn')
  const nextEpBtn = document.getElementById('nextEpBtn')
  const qualitySelect = els.qualitySelect
  const labelByUrl = (sources, url) => {
    const s = (sources || []).find(x => x.url === url)
    const l = s && (s.label || s.quality)
    return l ? String(l) : ''
  }
  const showOSD = (msg) => {
    if (!els.playerOSD) return
    els.playerOSD.textContent = String(msg || '')
    els.playerOSD.style.display = ''
    els.playerOSD.classList.add('show')
    clearTimeout(state._osdTimer)
    state._osdTimer = setTimeout(() => { els.playerOSD.classList.remove('show'); els.playerOSD.style.display = 'none' }, 1800)
  }
  if (isSerie) {
    if (seasonCtrl) seasonCtrl.style.display = ''
    if (episodeCtrl) episodeCtrl.style.display = ''
    els.seasonSelect.innerHTML = item.seasons.map((s,idx) => `<option value="${idx}">${s.name || ('T'+(idx+1))}</option>`).join('')
    const loadSeason = (si) => {
      const eps = item.seasons[si]?.episodes || []
      els.episodeSelect.innerHTML = eps.map((ep,ei) => `<option value="${ei}">${ep.title || ('E'+(ei+1))}</option>`).join('')
      if (!eps.length) { showToast('No hay episodios en esta temporada'); return }
      const first = eps[0]
      // calidad automática por episodio
      const url = first?.sources ? pickBest(first.sources, first.url) : (first?.url || item.urlVideo)
      if (!url) { showToast('Este episodio no tiene fuente de video'); return }
      setVideoSource(url)
      const lab = first?.sources ? (labelByUrl(first.sources, url) || 'Automática') : ''
      if (lab) showOSD('Calidad: ' + lab)
      if (qualitySelect) {
        if (Array.isArray(first?.sources) && first.sources.length) {
          qualitySelect.style.display = ''
          qualitySelect.innerHTML = '<option value="">Automática</option>' + first.sources.map(s => `<option value="${s.url}">${s.label || s.quality || 'Fuente'}</option>`).join('')
          qualitySelect.onchange = () => {
            const val = qualitySelect.value
            setVideoSource(val || pickBest(first.sources, first.url))
            const lab2 = val ? (qualitySelect.options[qualitySelect.selectedIndex]?.text || 'Fuente') : (labelByUrl(first.sources, pickBest(first.sources, first.url)) || 'Automática')
            showOSD('Calidad: ' + lab2)
          }
        } else {
          qualitySelect.style.display = 'none'
        }
      }
    }
    loadSeason(0)
    els.seasonSelect.onchange = () => loadSeason(Number(els.seasonSelect.value))
    els.episodeSelect.onchange = () => {
      const si = Number(els.seasonSelect.value)
      const ei = Number(els.episodeSelect.value)
      const ep = item.seasons[si]?.episodes?.[ei]
      if (ep) {
        const url = ep.sources ? pickBest(ep.sources, ep.url) : ep.url
        setVideoSource(url)
        if (qualitySelect) {
          if (Array.isArray(ep.sources) && ep.sources.length) {
            qualitySelect.style.display = ''
            qualitySelect.innerHTML = '<option value="">Automática</option>' + ep.sources.map(s => `<option value="${s.url}">${s.label || s.quality || 'Fuente'}</option>`).join('')
            qualitySelect.onchange = () => {
              const val = qualitySelect.value
              setVideoSource(val || pickBest(ep.sources, ep.url))
            }
          } else {
            qualitySelect.style.display = 'none'
          }
        }
      }
    }
    if (prevEpBtn && nextEpBtn) {
      prevEpBtn.style.display = ''
      nextEpBtn.style.display = ''
      prevEpBtn.onclick = () => {
        let si = Number(els.seasonSelect.value)
        let ei = Number(els.episodeSelect.value) - 1
        if (ei < 0) {
          si = Math.max(0, si - 1)
          els.seasonSelect.value = String(si)
          const eps = item.seasons[si]?.episodes || []
          ei = Math.max(0, eps.length - 1)
          els.episodeSelect.innerHTML = eps.map((ep,ei2) => `<option value="${ei2}">${ep.title || ('E'+(ei2+1))}</option>`).join('')
        }
        els.episodeSelect.value = String(Math.max(0, ei))
        const ep = item.seasons[si]?.episodes?.[Math.max(0, ei)]
        if (ep?.url) setVideoSource(ep.url)
      }
      nextEpBtn.onclick = () => {
        let si = Number(els.seasonSelect.value)
        let ei = Number(els.episodeSelect.value) + 1
        const epsCur = item.seasons[si]?.episodes || []
        if (ei >= epsCur.length) {
          si = Math.min(item.seasons.length - 1, si + 1)
          els.seasonSelect.value = String(si)
          const eps = item.seasons[si]?.episodes || []
          els.episodeSelect.innerHTML = eps.map((ep,ei2) => `<option value="${ei2}">${ep.title || ('E'+(ei2+1))}</option>`).join('')
          ei = 0
        }
        els.episodeSelect.value = String(ei)
        const ep = item.seasons[si]?.episodes?.[ei]
        if (ep?.url) setVideoSource(ep.url)
      }
    }
    if (els.playerBadges) { els.playerBadges.innerHTML = ''; els.playerBadges.style.display = 'none' }
  } else {
    if (seasonCtrl) seasonCtrl.style.display = 'none'
    if (episodeCtrl) episodeCtrl.style.display = 'none'
    const urlBest = item.sources ? pickBest(item.sources, item.urlVideo) : item.urlVideo
    if (!urlBest) { showToast('Este contenido no tiene fuente de video'); return }
    setVideoSource(urlBest)
    const lab = item.sources ? (labelByUrl(item.sources, urlBest) || 'Automática') : ''
    if (lab) showOSD('Calidad: ' + lab)
    if (qualitySelect) {
      if (Array.isArray(item.sources) && item.sources.length) {
        qualitySelect.style.display = ''
        qualitySelect.innerHTML = '<option value="">Automática</option>' + item.sources.map(s => `<option value="${s.url}">${s.label || s.quality || 'Fuente'}</option>`).join('')
        qualitySelect.onchange = () => {
          const val = qualitySelect.value
          setVideoSource(val || pickBest(item.sources, item.urlVideo))
        }
      } else {
        qualitySelect.style.display = 'none'
      }
    }
    if (els.playerBadges) { els.playerBadges.innerHTML = ''; els.playerBadges.style.display = 'none' }
    if (els.playerTopMeta) { els.playerTopMeta.innerHTML = ''; els.playerTopMeta.style.display = 'none' }
  }
  if (els.playerVideo) { try { els.playerVideo.controls = true } catch {} }
  if (speedSelect) {
    const saved = localStorage.getItem('niro_playback_rate')
    speedSelect.value = saved || '1'
    try { els.playerVideo.playbackRate = Number(speedSelect.value) } catch {}
    speedSelect.onchange = () => { try { const r=Number(speedSelect.value); els.playerVideo.playbackRate = r; localStorage.setItem('niro_playback_rate', String(r)); showOSD('Velocidad: ' + speedSelect.value + 'x') } catch {} }
  }
  if (cinemaBtn) {
    cinemaBtn.textContent = 'Modo inmersivo'
    cinemaBtn.onclick = () => {
      const on = document.body.classList.toggle('cinema')
      cinemaBtn.textContent = on ? 'Salir de modo inmersivo' : 'Modo inmersivo'
      showOSD(on ? 'Modo inmersivo' : 'Modo estándar')
    }
  }
  // Atajos de teclado en reproductor
  const keyHandler = (e) => {
    const playerVisible = document.querySelector('.view-player')?.style.display !== 'none'
    if (!playerVisible) return
    const v = els.playerVideo
    if (!v) return
    if (e.key === ' ' || e.code === 'Space') { e.preventDefault(); if (v.paused) v.play(); else v.pause() }
    else if (e.key.toLowerCase() === 'f') { cinemaBtn?.click() }
    else if (e.key === 'ArrowRight') { v.currentTime = Math.min((v.currentTime||0)+5, v.duration||1e9) }
    else if (e.key === 'ArrowLeft') { v.currentTime = Math.max((v.currentTime||0)-5, 0) }
    else if (e.key.toLowerCase() === 'm') { v.muted = !v.muted; showOSD(v.muted ? 'Silencio' : 'Sonido') }
  }
  window.addEventListener('keydown', keyHandler)
  const fmt = (s) => {
    s = Math.floor(Number(s||0))
    const m = Math.floor(s/60), h = Math.floor(m/60)
    const mm = String(m % 60).padStart(2,'0'), ss = String(s % 60).padStart(2,'0')
    return h > 0 ? `${h}:${mm}:${ss}` : `${mm}:${ss}`
  }
  const updateTimeUI = () => {
    if (!els.uiTime || !els.playerVideo) return
    els.uiTime.textContent = `${fmt(els.playerVideo.currentTime||0)} / ${fmt(els.playerVideo.duration||0)}`
  }
  const updateProgressUI = () => {
    const v = els.playerVideo; if (!v || !els.uiFill) return
    const p = (v.currentTime||0) / Math.max(1,(v.duration||1))
    els.uiFill.style.width = `${Math.max(0, Math.min(1, p)) * 100}%`
  }
  const updateBufferUI = () => {
    const v = els.playerVideo; if (!v || !els.uiBuffer) return
    try {
      if (v.buffered && v.buffered.length) {
        const end = v.buffered.end(v.buffered.length-1)
        const p = end / Math.max(1,(v.duration||1))
        els.uiBuffer.style.width = `${Math.max(0, Math.min(1, p)) * 100}%`
      }
    } catch {}
  }
  if (els.uiPlay && els.playerVideo) {
    const v = els.playerVideo
    const syncPlayBtn = () => { els.uiPlay.classList.toggle('playing', !v.paused) }
    els.uiPlay.onclick = () => { try { if (v.paused) v.play(); else v.pause() } catch {} }
    v.addEventListener('play', syncPlayBtn)
    v.addEventListener('pause', syncPlayBtn)
    syncPlayBtn()
  }
  if (els.uiMute && els.playerVideo) {
    els.uiMute.onclick = () => { els.playerVideo.muted = !els.playerVideo.muted }
    const syncMute = () => { document.body.classList.toggle('muted', !!els.playerVideo.muted) }
    els.playerVideo.addEventListener('volumechange', syncMute)
    syncMute()
  }
  if (els.uiVolume && els.playerVideo) {
    els.uiVolume.value = String(els.playerVideo.volume || 1)
    els.uiVolume.oninput = () => { try { els.playerVideo.volume = Number(els.uiVolume.value) } catch {} }
  }
  if (els.uiFullscreen) {
    els.uiFullscreen.onclick = () => {
      const frame = document.querySelector('.player-frame')
      const isFull = document.fullscreenElement
      try {
        if (!isFull) frame?.requestFullscreen?.(); else document.exitFullscreen?.()
      } catch {}
    }
  }
  if (els.uiProgress && els.playerVideo) {
    const v = els.playerVideo
    const seekTo = (clientX) => {
      const r = els.uiProgress.getBoundingClientRect()
      const dx = Math.max(0, Math.min(r.width, clientX - r.left))
      const p = dx / Math.max(1, r.width)
      v.currentTime = p * (v.duration||0)
    }
    els.uiProgress.addEventListener('click', (e) => seekTo(e.clientX))
    let dragging = false
    els.uiProgress.addEventListener('mousedown', (e) => { dragging = true; seekTo(e.clientX) })
    window.addEventListener('mousemove', (e) => { if (dragging) seekTo(e.clientX) })
    window.addEventListener('mouseup', () => { dragging = false })
  }
  if (els.playerVideo) {
    els.playerVideo.addEventListener('timeupdate', () => { updateTimeUI(); updateProgressUI() })
    els.playerVideo.addEventListener('progress', updateBufferUI)
    updateTimeUI(); updateProgressUI(); updateBufferUI()
  }
  if (els.playerUI) {
    let hideT
    const showUI = () => { els.playerUI.classList.remove('hidden'); document.body.style.cursor = 'default'; clearTimeout(hideT); hideT = setTimeout(() => { if (!els.playerVideo?.paused) { els.playerUI.classList.add('hidden'); document.body.style.cursor = 'none' } }, 1800) }
    showUI()
    document.querySelector('.player-frame')?.addEventListener('mousemove', showUI)
  }
  try {
    const prog = state.progress?.[id]
    if (typeof prog === 'number') { els.playerVideo.currentTime = prog }
    els.playerVideo.addEventListener('timeupdate', () => {
      const t = els.playerVideo.currentTime || 0
      state.progress = state.progress || {}
      state.progress[id] = Math.floor(t)
      saveLocal()
    }, { once: false })
    els.playerVideo.addEventListener('play', () => showOSD('Reproduciendo'))
    els.playerVideo.addEventListener('pause', () => showOSD('Pausa'))
    els.playerVideo.addEventListener('volumechange', () => showOSD(els.playerVideo.muted ? 'Silencio' : 'Sonido'))
  } catch {}
}

function toggleFavorite(id) {
  const i = state.favorites.indexOf(id)
  if (i >= 0) {
    state.favorites.splice(i,1)
    showToast('Eliminado de Favoritos')
  } else {
    state.favorites.push(id)
    showToast('Guardado en Favoritos')
  }
  saveLocal()
}

async function addItem(data) {
  if (!isAdmin()) { showToast('No autorizado'); return }
  const id = 'n' + Math.random().toString(36).slice(2,8)
  const item = { id, title: data.title, description: data.description, year: Number(data.year), genre: data.genre, type: data.type, urlImage: data.urlImage, urlVideo: data.urlVideo, featured: [], isNew: true }
  const uploadFile = async (kind, file) => {
    try {
      const fd = new FormData(); fd.append('file', file)
      const r = await fetch(API_BASE + '/upload/' + kind, { method: 'POST', body: fd })
      if (!r.ok) throw new Error('upload failed')
      const j = await r.json(); return API_BASE + j.url
    } catch { return null }
  }
  if (data.imageFile instanceof Blob) {
    const url = await uploadFile('image', data.imageFile)
    if (url) item.urlImage = url
    else {
      item.imageBlobKey = `media:img:${id}`
      await storage.set(item.imageBlobKey, data.imageFile)
      const blob = await storage.get(item.imageBlobKey)
      if (blob) item.urlImage = URL.createObjectURL(blob)
    }
  }
  if (data.videoFile instanceof Blob) {
    const url = await uploadFile('video', data.videoFile)
    if (url) item.urlVideo = url
    else {
      item.videoBlobKey = `media:video:${id}`
      await storage.set(item.videoBlobKey, data.videoFile)
      const blob = await storage.get(item.videoBlobKey)
      if (blob) item.urlVideo = URL.createObjectURL(blob)
    }
  }
  if (data.type === 'Serie' && Array.isArray(data.seasons)) {
    item.seasons = []
    for (let si = 0; si < data.seasons.length; si++) {
      const s = data.seasons[si]
      const season = { name: s.name || `T${si+1}`, episodes: [] }
      for (let ei = 0; ei < (s.episodes || []).length; ei++) {
        const ep = s.episodes[ei]
        const epi = { title: ep.title || `E${ei+1}` }
        if (ep.file instanceof Blob) {
          const url = await uploadFile('video', ep.file)
          if (url) epi.url = url
          else {
            epi.videoBlobKey = `series:${id}:s${si}:e${ei}`
            await storage.set(epi.videoBlobKey, ep.file)
            const blob = await storage.get(epi.videoBlobKey)
            if (blob) epi.url = URL.createObjectURL(blob)
          }
        }
        season.episodes.push(epi)
      }
      item.seasons.push(season)
    }
  }
  state.items.unshift(item)
  saveLocal()
  showToast('Contenido agregado')
  pushNotification('Estreno', `${item.type}: ${item.title}`, item.id)
  renderHero()
  return id
}

async function updateItem(id, data) {
  if (!isAdmin()) { showToast('No autorizado'); return }
  const idx = state.items.findIndex(i => i.id === id)
  if (idx < 0) return
  const base = { ...state.items[idx], ...data, year: Number(data.year) }
  const uploadFile = async (kind, file) => {
    try {
      const fd = new FormData(); fd.append('file', file)
      const r = await fetch(API_BASE + '/upload/' + kind, { method: 'POST', body: fd })
      if (!r.ok) throw new Error('upload failed')
      const j = await r.json(); return API_BASE + j.url
    } catch { return null }
  }
  if (data.imageFile instanceof Blob) {
    const url = await uploadFile('image', data.imageFile)
    if (url) base.urlImage = url
    else {
      base.imageBlobKey = `media:img:${id}`
      await storage.set(base.imageBlobKey, data.imageFile)
      const blob = await storage.get(base.imageBlobKey)
      if (blob) base.urlImage = URL.createObjectURL(blob)
    }
  }
  if (data.videoFile instanceof Blob) {
    const url = await uploadFile('video', data.videoFile)
    if (url) base.urlVideo = url
    else {
      base.videoBlobKey = `media:video:${id}`
      await storage.set(base.videoBlobKey, data.videoFile)
      const blob = await storage.get(base.videoBlobKey)
      if (blob) base.urlVideo = URL.createObjectURL(blob)
    }
  }
  if (data.type === 'Serie' && Array.isArray(data.seasons)) {
    base.seasons = []
    for (let si = 0; si < data.seasons.length; si++) {
      const s = data.seasons[si]
      const season = { name: s.name || `T${si+1}`, episodes: [] }
      for (let ei = 0; ei < (s.episodes || []).length; ei++) {
        const ep = s.episodes[ei]
        const epi = { title: ep.title || `E${ei+1}` }
        if (ep.file instanceof Blob) {
          const url = await uploadFile('video', ep.file)
          if (url) epi.url = url
          else {
            epi.videoBlobKey = `series:${id}:s${si}:e${ei}`
            await storage.set(epi.videoBlobKey, ep.file)
            const blob = await storage.get(epi.videoBlobKey)
            if (blob) epi.url = URL.createObjectURL(blob)
          }
        } else if (ep.videoBlobKey) {
          epi.videoBlobKey = ep.videoBlobKey
          const blob = await storage.get(ep.videoBlobKey)
          if (blob) epi.url = URL.createObjectURL(blob)
        } else if (ep.url) {
          epi.url = ep.url
        }
        season.episodes.push(epi)
      }
      base.seasons.push(season)
    }
  }
  state.items[idx] = base
  saveLocal()
  showToast('Contenido actualizado')
  renderHero()
}

async function deleteItem(id) {
  if (!isAdmin()) { showToast('No autorizado'); return }
  const it = state.items.find(i => i.id === id)
  state.items = state.items.filter(i => i.id !== id)
  state.favorites = state.favorites.filter(f => f !== id)
  const deleteRemote = async (url) => {
    try {
      if (!url) return
      const resp = await fetch(API_BASE + '/delete', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url }) })
      if (!resp.ok) {
        await fetch(API_BASE + '/delete?url=' + encodeURIComponent(url), { method: 'GET', cache: 'no-store' })
      }
    } catch {}
  }
  try {
    if (it?.imageBlobKey) await storage.del(it.imageBlobKey)
    if (it?.videoBlobKey) await storage.del(it.videoBlobKey)
    if (it?.urlImage && it.urlImage.startsWith(API_BASE)) await deleteRemote(it.urlImage)
    if (it?.urlVideo && it.urlVideo.startsWith(API_BASE)) await deleteRemote(it.urlVideo)
    if (it?.type === 'Serie' && Array.isArray(it.seasons)) {
      for (let si = 0; si < it.seasons.length; si++) {
        const s = it.seasons[si]
        for (let ei = 0; ei < (s.episodes || []).length; ei++) {
          const ep = s.episodes[ei]
          if (ep.videoBlobKey) await storage.del(ep.videoBlobKey)
          if (ep.url && ep.url.startsWith(API_BASE)) await deleteRemote(ep.url)
        }
      }
    }
  } catch {}
  saveLocal()
  saveRemote()
  renderCatalog()
  renderAdminList()
  renderHero()
  renderAdminStats()
  showToast('Contenido eliminado')
}

function renderAdminList() {
  els.adminList.innerHTML = state.items.map(i => `
    <article class="card" data-id="${i.id}">
      <img class="card-img" src="${i.urlImage}" alt="${i.title}" onerror="this.src='${FALLBACK_IMAGE}'" />
      <div class="card-grad"></div>
      <div class="card-info">
        <h3 class="card-title">${i.title}</h3>
        <div class="card-meta">${i.type}</div>
      </div>
      <div style="position:absolute;top:10px;right:10px;display:flex;gap:8px">
        <button class="btn btn-secondary" data-action="edit">Editar</button>
        <button class="btn btn-ghost" data-action="del">Eliminar</button>
      </div>
    </article>
  `).join('')
  els.adminList.querySelectorAll('[data-action="edit"]').forEach(b => {
    b.addEventListener('click', e => {
      const id = e.currentTarget.closest('.card').dataset.id
      const it = state.items.find(x => x.id === id)
      state.editingId = id
      els.itemId.value = id
      els.titleInput.value = it.title
      els.yearInput.value = it.year
      els.genreInput.value = it.genre
      els.typeInput.value = it.type
      els.descInput.value = it.description
      if (els.imageFileInput) els.imageFileInput.value = ''
      if (els.videoFileInput) els.videoFileInput.value = ''
      adminTemp.seasons = Array.isArray(it.seasons) ? it.seasons.map(s => ({ name: s.name, episodes: (s.episodes || []).map(ep => ({ title: ep.title, videoBlobKey: ep.videoBlobKey, url: ep.url })) })) : []
      renderSeasonsAdmin()
      const grp = document.getElementById('seriesGroup')
      if (grp) grp.style.display = it.type === 'Serie' ? '' : 'none'
      if (els.adminFormContainer) els.adminFormContainer.style.display = ''
      if (els.adminContentContainer) els.adminContentContainer.style.display = 'none'
      if (els.adminUsersContainer) els.adminUsersContainer.style.display = 'none'
      if (els.seriesSteps) {
        if (it.type === 'Serie') {
          els.seriesSteps.style.display = ''
          els.seriesSteps.querySelectorAll('[data-step]').forEach(b2 => b2.classList.toggle('active', b2.dataset.step === 'cover'))
          els.seriesSteps.querySelectorAll('[data-step="seasons"], [data-step="episodes"]').forEach(b2 => b2.disabled = false)
        } else {
          els.seriesSteps.style.display = 'none'
        }
      }
      showToast('Editando contenido')
    })
  })
  els.adminList.querySelectorAll('[data-action="del"]').forEach(b => b.addEventListener('click', e => deleteItem(e.currentTarget.closest('.card').dataset.id)))
}

function renderUsersList() {
  els.usersList.innerHTML = state.users.map(u => `
    <article class="card" data-email="${u.email}">
      <div class="card-grad"></div>
      <div class="card-info">
        <h3 class="card-title">${u.name} (${u.role})</h3>
        <div class="card-meta">${u.email}${u.banned ? ' • BANEADO' : ''}${u.verified ? ' • VERIFICADO' : ' • SIN VERIFICAR'}${u.accessCode ? ' • CODE: '+u.accessCode : ''}</div>
      </div>
      <div style="position:absolute;top:10px;right:10px;display:flex;gap:8px">
        ${u.role !== 'admin' ? `<button class="btn btn-secondary" data-action="ban">${u.banned ? 'Desbanear' : 'Banear'}</button>` : ''}
        ${u.role !== 'admin' ? '<button class="btn btn-ghost" data-action="del">Eliminar</button>' : ''}
      </div>
    </article>
  `).join('')
  els.usersList.querySelectorAll('[data-action="ban"]').forEach(b => b.addEventListener('click', e => toggleBanUser(e.currentTarget.closest('.card').dataset.email)))
  els.usersList.querySelectorAll('[data-action="del"]').forEach(b => b.addEventListener('click', e => deleteUser(e.currentTarget.closest('.card').dataset.email)))
}

function renderCodesList() {
  if (!els.codesList) return
  els.codesList.innerHTML = state.codes.map(c => `<span class="chip">${c}<button class="chip-del" data-code="${c}">×</button></span>`).join('')
  els.codesList.querySelectorAll('.chip-del').forEach(b => b.addEventListener('click', e => {
    const code = e.currentTarget.dataset.code
    state.codes = state.codes.filter(x => x !== code)
    saveLocal()
    renderCodesList()
  }))
}

function renderAdminStats() {
  if (!els.adminStats) return
  const total = state.items.length
  const movies = state.items.filter(i => i.type === 'Película').length
  const series = state.items.filter(i => i.type === 'Serie').length
  const users = state.users.length
  els.adminStats.innerHTML = `
    <div class="stat-card"><div class="stat-title">Total</div><div class="stat-value">${total}</div></div>
    <div class="stat-card"><div class="stat-title">Películas</div><div class="stat-value">${movies}</div></div>
    <div class="stat-card"><div class="stat-title">Series</div><div class="stat-value">${series}</div></div>
    <div class="stat-card"><div class="stat-title">Usuarios</div><div class="stat-value">${users}</div></div>
  `
}

function addUser(data) {
  if (!isAdmin()) { showToast('No autorizado'); return }
  const exists = state.users.some(u => u.email === data.email)
  if (exists) { showToast('El usuario ya existe'); return }
  state.users.push({ email: data.email, name: data.name, password: data.password, role: 'user', banned: false, verified: false, accessCode: data.accessCode || '' })
  if (data.accessCode && !state.codes.includes(data.accessCode)) {
    state.codes.push(data.accessCode)
  }
  saveLocal()
  renderUsersList()
  renderAdminStats()
  showToast('Usuario agregado')
}

function deleteUser(email) {
  if (!isAdmin()) { showToast('No autorizado'); return }
  state.users = state.users.filter(u => u.email !== email)
  saveLocal()
  renderUsersList()
  renderAdminStats()
  showToast('Usuario eliminado')
}

function toggleBanUser(email) {
  if (!isAdmin()) { showToast('No autorizado'); return }
  const u = state.users.find(x => x.email === email)
  if (!u) return
  u.banned = !u.banned
  saveLocal()
  renderUsersList()
  renderAdminStats()
  showToast(u.banned ? 'Usuario baneado' : 'Usuario desbaneado')
}

function handleAdminForm() {
  els.adminForm.addEventListener('submit', async e => {
    e.preventDefault()
    const data = {
      title: els.titleInput.value.trim(),
      description: els.descInput.value.trim(),
      year: els.yearInput.value,
      genre: els.genreInput.value.trim(),
      type: els.typeInput.value,
      imageFile: els.imageFileInput.files && els.imageFileInput.files[0],
      videoFile: els.videoFileInput.files && els.videoFileInput.files[0],
      seasons: (adminTemp.seasons && adminTemp.seasons.length) ? adminTemp.seasons : undefined
    }
    const editing = !!state.editingId
    if (!data.title || !data.description || !data.year || !data.genre || !data.type) { showToast('Completa todos los campos'); return }
    if (!editing) {
      if (!data.imageFile) { showToast('Sube una imagen'); return }
      if (data.type === 'Película' && !data.videoFile) { showToast('Sube el video de la película'); return }
    }
    if (state.editingId) {
      await updateItem(state.editingId, data)
    } else {
      const newId = await addItem(data)
      if (data.type === 'Serie') {
        state.editingId = newId
        showToast('Serie creada: agrega temporadas y episodios')
      }
    }
    state.editingId = null
    els.itemId.value = ''
    if (data.type === 'Película') {
      els.adminForm.reset()
      adminTemp.seasons = []
      renderSeasonsAdmin()
    }
    renderAdminList()
    renderCatalog()
  })
  document.getElementById('resetFormBtn').addEventListener('click', () => {
    state.editingId = null
    els.itemId.value = ''
    els.adminForm.reset()
    adminTemp.seasons = []
    renderSeasonsAdmin()
  })
}

const adminTemp = { seasons: [] }

function renderSeasonsAdmin() {
  if (!els.seasonList) return
  els.seasonList.innerHTML = adminTemp.seasons.map((s,si) => `
    <div class="season" data-si="${si}" style="border:1px solid #232337;padding:10px;border-radius:10px;margin-top:10px">
      <div style="display:flex;align-items:center;justify-content:space-between">
        <strong>${s.name || 'Temporada ' + (si+1)}</strong>
        <button type="button" class="btn btn-ghost del-season" data-si="${si}">Eliminar temporada</button>
      </div>
      <div class="form-row" style="margin-top:8px">
        <input class="input episodeTitleInput" placeholder="Título del episodio" />
        <input class="input episodeFileInput" type="file" accept="video/*" />
      </div>
      <div class="form-actions" style="margin-top:8px">
        <button type="button" class="btn btn-secondary add-episode" data-si="${si}">Agregar episodio</button>
      </div>
      <div class="chip-list episode-list">${(s.episodes||[]).map((ep,ei)=>`<span class="chip">${ep.title||('E'+(ei+1))}<button class="chip-del" data-si="${si}" data-ei="${ei}">×</button></span>`).join('')}</div>
    </div>
  `).join('')
  els.seasonList.querySelectorAll('.add-episode').forEach(btn => {
    btn.addEventListener('click', e => {
      const si = Number(e.currentTarget.dataset.si)
      const sc = e.currentTarget.closest('.season')
      const titleEl = sc.querySelector('.episodeTitleInput')
      const fileEl = sc.querySelector('.episodeFileInput')
      const title = titleEl.value.trim()
      const file = fileEl.files && fileEl.files[0]
      if (!title || !file) { showToast('Completa título y archivo'); return }
      adminTemp.seasons[si].episodes = adminTemp.seasons[si].episodes || []
      adminTemp.seasons[si].episodes.push({ title, file })
      titleEl.value = ''
      fileEl.value = ''
      renderSeasonsAdmin()
    })
  })
  els.seasonList.querySelectorAll('.chip-del').forEach(btn => {
    btn.addEventListener('click', e => {
      const si = Number(e.currentTarget.dataset.si)
      const ei = Number(e.currentTarget.dataset.ei)
      adminTemp.seasons[si].episodes.splice(ei,1)
      renderSeasonsAdmin()
    })
  })
  els.seasonList.querySelectorAll('.del-season').forEach(btn => {
    btn.addEventListener('click', e => {
      const si = Number(e.currentTarget.dataset.si)
      adminTemp.seasons.splice(si,1)
      renderSeasonsAdmin()
    })
  })
}

function handleSeriesAdmin() {
  if (els.typeInput) {
    const toggle = () => {
      const isSerie = els.typeInput.value === 'Serie'
      const grp = document.getElementById('seriesGroup')
      if (grp) grp.style.display = isSerie ? '' : 'none'
      if (els.seriesSteps) els.seriesSteps.style.display = isSerie ? '' : 'none'
      if (els.seriesEpisodesGroup) els.seriesEpisodesGroup.style.display = isSerie ? 'none' : 'none'
      if (els.seriesSteps) {
        const canSteps = !!state.editingId && isSerie
        els.seriesSteps.querySelectorAll('[data-step="seasons"], [data-step="episodes"]').forEach(b => b.disabled = !canSteps)
      }
    }
    els.typeInput.addEventListener('change', toggle)
    toggle()
  }
  if (els.addSeasonBtn) {
    els.addSeasonBtn.addEventListener('click', () => {
      const name = (els.seasonNameInput?.value || '').trim()
      adminTemp.seasons.push({ name, episodes: [] })
      if (els.seasonNameInput) els.seasonNameInput.value = ''
      renderSeasonsAdmin()
    })
  }
  if (els.seriesSteps) {
    els.seriesSteps.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        els.seriesSteps.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'))
        btn.classList.add('active')
        const step = btn.dataset.step
        const showCover = step === 'cover'
        const showSeasons = step === 'seasons'
        const showEpisodes = step === 'episodes'
        document.getElementById('seriesGroup').style.display = showSeasons ? '' : 'none'
        els.seriesEpisodesGroup.style.display = showEpisodes ? '' : 'none'
      })
    })
  }
  if (els.addEpisodeBtn) {
    els.addEpisodeBtn.addEventListener('click', () => {
      const si = Number(els.seasonPickSelect.value || 0)
      const title = (els.episodeTitleInput.value || '').trim()
      const file = els.episodeFileInput.files && els.episodeFileInput.files[0]
      if (!adminTemp.seasons[si]) { showToast('Primero crea la temporada'); return }
      if (!title || !file) { showToast('Completa título y archivo'); return }
      adminTemp.seasons[si].episodes = adminTemp.seasons[si].episodes || []
      adminTemp.seasons[si].episodes.push({ title, file })
      els.episodeTitleInput.value = ''
      els.episodeFileInput.value = ''
      renderEpisodesAdmin()
    })
  }
  function renderEpisodesAdmin() {
    els.seasonPickSelect.innerHTML = adminTemp.seasons.map((s,si)=>`<option value="${si}">${s.name || ('T'+(si+1))}</option>`).join('')
    const si = Number(els.seasonPickSelect.value || 0)
    const eps = (adminTemp.seasons[si]?.episodes)||[]
    els.episodeAdminList.innerHTML = eps.map((ep,ei)=>`<span class="chip">${ep.title}<button class="chip-del" data-si="${si}" data-ei="${ei}">×</button></span>`).join('')
    els.episodeAdminList.querySelectorAll('.chip-del').forEach(b => b.addEventListener('click', e => {
      const si2 = Number(e.currentTarget.dataset.si)
      const ei2 = Number(e.currentTarget.dataset.ei)
      adminTemp.seasons[si2].episodes.splice(ei2,1)
      renderEpisodesAdmin()
    }))
  }
}

function handleUserForm() {
  if (!els.userForm) return
  els.userForm.addEventListener('submit', e => {
    e.preventDefault()
    const data = {
      email: els.userEmailInput.value.trim(),
      name: els.userNameInput.value.trim(),
      password: els.userPasswordInput.value.trim(),
      accessCode: (els.userAccessCodeInput && els.userAccessCodeInput.value || '').trim()
    }
    if (!data.email || !data.name || !data.password) { showToast('Completa todos los campos'); return }
    addUser(data)
    els.userForm.reset()
  })
}

function handleSupportForm() {
  if (!els.supportForm) return
  els.supportForm.addEventListener('submit', e => {
    e.preventDefault()
    const email = els.supportEmailInput.value.trim()
    const subject = els.supportSubjectInput.value.trim()
    const message = els.supportMessageInput.value.trim()
    if (!email || !subject || !message) { showToast('Completa todos los campos'); return }
    showToast('Solicitud enviada')
    els.supportForm.reset()
  })
}

function handleVerifyView() {
  if (!els.verifyCodeViewBtn || !els.verifyCodeViewInput) return
  els.verifyCodeViewBtn.addEventListener('click', () => {
    const code = (els.verifyCodeViewInput.value || '').trim()
    const email = state.pendingVerifyEmail
    const ok = state.codes && state.codes.includes(code)
    if (!ok) { const err = document.getElementById('verifyCodeError'); if (err) { err.textContent = 'Código inválido'; err.style.display = '' } return }
    const u = state.users.find(x => x.email === email)
    if (!u) { showToast('Usuario no encontrado'); return }
    state.codes = state.codes.filter(c => c !== code)
    u.verified = true
    state.pendingVerifyEmail = null
    saveLocal()
    applyAuthUI()
    state.user = { email: u.email, role: u.role }
    showToast('Código verificado')
    setRoute('home')
  })
  if (els.verifyCancelBtn) {
    els.verifyCancelBtn.addEventListener('click', () => {
      state.pendingVerifyEmail = null
      saveLocal()
      setRoute('account')
    })
  }
}

function handleAdminMenu() {
  if (!els.adminMenuBtn || !els.adminDrawer) return
  els.adminMenuBtn.addEventListener('click', () => {
    const open = els.adminDrawer.classList.toggle('open')
    if (open) {
      els.adminDrawer.style.display = ''
    } else {
      els.adminDrawer.style.display = ''
    }
  })
  els.adminDrawer.querySelectorAll('.drawer-item').forEach(btn => {
    btn.addEventListener('click', () => {
      const a = btn.dataset.adminAction
      if (els.adminFormContainer) els.adminFormContainer.style.display = 'none'
      if (els.adminContentContainer) els.adminContentContainer.style.display = 'none'
      if (els.adminUsersContainer) els.adminUsersContainer.style.display = 'none'
      if (a === 'add-movie') {
        if (els.adminFormContainer) els.adminFormContainer.style.display = ''
        state.editingId = null
        if (els.adminForm) els.adminForm.reset()
        adminTemp.seasons = []
        renderSeasonsAdmin()
        if (els.typeInput) els.typeInput.value = 'Película'
        const grp = document.getElementById('seriesGroup')
        if (grp) grp.style.display = 'none'
        if (els.seriesSteps) els.seriesSteps.style.display = 'none'
      } else if (a === 'add-series') {
        if (els.adminFormContainer) els.adminFormContainer.style.display = ''
        state.editingId = null
        if (els.adminForm) els.adminForm.reset()
        adminTemp.seasons = []
        renderSeasonsAdmin()
        if (els.typeInput) els.typeInput.value = 'Serie'
        if (els.seriesSteps) {
          els.seriesSteps.style.display = ''
          els.seriesSteps.querySelectorAll('[data-step]')
            .forEach(b => b.classList.toggle('active', b.dataset.step === 'cover'))
          els.seriesSteps.querySelectorAll('[data-step="seasons"], [data-step="episodes"]')
            .forEach(b => b.disabled = true)
        }
        const grp = document.getElementById('seriesGroup')
        if (grp) grp.style.display = 'none'
        if (els.seriesEpisodesGroup) els.seriesEpisodesGroup.style.display = 'none'
      } else if (a === 'list-content') {
        if (els.adminContentContainer) els.adminContentContainer.style.display = ''
        renderAdminList()
      } else if (a === 'manage-users') {
        if (els.adminUsersContainer) els.adminUsersContainer.style.display = ''
        renderUsersList()
      }
      els.adminDrawer.classList.remove('open')
    })
  })
}

function handleLogin() {
  els.loginForm.addEventListener('submit', e => {
    e.preventDefault()
    const submitBtn = els.loginForm.querySelector('button[type="submit"]')
    if (submitBtn) { submitBtn.classList.add('loading'); submitBtn.disabled = true }
    const card = document.querySelector('.login-card')
    if (card) card.classList.add('loading')
    const email = els.emailInput.value.trim()
    const pass = els.passwordInput.value.trim()
    els.loginError.style.display = 'none'
    els.emailError.style.display = 'none'
    els.passwordError.style.display = 'none'
    els.emailInput.classList.remove('invalid')
    els.passwordInput.classList.remove('invalid')
    const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
    if (!emailValid) { els.emailError.textContent = 'Ingresa un email válido'; els.emailError.style.display = ''; els.emailInput.classList.add('invalid'); if (submitBtn) { submitBtn.classList.remove('loading'); submitBtn.disabled = false } if (card) card.classList.remove('loading'); return }
    if (!pass) { els.passwordError.textContent = 'Ingresa tu contraseña'; els.passwordError.style.display = ''; els.passwordInput.classList.add('invalid'); if (submitBtn) { submitBtn.classList.remove('loading'); submitBtn.disabled = false } if (card) card.classList.remove('loading'); return }
    if (email === 'admin@niro.com' && pass === 'admin123') {
      state.user = { email, role: 'admin' }
      els.accountStatus.textContent = 'Sesión iniciada como administrador'
      els.logoutBtn.style.display = ''
      if (els.navLogout) els.navLogout.style.display = ''
      showToast('Bienvenido Admin')
      localStorage.setItem('niro_session_last', String(Date.now()))
      if (!localStorage.getItem('niro_session_max_days')) localStorage.setItem('niro_session_max_days', '10')
      els.navAdmin.style.display = ''
      if (els.accountNavLink) els.accountNavLink.style.display = 'none'
      if (els.navLogout) els.navLogout.style.display = ''
      saveLocal()
      setRoute('admin')
      renderAdminList()
      renderUsersList()
      if (submitBtn) { submitBtn.classList.remove('loading'); submitBtn.disabled = false }
      if (card) card.classList.remove('loading')
    } else {
      const u = state.users.find(x => x.email === email && x.password === pass)
      if (!u) {
        els.loginError.textContent = 'Credenciales inválidas'
        els.loginError.style.display = ''
        if (submitBtn) { submitBtn.classList.remove('loading'); submitBtn.disabled = false }
        if (card) card.classList.remove('loading')
        return
      }
      if (u.banned) {
        els.loginError.textContent = 'Tu cuenta está baneada'
        els.loginError.style.display = ''
        if (submitBtn) { submitBtn.classList.remove('loading'); submitBtn.disabled = false }
        if (card) card.classList.remove('loading')
        return
      }
      if (!u.verified) {
        state.pendingVerifyEmail = u.email
        saveLocal()
        if (submitBtn) { submitBtn.classList.remove('loading'); submitBtn.disabled = false }
        if (card) card.classList.remove('loading')
        setRoute('verify')
        return
      }
      state.user = { email: u.email, role: u.role }
      els.accountStatus.textContent = 'Sesión iniciada como usuario'
      els.logoutBtn.style.display = ''
      els.navAdmin.style.display = u.role === 'admin' ? '' : 'none'
      if (els.accountNavLink) els.accountNavLink.style.display = 'none'
      showToast('Inicio de sesión exitoso')
      localStorage.setItem('niro_session_last', String(Date.now()))
      if (!localStorage.getItem('niro_session_max_days')) localStorage.setItem('niro_session_max_days', '10')
      saveLocal()
      setRoute('home')
      if (submitBtn) { submitBtn.classList.remove('loading'); submitBtn.disabled = false }
      if (card) card.classList.remove('loading')
    }
  })
  const forgot = document.querySelector('.forgot')
  if (forgot) {
    forgot.addEventListener('click', e => {
      e.preventDefault()
      const card = document.querySelector('.login-card')
      if (card) card.classList.add('loading')
      setTimeout(() => {
        showToast('Si el email existe, enviamos instrucciones')
        if (card) card.classList.remove('loading')
      }, 1200)
    })
  }
  els.emailInput.addEventListener('input', () => { els.emailError.style.display = 'none'; els.emailInput.classList.remove('invalid') })
  els.passwordInput.addEventListener('input', () => { els.passwordError.style.display = 'none'; els.passwordInput.classList.remove('invalid') })
    els.logoutBtn.addEventListener('click', () => {
      state.user = null
      els.accountStatus.textContent = ''
      els.logoutBtn.style.display = 'none'
      els.navAdmin.style.display = 'none'
      if (els.accountNavLink) els.accountNavLink.style.display = ''
      if (els.navLogout) els.navLogout.style.display = 'none'
      saveLocal()
      showToast('Sesión cerrada')
    })
  if (els.navLogout) {
    els.navLogout.addEventListener('click', e => {
      e.preventDefault()
      state.user = null
      els.accountStatus.textContent = ''
      els.logoutBtn.style.display = 'none'
      els.navAdmin.style.display = 'none'
      if (els.accountNavLink) els.accountNavLink.style.display = ''
      els.navLogout.style.display = 'none'
      saveLocal()
      showToast('Sesión cerrada')
      setRoute('home')
    })
  }
  if (els.togglePass) {
    els.togglePass.addEventListener('click', () => {
      const is = els.passwordInput.type === 'password'
      els.passwordInput.type = is ? 'text' : 'password'
      els.togglePass.textContent = is ? 'Ocultar' : 'Ver'
    })
    els.togglePass.textContent = els.passwordInput.type === 'password' ? 'Ver' : 'Ocultar'
  }
}

function handleSignup() {
  if (!els.signupForm) return
  const show = () => { els.signupForm.style.display = ''; els.loginForm.style.display = 'none' }
  const hide = () => { els.signupForm.style.display = 'none'; els.loginForm.style.display = '' }
  if (els.showSignup) els.showSignup.addEventListener('click', e => { e.preventDefault(); show() })
  if (els.cancelSignup) els.cancelSignup.addEventListener('click', () => hide())
  const toggle = (input, btn) => {
    if (!input || !btn) return
    btn.addEventListener('click', () => {
      const show = input.type === 'password'
      input.type = show ? 'text' : 'password'
      btn.textContent = show ? 'Ocultar' : 'Ver'
    })
  }
  toggle(els.signupPasswordInput, els.toggleSignupPass1)
  toggle(els.signupConfirmInput, els.toggleSignupPass2)
  const strength = v => {
    let s = 0
    if (v.length >= 8) s++
    if (/[A-Z]/.test(v)) s++
    if (/[a-z]/.test(v)) s++
    if (/\d/.test(v)) s++
    if (/[^A-Za-z0-9]/.test(v)) s++
    if (s <= 2) return 'Contraseña débil'
    if (s === 3 || s === 4) return 'Contraseña media'
    return 'Contraseña fuerte'
  }
  if (els.signupPasswordInput && els.signupStrength) {
    els.signupPasswordInput.addEventListener('input', () => {
      els.signupStrength.textContent = strength(els.signupPasswordInput.value)
    })
  }
  els.signupForm.addEventListener('submit', e => {
    e.preventDefault()
    const email = els.signupEmailInput.value.trim()
    const name = els.signupNameInput.value.trim()
    const password = els.signupPasswordInput.value.trim()
    const confirm = els.signupConfirmInput.value.trim()
    const accepted = !!(els.signupTermsCheck && els.signupTermsCheck.checked)
    if (!email || !name || !password) { showToast('Completa todos los campos'); return }
    if (password !== confirm) { const se = document.getElementById('signupError'); if (se) { se.textContent = 'Las contraseñas no coinciden'; se.style.display = '' } return }
    if (!accepted) { const se = document.getElementById('signupError'); if (se) { se.textContent = 'Acepta los términos y privacidad'; se.style.display = '' } return }
    const exists = state.users.some(u => u.email === email)
    if (exists) { showToast('El email ya existe'); return }
    if (els.signupSubmitBtn) { els.signupSubmitBtn.classList.add('loading'); els.signupSubmitBtn.disabled = true }
    state.users.push({ email, name, password, role: 'user', banned: false, verified: false })
    saveLocal()
    renderUsersList()
    showToast('Cuenta creada: verifica tu acceso')
    state.pendingVerifyEmail = email
    saveLocal()
    hide()
    setRoute('verify')
    if (els.signupSubmitBtn) { els.signupSubmitBtn.classList.remove('loading'); els.signupSubmitBtn.disabled = false }
  })
}

function handleNav() {
  document.querySelectorAll('[data-route]').forEach(el => {
    el.addEventListener('click', e => {
      e.preventDefault()
      const r = el.dataset.route
      if (r === 'admin' && !isAdmin()) { setRoute('account'); return }
      if (r === 'home' && state.pendingVerifyEmail) { setRoute('verify'); return }
      setRoute(r)
      updateSessionActivity()
    })
  })
  if (els.menuBtn) {
    els.menuBtn.addEventListener('click', () => {
      const open = document.body.classList.toggle('menu-open')
      document.body.classList.toggle('nav-open', open)
    })
  }
}

function handleModal() {
  els.modalClose.addEventListener('click', () => {
    els.modal.classList.remove('show')
    els.modal.setAttribute('aria-hidden', 'true')
  })
  els.modal.addEventListener('click', e => {
    if (e.target.classList.contains('modal-backdrop')) {
      els.modal.classList.remove('show')
      els.modal.setAttribute('aria-hidden', 'true')
    }
  })
}

function handleFilters() {
  els.searchInput.addEventListener('input', e => { state.filters.text = e.target.value; filterCatalog() })
  els.genreSelect.addEventListener('change', e => { state.filters.genre = e.target.value; filterCatalog() })
  els.typeSelect.addEventListener('change', e => { state.filters.type = e.target.value; filterCatalog() })
  els.clearFilters.addEventListener('click', () => {
    state.filters = { text: "", genre: "", type: "" }
    els.searchInput.value = ''
    els.genreSelect.value = ''
    els.typeSelect.value = ''
    filterCatalog()
  })
}

function pushNotification(kind, title, id) {
  const exists = state.notifications.some(n => n.id === id)
  if (exists) return
  const n = { id, kind, title, at: Date.now() }
  state.notifications.unshift(n)
  saveLocal()
  renderNotifications()
}

function renderNotifications() {
  els.notifDot.style.display = state.notifications.length ? '' : 'none'
  els.notifPanel.innerHTML = state.notifications.slice(0,8).map(n => `<div class="notif-item"><div><strong>${n.kind}</strong></div><div>${n.title}</div></div>`).join('')
}

function handleNotifications() {
  if (!els.notifBtn) return
  els.notifBtn.addEventListener('click', () => {
    const vis = els.notifPanel.style.display === 'none' || els.notifPanel.style.display === ''
    renderNotifications()
    els.notifPanel.style.display = vis ? '' : 'none'
  })
  document.addEventListener('click', e => {
    if (!els.notifPanel.contains(e.target) && !els.notifBtn.contains(e.target)) {
      els.notifPanel.style.display = 'none'
    }
  })
}

function handleButtonEffects() {
  document.addEventListener('click', e => {
    const b = e.target.closest('.btn-primary')
    if (!b) return
    const r = b.getBoundingClientRect()
    const x = ((e.clientX - r.left)/r.width)*100 + '%'
    const y = ((e.clientY - r.top)/r.height)*100 + '%'
    b.style.setProperty('--x', x)
    b.style.setProperty('--y', y)
    b.classList.add('clicked')
    setTimeout(() => b.classList.remove('clicked'), 500)
  })
}

function handleHeroRotator() {
  const el = els.heroRotator
  if (!el) return
  const msgs = ['Películas y series premium', 'Calidad sin cortes', 'Tu entretenimiento, a tu ritmo']
  let i = 0
  el.textContent = msgs[i]
  setInterval(() => { i = (i + 1) % msgs.length; el.textContent = msgs[i] }, 2500)
}

function detectDevice() {
  const w = window.innerWidth
  document.body.classList.remove('device-mobile','device-tablet','device-desktop')
  if (w < 680) document.body.classList.add('device-mobile')
  else if (w < 1100) document.body.classList.add('device-tablet')
  else document.body.classList.add('device-desktop')
  if (!document.body.classList.contains('device-mobile')) {
    document.body.classList.remove('menu-open','nav-open')
  }
}

function handleDevice() {
  detectDevice()
  let t
  window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(detectDevice, 100) })
}

function applyAuthUI() {
  els.navAdmin.style.display = isAdmin() ? '' : 'none'
  if (els.accountNavLink) els.accountNavLink.style.display = state.user ? 'none' : ''
  if (els.navLogout) els.navLogout.style.display = state.user ? '' : 'none'
}

async function init() {
  await storage.init().catch(() => {})
  await loadLocal()
  const ok = await loadRemote()
  if (ok) await saveLocal()
  if (!localStorage.getItem('niro_session_max_days')) localStorage.setItem('niro_session_max_days', '10')
  updateSessionActivity()
  checkSessionExpiry()
  applyAuthUI()
  renderCarousels()
  renderHero()
  renderCatalog()
  renderAdminStats()
  handleNav()
  handleModal()
  handleFilters()
  handleLogin()
  handleSignup()
  handleAdminForm()
  handleAdminMenu()
  handleSeriesAdmin()
  handleUserForm()
  handleNotifications()
  handleButtonEffects()
  handleHeroRotator()
  handleHeroParallax()
  handleDevice()
  handleSupportForm()
  handleVerifyView()
  window.addEventListener('click', updateSessionActivity)
  window.addEventListener('keydown', updateSessionActivity)
  if (els.addCodeBtn) {
    els.addCodeBtn.addEventListener('click', () => {
      const c = (els.newCodeInput && els.newCodeInput.value || '').trim()
      if (!c) { showToast('Escribe un código'); return }
      if (state.codes.includes(c)) { showToast('Código ya existe'); return }
      state.codes.push(c)
      if (els.newCodeInput) els.newCodeInput.value = ''
      saveLocal()
      renderCodesList()
      showToast('Código creado')
    })
  }
  renderCodesList()
  if (els.adminFormContainer) els.adminFormContainer.style.display = 'none'
  if (els.adminUsersContainer) els.adminUsersContainer.style.display = 'none'
  if (els.adminContentContainer) els.adminContentContainer.style.display = ''
  state.items.filter(i => i.isNew).forEach(i => pushNotification('Estreno', `${i.type}: ${i.title}`, i.id))
  if (state.pendingVerifyEmail) setRoute('verify')
  else setRoute('home')
  startAutoSync()
  const pl = document.getElementById('pageLoading')
  if (pl) setTimeout(() => { pl.style.display = 'none' }, 300)
}

init()
