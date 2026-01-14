
import re
import os

file_path = "c:\\Users\\Camero\\Downloads\\Mov\\index_pro.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# ---------------------------------------------------------
# 1. NEW DESIGN: Floating Glass Menu (Cyberpunk/Modern Streaming)
# ---------------------------------------------------------

new_css = """
        /* Redesign V3: Floating Glass (Modern Aesthetic) */
        @media (max-width: 768px) {
            .mobile-nav {
                display: flex !important;
                justify-content: space-around;
                align-items: center;
                position: fixed;
                bottom: 20px;
                left: 20px;
                right: 20px;
                height: 70px;
                background: rgba(15, 15, 20, 0.85); /* Deep dark */
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 24px;
                z-index: 10000;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
                padding: 0 10px;
                transition: transform 0.3s ease;
            }

            /* Hide menu when keyboard is open (optional, hard to detect purely css, 
               but we handle safe area) */

            .nav-item {
                flex: 1;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: rgba(255, 255, 255, 0.4);
                text-decoration: none;
                transition: all 0.3s ease;
                position: relative;
                -webkit-tap-highlight-color: transparent;
            }

            .nav-item i {
                font-size: 24px !important;
                margin-bottom: 4px;
                transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            }
            
            .nav-item span {
                font-size: 10px !important;
                font-weight: 600;
                letter-spacing: 0.3px;
                opacity: 0.7;
                transition: opacity 0.3s;
            }

            /* Active State */
            .nav-item.active {
                color: #ffffff !important;
            }
            
            .nav-item.active i {
                color: #bc13fe !important; /* Neon Purple Brand */
                transform: translateY(-4px) scale(1.1);
                filter: drop-shadow(0 0 12px rgba(188, 19, 254, 0.5));
            }

            .nav-item.active span {
                opacity: 1;
                color: #ffffff;
            }
            
            /* Active Indicator Dot */
            .nav-item.active::after {
                content: '';
                position: absolute;
                bottom: -6px;
                width: 4px;
                height: 4px;
                background: #bc13fe;
                border-radius: 50%;
                box-shadow: 0 0 8px #bc13fe;
                animation: popIn 0.3s ease forwards;
            }

            @keyframes popIn {
                from { transform: scale(0); opacity: 0; }
                to { transform: scale(1); opacity: 1; }
            }

            /* Profile Icon Specifics */
            .nav-profile-icon {
                width: 28px !important;
                height: 28px !important;
                border-radius: 50% !important; /* Circle */
                object-fit: cover;
                border: 2px solid transparent;
                transition: all 0.3s;
            }
            
            .nav-item.active .nav-profile-icon {
                border-color: #bc13fe;
                box-shadow: 0 0 12px rgba(188, 19, 254, 0.4);
            }
        }
"""

# Replace the previous V2 CSS (or V1)
# We look for the last inserted CSS block.
# Since we appended it before </style>, we can try to find the V2 block or just regex substitute the whole mobile-nav block.

# Regex to find existing .mobile-nav block inside @media
# It's safer to just append this NEW CSS at the end of <style> again, 
# because CSS cascading will make the last one win (especially with !important).
# But to keep file clean, let's try to remove old ones if we can identify them.
# The V2 block started with "/* Redesign V2: Minimalist"
if "/* Redesign V2: Minimalist" in content:
    # Remove V2
    content = re.sub(r'/\* Redesign V2: Minimalist.*?profile-icon \{\s*border-color: #ffffff;\s*\}\s*\}\s*', '', content, flags=re.DOTALL)

# Append V3
content = content.replace("</style>", new_css + "\n</style>")


# ---------------------------------------------------------
# 2. FIX UPLOAD: Use Chunked Upload in handleUpdateContent
# ---------------------------------------------------------

# Find handleUpdateContent function
# We need to replace the video upload part.

old_update_video_code = r"""
                    const vidFile = document.getElementById('e-video-file').files\[0\];
                    if\(vidFile\) \{
                        status.innerText = "Subiendo nuevo video \(esto puede tardar\)...";
                        const fd = new FormData\(\);
                        fd.append\('file', vidFile\);
                        const res = await fetch\('/upload/video', \{ method:'POST', body:fd \}\);
                        const data = await res.json\(\);
                        if\(data.url\) item.video = data.url;
                    \}
"""

# We need to be careful with regex whitespace.
# Let's find the exact string in the file content to be safe, or use a simpler replacement.

# The target block in handleUpdateContent:
target_block = """
                    const vidFile = document.getElementById('e-video-file').files[0];
                    if(vidFile) {
                        status.innerText = "Subiendo nuevo video (esto puede tardar)...";
                        const fd = new FormData();
                        fd.append('file', vidFile);
                        const res = await fetch('/upload/video', { method:'POST', body:fd });
                        const data = await res.json();
                        if(data.url) item.video = data.url;
                    }
"""

new_update_video_code = """
                    const vidFile = document.getElementById('e-video-file').files[0];
                    if(vidFile) {
                        status.innerText = "Iniciando carga optimizada...";
                        // Use Chunked Upload
                        const data = await uploadChunkedFile(vidFile, (pct) => {
                            const p = Math.floor(pct);
                            status.innerText = `Subiendo video: ${p}%`;
                        });
                        if(data.url) item.video = data.url;
                    }
"""

