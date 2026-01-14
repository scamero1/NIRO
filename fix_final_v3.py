
import re

file_path = "c:\\Users\\Camero\\Downloads\\Mov\\index_pro.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix HTML Class Mismatch for Mobile Nav
# Replace class="mobile-nav-item" with class="nav-item"
content = content.replace('class="mobile-nav-item"', 'class="nav-item"')

# 2. Fix Episode Upload to use Chunked Upload
# Target handleEpUpload function
# Look for: const res = await fetch('/upload/video', { method:'POST', body:fd });

# Context: handleEpUpload function
# We replace the block handling video upload

old_ep_upload = """
                // Upload Video
                const fd = new FormData();
                fd.append('file', vidFile);
                const res = await fetch('/upload/video', { method:'POST', body:fd });
                const data = await res.json();
                
                if(data.url) {
"""

new_ep_upload = """
                // Upload Video (Chunked)
                status.innerText = "Subiendo video del episodio (0%)...";
                const data = await uploadChunkedFile(vidFile, (pct) => {
                    status.innerText = `Subiendo video: ${Math.floor(pct)}%`;
                });
                
                if(data.url) {
"""

# Try simple replace first (ignoring whitespace differences if possible, but exact string match is safer)
# Since I read the file, I can try to find the exact string from previous Read output or use regex.

# Regex for the fetch line in handleEpUpload
regex_ep = re.compile(r"""
    //\s*Upload\s*Video\s*
    \s*const\s+fd\s*=\s*new\s+FormData\(\);
    \s*fd\.append\('file',\s*vidFile\);
    \s*const\s+res\s*=\s*await\s+fetch\('/upload/video',\s*\{\s*method:'POST',\s*body:fd\s*\}\);
    \s*const\s+data\s*=\s*await\s+res\.json\(\);
""", re.VERBOSE | re.DOTALL)

if regex_ep.search(content):
    content = regex_ep.sub("""
                // Upload Video (Chunked)
                status.innerText = "Subiendo video (0%)...";
                const data = await uploadChunkedFile(vidFile, (pct) => {
                    status.innerText = `Subiendo video: ${Math.floor(pct)}%`;
                });
    """, content)
    print("Fixed handleEpUpload to use chunked upload.")
else:
    print("WARNING: Could not find handleEpUpload video block.")

# 3. Ensure Mobile Nav IDs are correct for active state logic
# My JS logic:
# item.addEventListener('click', () => { navItems.forEach(n => n.classList.remove('active')); item.classList.add('active'); });
# This is generic, it works.
# But app.router() re-renders or changes view. Does it reset the nav?
# The nav is static in index_pro.html (outside app container? No, it's at the end of body).
# So it stays.
# But if I reload, I need to set the active state based on current hash/view.
# I'll add a small helper to highlight the correct nav item on load.

js_active_state = """
            // Set initial active state based on function called or URL
            // Since we use app.router('home'), we can hook into that or just default to home.
            // Let's highlight 'nav-home' by default.
            document.getElementById('nav-home').classList.add('active');
"""

# Append this to the DOMContentLoaded listener I added earlier
# Search for "document.addEventListener('DOMContentLoaded', () => {"
if "document.addEventListener('DOMContentLoaded', () => {" in content:
    content = content.replace("document.addEventListener('DOMContentLoaded', () => {", "document.addEventListener('DOMContentLoaded', () => {\n" + js_active_state)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("index_pro.html fixed (Nav classes, Ep Upload, Active State).")
