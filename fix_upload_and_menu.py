
import os
import re

file_path = "c:\\Users\\Camero\\Downloads\\Mov\\index_pro.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Inject uploadFileWithProgress helper function before handleAddContent
# We'll put it before "async function handleAddContent() {"
helper_js = """
        function uploadFileWithProgress(url, fd, onProgress) {
            return new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();
                xhr.open('POST', url, true);
                
                xhr.upload.onprogress = (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        if(onProgress) onProgress(percentComplete);
                    }
                };
                
                xhr.onload = () => {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        try {
                            const data = JSON.parse(xhr.responseText);
                            resolve(data);
                        } catch (e) {
                            reject(new Error("Invalid JSON response"));
                        }
                    } else {
                        reject(new Error("Upload failed: " + xhr.statusText));
                    }
                };
                
                xhr.onerror = () => reject(new Error("Network error"));
                xhr.send(fd);
            });
        }

"""

if "function uploadFileWithProgress" not in content:
    content = content.replace("async function handleAddContent() {", helper_js + "        async function handleAddContent() {")

# 2. Replace the fetch logic in handleAddContent with uploadFileWithProgress
# Target: status.innerText = "Subiendo video (esto puede tardar)..."; ... const res = await fetch('/upload/video', { method:'POST', body:fd }); ... if(data.url) videoUrl = data.url;

# We need to use regex carefully because of whitespace
# We will match the specific block for video upload
old_video_upload_block = r"""status\.innerText\s*=\s*"Subiendo video \(esto puede tardar\)\.\.\.";\s*const fd\s*=\s*new FormData\(\);\s*fd\.append\('file',\s*vidFile\);\s*const res\s*=\s*await fetch\('/upload/video',\s*\{\s*method:'POST',\s*body:fd\s*\}\);\s*const data\s*=\s*await res\.json\(\);\s*if\(data\.url\)\s*videoUrl\s*=\s*data\.url;"""

new_video_upload_block = """status.innerHTML = 'Subiendo video: <span id="upload-pct">0%</span><div style="width:100%; height:4px; background:#333; margin-top:5px; border-radius:2px;"><div id="upload-bar" style="width:0%; height:100%; background:var(--color-brand-primary); transition:width 0.2s;"></div></div>';
                        const fd = new FormData();
                        fd.append('file', vidFile);
                        
                        const data = await uploadFileWithProgress('/upload/video', fd, (pct) => {
                            const p = Math.floor(pct);
                            const pctEl = document.getElementById('upload-pct');
                            const barEl = document.getElementById('upload-bar');
                            if(pctEl) pctEl.innerText = p + '%';
                            if(barEl) barEl.style.width = p + '%';
                            if(p >= 100) status.innerText = "Procesando video...";
                        });
                        
                        if(data.url) videoUrl = data.url;"""

# Normalize spaces for regex matching isn't perfect, let's try strict replacement if exact string matches, else regex
# The code read previously:
# status.innerText = "Subiendo video (esto puede tardar)...";
#                         const fd = new FormData();
#                         fd.append('file', vidFile);
#                         const res = await fetch('/upload/video', { method:'POST', body:fd });
#                         const data = await res.json();
#                         if(data.url) videoUrl = data.url;

target_str = """status.innerText = "Subiendo video (esto puede tardar)...";
                        const fd = new FormData();
                        fd.append('file', vidFile);
                        const res = await fetch('/upload/video', { method:'POST', body:fd });
                        const data = await res.json();
                        if(data.url) videoUrl = data.url;"""

if target_str in content:
    content = content.replace(target_str, new_video_upload_block)
else:
    # Fallback: Try to replace line by line if indentation differs
    # But let's look at the Read output again.
    # Lines 4389-4394
    pass 

# 3. Fix Mobile Menu CSS
# We will append a style block at the end of head to override anything
css_fix = """
    <style>
        /* FORCE MOBILE NAV VISIBILITY */
        @media (max-width: 768px) {
            .mobile-nav {
                display: flex !important;
                z-index: 99999 !important; /* Ensure it's on top */
                bottom: 0 !important;
                position: fixed !important;
                background: rgba(11, 12, 15, 0.98) !important;
                backdrop-filter: blur(15px) !important;
                height: 60px !important;
                padding-bottom: env(safe-area-inset-bottom, 0px) !important;
                box-shadow: 0 -5px 20px rgba(0,0,0,0.5) !important;
            }
            
            /* Hide when in profile gate */
            body.in-profile-gate .mobile-nav {
                display: none !important;
            }
            
            /* Ensure content doesn't get hidden behind nav */
            #main-view {
                padding-bottom: 80px !important;
            }
        }
    </style>
</head>
"""

content = content.replace("</head>", css_fix)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("index_pro.html updated with upload progress bar and mobile menu fixes.")
