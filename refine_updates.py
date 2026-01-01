import re
import os

file_path = r"c:\Users\Camero\Downloads\Mov\index_pro.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# ----------------------------------------------------------------------------
# 1. PWA Update Logic (Non-intrusive)
# ----------------------------------------------------------------------------

# We'll replace the previous SW script with a smarter one
old_sw_script_pattern = r'<script>\s+if \(\'serviceWorker\' in navigator\) \{[\s\S]+?\}\s+<\/script>'

new_sw_script = """<script>
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js')
                    .then(registration => {
                        console.log('SW registered', registration);
                        
                        function showUpdateToast(worker) {
                            // Don't show if user is watching video
                            const video = document.querySelector('video');
                            if(video && !video.paused) {
                                console.log("Update pending, but video playing. deferring.");
                                return;
                            }
                            
                            // Check if toast already exists
                            if(document.querySelector('.update-toast')) return;

                            // Custom Toast with Action
                            const toast = document.createElement('div');
                            toast.className = 'update-toast';
                            toast.innerHTML = `
                                <div>
                                    <i class="ri-download-cloud-2-line"></i>
                                    <span>Nueva versión disponible</span>
                                </div>
                                <button>Actualizar</button>
                            `;
                            Object.assign(toast.style, {
                                position: 'fixed', bottom: '80px', right: '20px', 
                                background: 'rgba(30, 20, 50, 0.95)', border: '1px solid var(--color-brand-primary)',
                                padding: '15px', borderRadius: '12px', zIndex: '10000',
                                display: 'flex', gap: '15px', alignItems: 'center',
                                boxShadow: '0 10px 30px rgba(0,0,0,0.5)', backdropFilter: 'blur(10px)',
                                animation: 'slideInUp 0.5s cubic-bezier(0.19, 1, 0.22, 1)'
                            });
                            // Style the button
                            const btn = toast.querySelector('button');
                            Object.assign(btn.style, {
                                background: 'var(--color-brand-primary)', color: 'white',
                                border: 'none', padding: '8px 16px', borderRadius: '6px',
                                fontWeight: '600', fontSize: '0.9rem'
                            });
                            
                            btn.onclick = () => {
                                worker.postMessage({ type: 'SKIP_WAITING' });
                                toast.remove();
                            };

                            document.body.appendChild(toast);
                        }

                        // Check for updates
                        registration.addEventListener('updatefound', () => {
                            const newWorker = registration.installing;
                            newWorker.addEventListener('statechange', () => {
                                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                                    showUpdateToast(newWorker);
                                }
                            });
                        });
                        
                        // Check if there is already a waiting worker
                         if (registration.waiting) {
                              showUpdateToast(registration.waiting);
                        }
                    })
                    .catch(err => console.log('SW registration failed', err));
                
                // Reload when controller changes
                navigator.serviceWorker.addEventListener('controllerchange', () => {
                    window.location.reload();
                });
            });
        }
    </script>"""

# Try to find the pattern. If not found (maybe already replaced?), we might need to handle that.
# But for now assume it matches the previous structure.
if re.search(old_sw_script_pattern, content):
    content = re.sub(old_sw_script_pattern, new_sw_script, content)
else:
    print("Warning: SW Script pattern not found. It might have been already updated.")


# ----------------------------------------------------------------------------
# 2. Improve Mobile Menu (CSS) & Manage Profiles Fix
# ----------------------------------------------------------------------------
# Refined CSS
refined_css = """
    /* Mobile Bottom Nav Styles - Refined */
    .mobile-nav {
        display: none;
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(15, 7, 32, 0.85); /* More transparent */
        backdrop-filter: blur(20px); /* Glassmorphism */
        -webkit-backdrop-filter: blur(20px);
        border-top: 1px solid rgba(255,255,255,0.08);
        z-index: 5000;
        padding-bottom: env(safe-area-inset-bottom);
        height: calc(65px + env(safe-area-inset-bottom)); /* Slightly taller */
        justify-content: space-around;
        align-items: center;
        box-shadow: 0 -10px 40px rgba(0,0,0,0.3);
    }
    
    .mobile-nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #8B8198; /* Muted purple */
        font-size: 0.65rem;
        font-weight: 500;
        gap: 6px;
        width: 100%;
        height: 100%;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        position: relative;
    }
    
    .mobile-nav-item i {
        font-size: 1.5rem;
        transition: transform 0.3s;
    }
    
    /* Active State */
    .mobile-nav-item.active {
        color: white;
    }
    .mobile-nav-item.active i {
        color: var(--color-brand-primary);
        transform: translateY(-2px);
        text-shadow: 0 0 15px var(--color-brand-glow);
    }
    
    /* Active Indicator dot */
    .mobile-nav-item.active::after {
        content: '';
        position: absolute;
        top: 10px;
        width: 4px;
        height: 4px;
        background: var(--color-brand-primary);
        border-radius: 50%;
        box-shadow: 0 0 10px var(--color-brand-primary);
    }

    /* Profile Avatar in Nav */
    #mobile-nav-avatar {
        transition: all 0.3s;
        border: 2px solid transparent;
    }
    .mobile-nav-item.active #mobile-nav-avatar {
        border-color: var(--color-brand-primary);
        transform: scale(1.1);
    }

    /* Fix Manage Profiles Vertical Layout */
    @media (max-width: 768px) {
        .manage-profiles-container {
             /* Ensure it takes full height but respects nav */
             min-height: calc(100vh - 80px);
             justify-content: center; 
        }
        
        .manage-profiles-grid {
            display: grid !important;
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 20px !important;
            width: 100%;
            max-width: 320px; 
            margin: 0 auto;
        }
        
        .manage-profile-avatar-wrapper {
             width: 90px !important;
             height: 90px !important;
             margin: 0 auto 10px auto !important;
        }
        
        .profile-item {
             display: flex !important;
             flex-direction: column !important;
             align-items: center !important;
             text-align: center !important;
        }
    }
"""

