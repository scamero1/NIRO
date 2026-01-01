
css_injection = """
        /* -------------------------------------------------------------------------- */
        /*                             MOBILE PROFILE SHEET                           */
        /* -------------------------------------------------------------------------- */
        .bottom-sheet {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background: #1E1035;
            border-radius: 24px 24px 0 0;
            padding: 24px;
            transform: translateY(100%);
            transition: transform 0.4s cubic-bezier(0.19, 1, 0.22, 1);
            z-index: 6000;
            border-top: 1px solid rgba(255,255,255,0.1);
            display: flex;
            flex-direction: column;
            gap: 12px;
            box-shadow: 0 -10px 40px rgba(0,0,0,0.5);
            max-height: 80vh;
            overflow-y: auto;
        }
        .bottom-sheet.active {
            transform: translateY(0);
        }
        .sheet-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.6);
            z-index: 5999;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s;
            backdrop-filter: blur(5px);
        }
        .sheet-overlay.active {
            opacity: 1;
            pointer-events: auto;
        }
        .sheet-handle {
            width: 40px;
            height: 4px;
            background: rgba(255,255,255,0.2);
            border-radius: 2px;
            margin: -10px auto 15px;
        }
        .sheet-header {
            display: flex;
            align-items: center;
            gap: 16px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 10px;
        }
        .sheet-avatar {
            width: 60px;
            height: 60px;
            border-radius: 16px;
            background-size: cover;
            background-position: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            border: 2px solid rgba(255,255,255,0.1);
        }
        .sheet-user-info {
            flex: 1;
        }
        .sheet-user-info h3 {
            font-size: 1.2rem;
            margin: 0 0 4px 0;
            font-weight: 700;
            color: white;
        }
        .sheet-change-btn {
            font-size: 0.85rem;
            color: var(--color-brand-primary);
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            cursor: pointer;
            padding: 4px 0;
        }
        .sheet-item {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 16px;
            border-radius: 16px;
            background: rgba(255,255,255,0.03);
            font-size: 1rem;
            color: #e5e5e5;
            transition: transform 0.2s, background 0.2s;
            border: 1px solid transparent;
        }
        .sheet-item:active {
            background: rgba(255,255,255,0.08);
            transform: scale(0.98);
        }
        .sheet-item i {
            font-size: 1.5rem;
            color: var(--color-text-secondary);
        }
        .sheet-item.danger {
            background: rgba(239, 68, 68, 0.1);
            color: #ef4444;
            margin-top: 10px;
        }
        .sheet-item.danger i {
            color: #ef4444;
        }
        
        /* Animation for items */
        .bottom-sheet.active .sheet-item {
            animation: slideUpFade 0.4s backwards;
        }
        .bottom-sheet.active .sheet-item:nth-child(2) { animation-delay: 0.1s; }
        .bottom-sheet.active .sheet-item:nth-child(3) { animation-delay: 0.15s; }
        .bottom-sheet.active .sheet-item:nth-child(4) { animation-delay: 0.2s; }
        .bottom-sheet.active .sheet-item:nth-child(5) { animation-delay: 0.25s; }
        
        @keyframes slideUpFade {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
"""

html_injection = """
    <!-- Mobile Profile Sheet -->
    <div class="sheet-overlay" id="mobile-profile-overlay" onclick="app.closeMobileProfileMenu()"></div>
    <div class="bottom-sheet" id="mobile-profile-sheet">
        <div class="sheet-handle"></div>
        <div id="mobile-profile-content">
            <!-- Rendered by JS -->
        </div>
    </div>
"""

js_injection = """
            openMobileProfileMenu: () => {
                const sheet = document.getElementById('mobile-profile-sheet');
                const overlay = document.getElementById('mobile-profile-overlay');
                const user = app.state.user;
                const profile = app.state.currentProfile;

                if(!user || !profile) {
                    app.router('login');
                    return;
                }

                const content = document.getElementById('mobile-profile-content');
                content.innerHTML = `
                    <div class="sheet-header">
                        <div class="sheet-avatar" style="background-image:url('${profile.avatar}')"></div>
                        <div class="sheet-user-info">
                            <h3>${profile.name}</h3>
                            <div class="sheet-change-btn" onclick="app.closeMobileProfileMenu(); app.router('profiles')">
                                <i class="ri-arrow-left-right-line"></i> Cambiar perfil
                            </div>
                        </div>
                        <div onclick="app.closeMobileProfileMenu()">
                            <i class="ri-close-circle-fill" style="font-size:2rem;color:rgba(255,255,255,0.2);"></i>
                        </div>
                    </div>
                    
                    <div class="sheet-item" onclick="app.closeMobileProfileMenu(); app.router('account')">
                        <i class="ri-settings-4-line"></i>
                        <span>Cuenta</span>
                    </div>
                    
                    <div class="sheet-item" onclick="app.closeMobileProfileMenu(); app.router('mylist')">
                        <i class="ri-heart-3-line"></i>
                        <span>Mi Lista</span>
                    </div>
                    
                    ${user.role === 'admin' ? `
                    <div class="sheet-item" onclick="app.closeMobileProfileMenu(); app.router('admin')">
                        <i class="ri-shield-keyhole-line"></i>
                        <span>Panel de Admin</span>
                    </div>
                    ` : ''}

                     <div class="sheet-item" onclick="app.closeMobileProfileMenu(); app.installPWA()" id="sheet-install-btn" style="display:none;">
                        <i class="ri-download-cloud-2-line"></i>
                        <span>Instalar App</span>
                    </div>
                    
                    <div class="sheet-item danger" onclick="app.closeMobileProfileMenu(); app.logout()">
                        <i class="ri-logout-box-r-line"></i>
                        <span>Cerrar Sesión</span>
                    </div>
                `;
                
                // Show install button if available
                if(deferredPrompt) {
                     document.getElementById('sheet-install-btn').style.display = 'flex';
                }

                sheet.classList.add('active');
                overlay.classList.add('active');
            },

            closeMobileProfileMenu: () => {
                document.getElementById('mobile-profile-sheet').classList.remove('active');
                document.getElementById('mobile-profile-overlay').classList.remove('active');
            },
"""

with open('index_current.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Inject CSS
content = content.replace('</style>', css_injection + '\n    </style>')

# Inject HTML (before body end)
content = content.replace('</body>', html_injection + '\n</body>')

# Inject JS methods (add to app object)
# We look for a known method to append after, e.g., "confirmAction: (msg, onConfirm) => {"
# Actually, let's insert it at the beginning of app object for safety, or just before init.
# "init: async () => {" is a good anchor.
content = content.replace('init: async () => {', js_injection + '\n            init: async () => {')

# Modify Mobile Nav Click
# Original: onclick="app.router('profiles')"
# New: onclick="app.openMobileProfileMenu()"
# Use regex to replace only the specific one for nav-profile
import re
content = re.sub(
    r'(id="nav-profile"[^>]*onclick=")app\.router\(\'profiles\'\)', 
    r'\1app.openMobileProfileMenu()', 
    content
)

with open('index_pro.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("index_pro.html created.")
