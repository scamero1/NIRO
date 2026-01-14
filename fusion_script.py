
import re
import os

file_path = 'index_final.html'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
except UnicodeDecodeError:
    with open(file_path, 'r', encoding='latin-1') as f:
        content = f.read()

# ---------------------------------------------------------
# NEW CSS
# ---------------------------------------------------------
new_css = """
    <style>
        /* --- DESIGN TOKENS & RESET --- */
        :root {
            --bg-color: #050505;
            --glass-bg: rgba(20, 20, 20, 0.6);
            --glass-border: rgba(255, 255, 255, 0.08);
            --primary-accent: #e50914; 
            --text-primary: #ffffff;
            --text-secondary: rgba(255, 255, 255, 0.7);
            --gold-gradient: linear-gradient(135deg, #FFD700 0%, #FDB931 100%);
            --metal-gradient: linear-gradient(135deg, #e0e0e0 0%, #ffffff 50%, #a0a0a0 100%);
            --color-brand-primary: #8B5CF6; /* Keep for functional compat */
        }
        * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        body { font-family: 'Outfit', sans-serif; background-color: var(--bg-color); color: var(--text-primary); overflow-x: hidden; padding-bottom: 80px; }

        /* --- GLASSMORPHISM HEADER --- */
        .header { position: fixed; top: 0; left: 0; width: 100%; height: 70px; display: flex; align-items: center; justify-content: space-between; padding: 0 24px; z-index: 1000; background: rgba(0, 0, 0, 0.3); backdrop-filter: blur(15px); border-bottom: 1px solid var(--glass-border); transition: all 0.3s ease; }
        .logo { font-weight: 800; font-size: 24px; letter-spacing: -1px; background: linear-gradient(to right, #fff, #aaa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .nav-icons i { font-size: 22px; margin-left: 20px; color: var(--text-secondary); }
        .system-status { display: flex; align-items: center; gap: 6px; font-size: 10px; font-weight: 600; color: #46d369; background: rgba(70, 211, 105, 0.1); padding: 4px 8px; border-radius: 12px; border: 1px solid rgba(70, 211, 105, 0.2); margin-right: 12px; }
        .status-dot { width: 6px; height: 6px; background-color: #46d369; border-radius: 50%; box-shadow: 0 0 8px #46d369; animation: pulse-green 2s infinite; }
        @keyframes pulse-green { 0% { opacity: 1; box-shadow: 0 0 0 0 rgba(70, 211, 105, 0.7); } 70% { opacity: 1; box-shadow: 0 0 0 6px rgba(70, 211, 105, 0); } 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(70, 211, 105, 0); } }

        /* --- HERO SECTION --- */
        .hero { position: relative; height: 80vh; width: 100%; display: flex; align-items: flex-end; padding-bottom: 60px; background: url('https://images.unsplash.com/photo-1509248961158-e54f6934749c?q=80&w=2037&auto=format&fit=crop') center/cover no-repeat; mask-image: linear-gradient(to bottom, black 70%, transparent 100%); }
        .hero::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to top, var(--bg-color) 10%, rgba(0,0,0,0.6) 50%, rgba(0,0,0,0.2) 100%); }
        .hero-content { position: relative; z-index: 10; padding: 0 24px; width: 100%; max-width: 800px; }
        .hero-tags { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; font-size: 13px; font-weight: 500; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; }
        .match-score { color: #46d369; font-weight: 700; }
        .hero-title { font-size: clamp(3rem, 8vw, 5rem); font-weight: 800; line-height: 1.1; margin-bottom: 20px; text-shadow: 0 4px 20px rgba(0,0,0,0.8); background: linear-gradient(180deg, #fff 0%, #ccc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .hero-desc { font-size: 16px; line-height: 1.5; color: rgba(255,255,255,0.9); margin-bottom: 24px; max-width: 500px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
        .hero-actions { display: flex; gap: 16px; align-items: center; }
        .btn-play { background: var(--metal-gradient); color: #000; border: none; padding: 14px 32px; border-radius: 8px; font-weight: 700; font-size: 16px; display: flex; align-items: center; gap: 8px; cursor: pointer; transition: transform 0.2s; box-shadow: 0 4px 15px rgba(255, 255, 255, 0.2); }
        .btn-play:active { transform: scale(0.95); }
        .btn-secondary { background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px); color: white; border: 1px solid rgba(255,255,255,0.1); width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; cursor: pointer; }

        /* --- MOOD UI --- */
        .mood-section { padding: 40px 24px; }
        .section-title { font-size: 18px; font-weight: 600; margin-bottom: 20px; letter-spacing: 0.5px; color: var(--text-secondary); }
        .mood-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
        .mood-card { height: 120px; border-radius: 16px; position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: transform 0.3s ease; }
        .mood-card:active { transform: scale(0.98); }
        .mood-text { position: relative; z-index: 2; font-weight: 700; font-size: 16px; text-transform: uppercase; letter-spacing: 1px; text-shadow: 0 2px 10px rgba(0,0,0,0.5); }
        .mood-chill { background: linear-gradient(45deg, #0093E9 0%, #80D0C7 100%); }
        .mood-intensity { background: linear-gradient(45deg, #850000 0%, #cc0000 100%); }
        .mood-magic { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .mood-drama { background: #000; border: 1px solid #333; }

        /* --- LISTS --- */
        .content-list { padding: 0 0 40px 24px; }
        .list-header { margin-bottom: 16px; font-size: 18px; font-weight: 600; color: #eee; }
        .scroll-container { display: flex; gap: 16px; overflow-x: auto; padding-right: 24px; padding-bottom: 20px; scrollbar-width: none; }
        .scroll-container::-webkit-scrollbar { display: none; }
        .media-card { flex: 0 0 140px; height: 210px; border-radius: 12px; position: relative; transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94); cursor: pointer; overflow: hidden; }
        .media-card img { width: 100%; height: 100%; object-fit: cover; border-radius: 12px; }
        .media-info { position: absolute; bottom: 0; left: 0; width: 100%; padding: 15px; background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); opacity: 0; transform: translateY(10px); transition: all 0.3s ease; }
        .media-card:hover { transform: scale(1.05); z-index: 10; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .media-card:hover .media-info { opacity: 1; transform: translateY(0); }
        .media-title { font-size: 14px; font-weight: 700; margin-bottom: 4px; }
        .media-desc { font-size: 11px; color: #ccc; line-height: 1.2; }

        /* --- BOTTOM NAV --- */
        .bottom-nav { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); width: 90%; max-width: 400px; height: 65px; background: rgba(20, 20, 20, 0.85); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border-radius: 24px; border: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-around; align-items: center; z-index: 1000; box-shadow: 0 10px 40px rgba(0,0,0,0.5); }
        .nav-item { display: flex; flex-direction: column; align-items: center; justify-content: center; color: #888; font-size: 10px; gap: 4px; cursor: pointer; transition: color 0.3s; width: 60px; }
        .nav-item i { font-size: 20px; }
        .nav-item.active { color: #fff; }
        .nav-item.active i { background: linear-gradient(to bottom, #fff, #aaa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

        /* --- FUNCTIONAL (TOAST, MODAL, VIDEO) --- */
        .toast-container { position: fixed; bottom: 90px; right: 20px; z-index: 3000; display: flex; flex-direction: column; gap: 10px; pointer-events: none; }
        .toast { background: rgba(30, 16, 53, 0.9); backdrop-filter: blur(10px); color: white; padding: 1rem 1.5rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 10px 30px rgba(0,0,0,0.5); display: flex; align-items: center; gap: 10px; animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1); pointer-events: auto; }
        @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        .modal-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 5000; display: none; align-items: center; justify-content: center; backdrop-filter: blur(5px); }
        .modal-content { background: #1a1a1a; padding: 20px; border-radius: 12px; max-width: 90%; max-height: 90vh; overflow-y: auto; position: relative; }
        /* Video Player Styles (Simplified) */
        .video-overlay-container { position: fixed; inset: 0; background: black; z-index: 9999; display: flex; flex-direction: column; }
    </style>
"""