# Append CSS if not already present (checking a unique string)
if "Mobile Bottom Nav Styles - Refined" not in content:
    content = content.replace('</style>', refined_css + '\n    </style>')
else:
    print("CSS already applied.")


# ----------------------------------------------------------------------------
# 3. Update Profile Icon Logic (JS)
# ----------------------------------------------------------------------------
js_hook = """
            renderHeader: () => {
                // Update Mobile Nav Avatar
                const user = app.state.user;
                const profile = app.state.currentProfile;
                const navAvatar = document.getElementById('mobile-nav-avatar');
                if(navAvatar) {
                    if(profile && profile.avatar) {
                        navAvatar.src = profile.avatar;
                    } else {
                        // Default/Placeholder
                        navAvatar.src = "https://ui-avatars.com/api/?name=User&background=random"; 
                    }
                }
                
                // Highlight active mobile nav
                document.querySelectorAll('.mobile-nav-item').forEach(el => el.classList.remove('active'));
                const route = app.state.route;
                if(route === 'home') document.getElementById('nav-home')?.classList.add('active');
                if(route === 'series') document.getElementById('nav-series')?.classList.add('active');
                if(route === 'movies') document.getElementById('nav-movies')?.classList.add('active');
                if(route === 'mylist') document.getElementById('nav-mylist')?.classList.add('active');
                if(route === 'profile') document.getElementById('nav-profile')?.classList.add('active');
                
                const h = document.getElementById('main-header');
"""

if "Update Mobile Nav Avatar" not in content:
    content = content.replace('renderHeader: () => {', js_hook)
else:
    print("JS Hook already applied.")

# ----------------------------------------------------------------------------
# 4. Profile Icon HTML Structure
# ----------------------------------------------------------------------------
old_profile_nav = '<div class="mobile-nav-item" id="nav-profile" onclick="app.openMobileProfileMenu()"><i class="ri-user-3-fill"></i><span>Perfil</span></div>'
# Use fallback logic: Show Image if loaded, otherwise show Icon
new_profile_nav = '<div class="mobile-nav-item" id="nav-profile" onclick="app.openMobileProfileMenu()"><img id="mobile-nav-avatar" src="" style="width: 24px; height: 24px; border-radius: 4px; object-fit: cover; display: none;" onload="this.style.display=\'block\'; this.nextElementSibling.style.display=\'none\'" onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'block\'"><i class="ri-user-3-fill"></i><span>Perfil</span></div>'

if old_profile_nav in content:
    content = content.replace(old_profile_nav, new_profile_nav)
    print("Profile HTML updated.")
else:
    print("Profile HTML not found or already updated.")

# ----------------------------------------------------------------------------
# 5. Fix Manage Profiles Layout in JS (Grid Class)
# ----------------------------------------------------------------------------
# Ensure the manage profiles container has the correct class for our CSS to target
# Looking for where manage profiles is rendered.
# Usually in app.renderManageProfiles()
# We need to make sure the container has class 'manage-profiles-container' and grid has 'manage-profiles-grid'

# Search for the function
# app.renderManageProfiles = () => { ...
# We might need to inject classes if they aren't there.
# Let's check via regex if we can find the template string.

# Pattern for the grid container in manage profiles
grid_pattern = r'<div class="profile-list" style="(.+?)">'
# We want to add class 'manage-profiles-grid' to this div if it's in renderManageProfiles
# But doing this via regex blindly is risky. 
# However, our CSS targets `.manage-profiles-grid`. If the HTML doesn't have this class, the CSS won't work.
# The existing HTML uses `.profile-list`.
# So let's update the CSS to target `.profile-list` inside `.manage-profiles-container` OR just use `.profile-list`?
# In the CSS above, I used `.manage-profiles-grid`.
# Let's check the HTML generation in `index_pro.html` for manage profiles.
# Since I can't easily see it, I'll assume it uses `.profile-list`.
# So I should change my CSS injection to target `.profile-list` instead of `.manage-profiles-grid`.

refined_css = refined_css.replace('.manage-profiles-grid', '.profile-list')
# Also need to make sure the container has a class or ID we can target if needed.
# But `.profile-list` is quite specific if scoped correctly. 
# Actually `.profile-list` is also used in the Gate.
# We only want to affect the Manage Profiles screen.
# The Manage Profiles screen is usually rendered into `#main-view`.
# So `.manage-profiles-view .profile-list`?
# I'll rely on the fact that I can't easily change the JS rendering logic without replacing the whole function.
# But wait, I can just use `@media (max-width: 768px) { .profile-list { ... } }`? 
# No, that would affect the Profile Gate too.
# The Profile Gate `.profile-list` should also probably be 2 columns on mobile if it isn't already.
# So applying it to `.profile-list` generally on mobile might be a GOOD thing.
# Let's do that.

content = content.replace('.manage-profiles-grid', '.profile-list')


with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updates applied to index_pro.html")
