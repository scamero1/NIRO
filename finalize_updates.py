import re
import os

file_path = r"c:\Users\Camero\Downloads\Mov\index_pro.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. New CSS
new_css = """
        /* -------------------------------------------------------------------------- */
        /*                         PROFILE MANAGEMENT RESPONSIVE                      */
        /* -------------------------------------------------------------------------- */
        .manage-profiles-container {
            min-height: 100vh;
            padding: 100px 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            animation: fadeIn 0.5s;
        }
        .manage-profiles-title {
            font-size: 3rem;
            font-weight: 500;
            margin-bottom: 3rem;
            text-align: center;
        }
        .manage-profiles-grid {
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
            justify-content: center;
            margin-bottom: 4rem;
        }
        .manage-profile-avatar-wrapper {
            width: 10vw;
            height: 10vw;
            min-width: 120px;
            min-height: 120px;
            max-width: 200px;
            max-height: 200px;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 1rem;
            position: relative;
        }
        
        /* Edit Profile Modal Classes */
        .edit-profile-modal-container {
            padding: 2rem;
            max-width: 700px;
            margin: 0 auto;
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        .edit-profile-layout {
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
        }
        
        @media (max-width: 768px) {
            .manage-profiles-container {
                padding: 80px 20px 100px 20px; /* Add bottom padding for nav */
            }
            .manage-profiles-title {
                font-size: 1.8rem;
                margin-bottom: 1.5rem;
            }
            .manage-profiles-grid {
                gap: 1.5rem;
                display: grid;
                grid-template-columns: repeat(2, 1fr);
            }
            .manage-profile-avatar-wrapper {
                width: 100%;
                height: auto;
                aspect-ratio: 1/1;
                min-width: auto;
                min-height: auto;
                max-width: none;
                max-height: none;
            }
            
            /* Edit Profile Modal Mobile */
            .edit-profile-modal-container {
                padding: 1rem;
                max-width: 100%;
                overflow-y: auto;
                max-height: 85vh; /* Ensure it fits */
            }
            .edit-profile-layout {
                flex-direction: column;
                gap: 1.5rem;
            }
            .edit-profile-avatar-section {
                display: flex;
                justify-content: center;
                flex: 0 0 auto;
            }
            .edit-profile-avatar-img {
                width: 100px !important;
                height: 100px !important;
            }
            .edit-profile-form-section {
                flex: 1;
            }
            .edit-profile-actions {
                flex-direction: column-reverse;
                gap: 10px;
            }
            .edit-profile-actions button {
                width: 100%;
                margin: 0 !important;
            }
        }
"""

if ".manage-profiles-container" not in content:
    content = content.replace("</style>", new_css + "\n    </style>")

# 2. Update manageProfiles function HTML structure
search_str = '<div class="profile-gate-container" style="min-height:100vh;'
replace_str = '<div class="manage-profiles-container">'
if search_str in content:
    content = content.replace(search_str, replace_str)

# Replace the title style
title_search = '<h1 style="font-size:3rem; font-weight:500; margin-bottom:3rem; text-align:center;">Administrar Perfiles</h1>'
title_replace = '<h1 class="manage-profiles-title">Administrar Perfiles</h1>'
if title_search in content:
    content = content.replace(title_search, title_replace)

# Replace grid style
grid_search = '<div class="profiles-grid" style="display:flex; gap:2rem; flex-wrap:wrap; justify-content:center; margin-bottom:4rem;">'
grid_replace = '<div class="manage-profiles-grid">'
if grid_search in content:
    content = content.replace(grid_search, grid_replace)

# Replace avatar wrapper style (in loop)
content = re.sub(
    r'<div class="profile-avatar-wrapper" style="[^"]+margin-bottom:1rem; position:relative;">',
    '<div class="profile-avatar-wrapper manage-profile-avatar-wrapper">',
    content
)

# Add Profile Button Wrapper
content = re.sub(
    r'<div class="profile-avatar-wrapper" style="[^"]+border:1px solid #808080; color:#808080; transition:all 0.2s; margin-bottom:1rem;">',
    '<div class="profile-avatar-wrapper manage-profile-avatar-wrapper" style="display:flex; align-items:center; justify-content:center; background:transparent; border:1px solid #808080; color:#808080;">',
    content
)


# 3. Update editProfile function HTML
# <div style="padding:2rem; max-width:700px; margin:0 auto;">
edit_modal_search = '<div style="padding:2rem; max-width:700px; margin:0 auto;">'
edit_modal_replace = '<div class="edit-profile-modal-container">'
if edit_modal_search in content:
    content = content.replace(edit_modal_search, edit_modal_replace)

# <div style="display:flex; gap:2rem; flex-wrap:wrap;">
layout_search = '<div style="display:flex; gap:2rem; flex-wrap:wrap;">'
layout_replace = '<div class="edit-profile-layout">'
if layout_search in content:
    content = content.replace(layout_search, layout_replace)

# <div style="flex:0 0 120px;">
avatar_section_search = '<div style="flex:0 0 120px;">'
avatar_section_replace = '<div class="edit-profile-avatar-section">'
if avatar_section_search in content:
    content = content.replace(avatar_section_search, avatar_section_replace)

# <div style="flex:1; min-width:250px;">
form_section_search = '<div style="flex:1; min-width:250px;">'
form_section_replace = '<div class="edit-profile-form-section">'
if form_section_search in content:
    content = content.replace(form_section_search, form_section_replace)

# Add class to avatar image for targeting
content = re.sub(
    r'<img src="\$\{p.avatar\}" alt="\$\{p.name\}" style="width:120px; height:120px; border-radius:8px; object-fit:cover; box-shadow:0 4px 20px rgba\(0,0,0,0.5\);">',
    '<img src="${p.avatar}" alt="${p.name}" class="edit-profile-avatar-img" style="width:120px; height:120px; border-radius:8px; object-fit:cover; box-shadow:0 4px 20px rgba(0,0,0,0.5);">',
    content
)

# Update actions buttons container
actions_search = '<div style="display:flex; justify-content:space-between; align-items:center; margin-top:2rem; border-top:1px solid rgba(255,255,255,0.1); padding-top:1.5rem;">'
actions_replace = '<div class="edit-profile-actions" style="display:flex; justify-content:space-between; align-items:center; margin-top:2rem; border-top:1px solid rgba(255,255,255,0.1); padding-top:1.5rem;">'
if actions_search in content:
    content = content.replace(actions_search, actions_replace)


# 4. Update Service Worker Registration
new_sw_script = """<script>
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js')
                    .then(registration => {
                        console.log('SW registered', registration);
                        
                        // Check for updates
                        registration.addEventListener('updatefound', () => {
                            const newWorker = registration.installing;
                            newWorker.addEventListener('statechange', () => {
                                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                                    // New update available
                                    if(confirm("Nueva actualización disponible. ¿Recargar ahora?")) {
                                        window.location.reload();
                                    }
                                }
                            });
                        });
                        
                        // Check if there is already a waiting worker
                         if (registration.waiting) {
                              if(confirm("Nueva actualización disponible. ¿Recargar ahora?")) {
                                   registration.waiting.postMessage({ type: 'SKIP_WAITING' });
                                   window.location.reload();
                              }
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

content = re.sub(
    r'<script>\s+if \(\'serviceWorker\' in navigator\) \{[\s\S]+?\}\s+<\/script>',
    new_sw_script,
    content
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("index_pro.html updated successfully")