# Replace all style blocks in head
# Strategy: Find first <style> and replace everything until the <script> that typically follows styles in index.html
# Or just replace all <style>...</style> occurrences.
content = re.sub(r'<style[\s\S]*?</style>', '', content)
# Insert new CSS before </head>
content = content.replace('</head>', new_css + '\n</head>')


# ---------------------------------------------------------
# NEW BODY HTML
# ---------------------------------------------------------
new_body_html = """
    <div id="app">
        <!-- Header -->
        <header class="header">
            <div class="logo">NIRO</div>
            <div class="nav-icons" style="display:flex; align-items:center;">
                <div class="system-status">
                    <div class="status-dot"></div>
                    <span>ONLINE</span>
                </div>
                <i class="ri-search-line"></i>
                <i class="ri-notification-3-line"></i>
                <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Niro" style="width: 28px; height: 28px; border-radius: 4px; vertical-align: middle; margin-left: 20px;">
            </div>
        </header>

        <!-- Hero Section -->
        <section class="hero">
            <div class="hero-content">
                <div class="hero-tags">
                    <span class="match-score">90% MATCH</span>
                    <span>2025</span>
                    <span style="border: 1px solid #666; padding: 0 4px; border-radius: 2px;">16+</span>
                    <span>2h 15m</span>
                </div>
                <h1 class="hero-title">La Hermanastra<br>Fea</h1>
                <p class="hero-desc">En esta reimaginación gótica del clásico, la "villana" toma el control con sus propias botas. Un thriller psicológico donde la magia tiene un precio sangriento.</p>
                <div class="hero-actions">
                    <button class="btn-play" onclick="app.playItem(1)">
                        <i class="ri-play-fill"></i> Reproducir
                    </button>
                    <button class="btn-secondary" onclick="app.toggleMyList(1)">
                        <i class="ri-add-line"></i>
                    </button>
                    <button class="btn-secondary" onclick="app.openDetails(1)">
                        <i class="ri-information-line"></i>
                    </button>
                </div>
            </div>
        </section>

        <!-- Mood Based UI -->
        <section class="mood-section">
            <h2 class="section-title">¿QUÉ VIBE TIENES HOY?</h2>
            <div class="mood-grid">
                <div class="mood-card mood-chill" onclick="app.filterByMood('chill')">
                    <span class="mood-text">Chill & Relax</span>
                </div>
                <div class="mood-card mood-intensity" onclick="app.filterByMood('intense')">
                    <span class="mood-text">Intensidad</span>
                </div>
                <div class="mood-card mood-magic" onclick="app.filterByMood('magic')">
                    <span class="mood-text">Magia & Sci-Fi</span>
                </div>
                <div class="mood-card mood-drama" onclick="app.filterByMood('drama')">
                    <span class="mood-text">Drama Puro</span>
                </div>
            </div>
        </section>

        <!-- Main View for Lists -->
        <main id="main-view">
            <!-- Dynamic Lists Go Here -->
        </main>

        <!-- Bottom Nav -->
        <nav class="bottom-nav">
            <div class="nav-item active" onclick="app.router('home')">
                <i class="ri-home-5-fill"></i>
                <span>Inicio</span>
            </div>
            <div class="nav-item" onclick="app.router('movies')">
                <i class="ri-film-fill"></i>
                <span>Pelis</span>
            </div>
            <div class="nav-item" onclick="app.router('series')">
                <i class="ri-tv-2-line"></i>
                <span>Series</span>
            </div>
            <div class="nav-item" onclick="app.router('downloads')">
                <i class="ri-download-cloud-2-line"></i>
                <span>Descargas</span>
            </div>
        </nav>

        <!-- Toast Container -->
        <div class="toast-container" id="toast-container"></div>
        
        <!-- Modal -->
        <div class="modal-backdrop" id="generic-modal">
            <div class="modal-content" id="generic-modal-content"></div>
        </div>
    </div>
"""