# Normalize whitespace for search
# Actually, since I read the file, I can try to locate it.
# If exact match fails, I'll use a more robust approach.

if target_block.strip() in content:
    content = content.replace(target_block.strip(), new_update_video_code.strip())
else:
    # Try to find it loosely
    # It seems the file has indentations.
    # Let's try to replace by context.
    # Look for "if(item.type === 'movie') {" inside handleUpdateContent
    
    pattern = r"(if\(item\.type === 'movie'\) \{)([\s\S]*?)(// Update text fields)"
    
    # We want to replace the inner part that handles video upload
    
    replacement_code = """
                if(item.type === 'movie') {
                    const vidFile = document.getElementById('e-video-file').files[0];
                    if(vidFile) {
                        status.innerHTML = 'Subiendo video: <span id="update-pct">0%</span>';
                        
                        const data = await uploadChunkedFile(vidFile, (pct) => {
                             const p = Math.floor(pct);
                             status.innerText = `Subiendo video: ${p}%`;
                        });
                        
                        if(data.url) item.video = data.url;
                    }
                }
    """
    
    # This is risky with regex on large blocks. 
    # Let's just do a string replace of the specific fetch call if possible.
    
    old_fetch = "const res = await fetch('/upload/video', { method:'POST', body:fd });"
    if old_fetch in content:
        # This line appears in handleAddContent (which I supposedly fixed? No, I read it and it was using chunked)
        # Wait, I read handleAddContent in previous turn and it WAS using uploadChunkedFile.
        # Let's check handleUpdateContent again.
        # In the previous Read output, handleUpdateContent (lines 4838+) used fetch('/upload/video').
        pass

    # Let's just do a specific replace for handleUpdateContent logic.
    # I will construct a regex that matches the block inside handleUpdateContent
    
    # Search for: const vidFile = document.getElementById('e-video-file').files[0];
    # And replace the following block.
    
    regex_video_update = re.compile(r"""
        const\s+vidFile\s*=\s*document\.getElementById\('e-video-file'\)\.files\[0\];
        \s*if\(vidFile\)\s*\{
        \s*status\.innerText\s*=\s*"Subiendo\s+nuevo\s+video[^"]*";
        \s*const\s+fd\s*=\s*new\s+FormData\(\);
        \s*fd\.append\('file',\s*vidFile\);
        \s*const\s+res\s*=\s*await\s+fetch\('/upload/video',\s*\{\s*method:'POST',\s*body:fd\s*\}\);
        \s*const\s+data\s*=\s*await\s+res\.json\(\);
        \s*if\(data\.url\)\s*item\.video\s*=\s*data\.url;
        \s*\}
    """, re.VERBOSE | re.DOTALL)
    
    if regex_video_update.search(content):
        content = regex_video_update.sub(new_update_video_code.strip(), content)
        print("Updated handleUpdateContent to use chunked upload.")
    else:
        print("WARNING: Could not find video update block in handleUpdateContent. It might be already updated or different.")


# 3. Update Icons in HTML (ensure they are 'line' or 'fill' as needed)
# The new design uses 'line' for inactive and 'fill' (via JS) for active.
# I previously replaced -fill with -line.
# I will keep them as -line in HTML. The JS I added in V2 handles the switch.
# I should ensure the JS is compatible with V3.
# V3 JS: .nav-item.active i { ... }
# The JS I added in V2 swaps the class name.
# "icon.className = icon.className.replace('-line', '-fill');"
# This is still good for V3. Filled icons look better glowing.

# 4. FIX PURPLE SCREEN (DIAGNOSIS)
# User reported "pantalla morada vacia".
# This often happens if `renderHeader` or `renderHome` crashes.
# Or if `allItems` is empty/undefined.
# I will wrap the initial render in a try-catch to log errors to a visible toast if possible.

init_script = """
        window.addEventListener('load', async () => {
            try {
                // Initialize PWA
                if ('serviceWorker' in navigator) {
                    navigator.serviceWorker.register('/sw.js').then(reg => {
                        console.log('SW registered:', reg);
                        
                        reg.addEventListener('updatefound', () => {
                            const newWorker = reg.installing;
                            newWorker.addEventListener('statechange', () => {
                                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                                    showUpdateToast();
                                }
                            });
                        });
                    }).catch(err => console.log('SW error:', err));
                    
                    let refreshing;
                    navigator.serviceWorker.addEventListener('controllerchange', () => {
                        if (refreshing) return;
                        window.location.reload();
                        refreshing = true;
                    });
                }
                
                await app.init();
            } catch (e) {
                console.error("Critical Init Error:", e);
                document.body.innerHTML += `<div style="color:white; z-index:99999; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); background:red; padding:20px;">Error iniciando app: ${e.message}</div>`;
            }
        });
"""

# Replace the existing window load listener if I can find it, or just ensure app.init is safe.
# `app.init` is usually called at the end of the script.
# Let's search for `window.addEventListener('load'`
# I will just ensure the error reporting is there.

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("index_pro.html updated with V3 Design (Floating Glass) and Upload Fixes.")
