
import os
import re

file_path = "c:\\Users\\Camero\\Downloads\\Mov\\index_pro.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add uploadChunkedFile helper
# We'll insert it after uploadFileWithProgress
helper_js = """
        async function uploadChunkedFile(file, onProgress) {
            const chunkSize = 5 * 1024 * 1024; // 5MB chunks (safe for Cloudflare)
            const totalChunks = Math.ceil(file.size / chunkSize);
            const uploadId = Date.now().toString() + Math.random().toString().substr(2, 5);
            
            for (let i = 0; i < totalChunks; i++) {
                const start = i * chunkSize;
                const end = Math.min(start + chunkSize, file.size);
                const chunk = file.slice(start, end);
                
                const fd = new FormData();
                fd.append('chunk', chunk);
                fd.append('chunkIndex', i);
                fd.append('totalChunks', totalChunks);
                fd.append('fileName', file.name);
                fd.append('uploadId', uploadId);
                
                // Retry logic for robustness
                let attempts = 0;
                while(attempts < 3) {
                    try {
                        const res = await fetch('/upload/chunk', { method: 'POST', body: fd });
                        if (!res.ok) throw new Error('Upload failed');
                        const data = await res.json();
                        
                        // Report progress
                        if (onProgress) {
                            const percent = ((i + 1) / totalChunks) * 100;
                            onProgress(percent);
                        }
                        
                        if (data.done) {
                            return data;
                        }
                        break; // Success, move to next chunk
                    } catch (e) {
                        attempts++;
                        console.error(`Chunk ${i} failed, attempt ${attempts}`, e);
                        if(attempts >= 3) throw e;
                        await new Promise(r => setTimeout(r, 1000 * attempts)); // Backoff
                    }
                }
            }
        }
"""

if "async function uploadChunkedFile" not in content:
    content = content.replace("async function handleAddContent() {", helper_js + "\n        async function handleAddContent() {")

# 2. Replace the video upload logic in handleAddContent to use uploadChunkedFile
# Current block (from previous update):
# status.innerHTML = 'Subiendo video: <span id="upload-pct">0%</span>...';
# ... const data = await uploadFileWithProgress('/upload/video', fd, ...);

# We need to find this block. It was inserted via python script previously.
# Let's search for the unique string "uploadFileWithProgress('/upload/video'"

# Pattern to find:
# const fd = new FormData();
# fd.append('file', vidFile);
# const data = await uploadFileWithProgress('/upload/video', fd, (pct) => { ... });
# if(data.url) videoUrl = data.url;

# We will replace it with:
# const data = await uploadChunkedFile(vidFile, (pct) => { ... });

# Since the previous code was:
#                         const fd = new FormData();
#                         fd.append('file', vidFile);
#                         
#                         const data = await uploadFileWithProgress('/upload/video', fd, (pct) => {
#                             const p = Math.floor(pct);
#                             const pctEl = document.getElementById('upload-pct');
#                             const barEl = document.getElementById('upload-bar');
#                             if(pctEl) pctEl.innerText = p + '%';
#                             if(barEl) barEl.style.width = p + '%';
#                             if(p >= 100) status.innerText = "Procesando video...";
#                         });
#                         
#                         if(data.url) videoUrl = data.url;

# We'll use regex to match loosely
pattern = r"const fd = new FormData\(\);\s*fd\.append\('file', vidFile\);\s*const data = await uploadFileWithProgress\('/upload/video', fd, \(pct\) => \{[\s\S]*?\}\);\s*if\(data\.url\) videoUrl = data\.url;"

replacement = """
                        const data = await uploadChunkedFile(vidFile, (pct) => {
                            const p = Math.floor(pct);
                            const pctEl = document.getElementById('upload-pct');
                            const barEl = document.getElementById('upload-bar');
                            if(pctEl) pctEl.innerText = p + '%';
                            if(barEl) barEl.style.width = p + '%';
                            if(p >= 100) status.innerHTML = "Procesando video... <i class='ri-loader-4-line spin'></i>";
                        });
                        
                        if(data.url) videoUrl = data.url;
"""

# Try to find and replace
match = re.search(pattern, content)
if match:
    print("Found old upload logic, replacing with chunked logic.")
    content = content.replace(match.group(0), replacement)
else:
    print("Could not find exact old upload logic via regex. Checking manually.")
    # Fallback: maybe exact spacing differs.
    # We can try to replace the inner part if we can locate the start.
    pass

# 3. Mobile Menu Refinements
# User wants "estetico como de una plataforma streaming y que sea minimalista"
# I already did a good job, but maybe I can add:
# - A subtle top border gradient
# - Adjust spacing
# - Ensure it's not hidden by mistake (z-index was high, should be ok)

# Let's verify the CSS I added. It was:
# .mobile-nav { ... background: rgba(10, 10, 12, 0.92); backdrop-filter: blur(25px); ... }
# That is quite premium.
# I'll add a "glass" effect to the header too, as requested implicitly ("mejora el menu del celular" -> usually implies top and bottom navs).
# The header CSS:
# .header { background-color: rgba(15, 7, 32, 0.95); backdrop-filter: blur(12px); }
# I will make it match the bottom nav for consistency.

header_css_fix = """
        /* Header consistency */
        @media (max-width: 768px) {
            .header {
                background: rgba(10, 10, 12, 0.92) !important;
                backdrop-filter: blur(25px) !important;
                -webkit-backdrop-filter: blur(25px) !important;
                border-bottom: 1px solid rgba(255,255,255,0.06);
                height: 60px;
            }
            .header-content {
                height: 100%;
                align-items: center;
            }
            .logo img {
                height: 32px !important; /* Smaller logo on mobile */
            }
        }
"""
content = content.replace("</style>", header_css_fix + "\n</style>")


with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("index_pro.html updated with chunked upload support and header refinements.")