# Replace body content: from <body> to <script>
# We'll use a regex that matches <body>...<script>
# Note: we must match the *first* script that contains app logic.
# The previous file had scripts in head too.
# We want to replace content inside <body>...</body> but KEEP the scripts at the end.
# Usually, <body> tags contain visible HTML, then <script> tags at the end.
# We will find the position of `<body>` and the position of the last `<div class="modal-backdrop"` (or similar last element of old html)
# Simpler: Find `<body>` and `</body>`.
# Inside that range, find the LAST `<script>` block and keep it. Replace everything before it.
# But there might be multiple script blocks.
# Let's assume the scripts are at the end of body.
# We will replace everything from after `<body>` until the first `<script>` inside `<body>`.
# If there are no scripts inside body, we replace until `</body>`.

body_match = re.search(r'<body[^>]*>', content)
if body_match:
    body_start_pos = body_match.end()
    # Find first script after body start
    script_match = re.search(r'<script>', content[body_start_pos:])
    if script_match:
        script_pos = body_start_pos + script_match.start()
        # Replace
        content = content[:body_start_pos] + new_body_html + content[script_pos:]
    else:
        # No scripts in body? Append new body html
        content = content[:body_start_pos] + new_body_html + '</body></html>'

# ---------------------------------------------------------
# NEW JS OVERRIDES
# ---------------------------------------------------------
final_render_home_js = """
<script>
// OVERRIDE renderHome for New UI
app.renderHome = function(filterType) {
    const main = document.getElementById('main-view');
    if(!main) return;
    
    let html = '';
    
    // Logic to handle filterType (Movies, Series, etc.)
    let categories = [];
    if(filterType === 'movies') {
        categories.push({ title: "Películas", filter: i => i.type === 'movie' });
    } else if(filterType === 'series') {
        categories.push({ title: "Series", filter: i => i.type === 'series' });
    } else {
        categories.push(
            { title: "Tendencias", filter: i => i.year >= 2024 },
            { title: "Recientes", filter: i => true },
            { title: "Acción", filter: i => i.genre && i.genre.includes('Acción') }
        );
    }
    
    categories.forEach(cat => {
        let items = allItems.filter(cat.filter);
        if(app.state.currentMood) {
             if(app.state.currentMood === 'chill') items = items.filter(i => i.genre && (i.genre.includes('Comedia') || i.genre.includes('Animación') || i.genre.includes('Romance')));
             if(app.state.currentMood === 'intense') items = items.filter(i => i.genre && (i.genre.includes('Acción') || i.genre.includes('Terror') || i.genre.includes('Suspenso')));
             if(app.state.currentMood === 'magic') items = items.filter(i => i.genre && (i.genre.includes('Fantasía') || i.genre.includes('Ciencia Ficción')));
             if(app.state.currentMood === 'drama') items = items.filter(i => i.genre && (i.genre.includes('Drama') || i.genre.includes('Misterio')));
        }
        
        if(items.length === 0) return;
        
        html += `
            <section class="content-list">
                <h2 class="list-header">${cat.title}</h2>
                <div class="scroll-container">
                    ${items.slice(0, 15).map(item => `
                        <div class="media-card" onclick="openDetails(${item.id})">
                            <img src="${item.img}" loading="lazy">
                            <div class="media-info">
                                <div class="media-title">${item.title}</div>
                                <div class="media-desc">${item.year}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </section>
        `;
    });
    
    main.innerHTML = html;
};

// Also override renderHeader to do nothing (since we have static header)
app.renderHeader = function() {}; 

// Override router to handle active state of bottom nav
const originalRouter = app.router;
app.router = function(route) {
    // Call original logic to set state
    if(originalRouter) originalRouter.call(app, route);
    
    // Update nav classes
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    if(route === 'home') document.querySelectorAll('.nav-item')[0].classList.add('active');
    if(route === 'movies') document.querySelectorAll('.nav-item')[1].classList.add('active');
    if(route === 'series') document.querySelectorAll('.nav-item')[2].classList.add('active');
    if(route === 'downloads' || route === 'mylist') document.querySelectorAll('.nav-item')[3].classList.add('active');
};

// Override filterByMood
app.filterByMood = function(mood) {
    app.state.currentMood = mood;
    // Update UI
    document.querySelectorAll('.mood-card').forEach(el => el.style.opacity = '0.5');
    document.querySelectorAll('.mood-' + mood).forEach(el => el.style.opacity = '1');
    
    app.renderHome();
};
</script>
"""

content = content.replace('</body>', final_render_home_js + '</body>')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Fusion complete!")
