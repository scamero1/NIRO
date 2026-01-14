
import re

file_path = "c:\\Users\\Camero\\Downloads\\Mov\\index_pro.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Define the new CSS
new_css = """
        /* Modern Mobile Nav - Minimalist Streaming Style */
        .mobile-nav {
            display: none;
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 70px; /* Comfortable touch height */
            background: rgba(10, 10, 12, 0.92); /* Deep elegant dark */
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            border-top: 1px solid rgba(255,255,255,0.06);
            z-index: 9999;
            justify-content: space-evenly;
            align-items: center;
            padding-bottom: env(safe-area-inset-bottom, 5px);
            box-shadow: 0 -15px 40px rgba(0,0,0,0.6);
        }
        
        .mobile-nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #7a7a7a; /* Muted minimalist gray */
            transition: all 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
            width: 65px;
            height: 100%;
            cursor: pointer;
            -webkit-tap-highlight-color: transparent;
            position: relative;
        }

        .mobile-nav-item i {
            font-size: 24px;
            margin-bottom: 3px;
            transition: all 0.25s ease;
        }
        
        .mobile-nav-item span {
            font-size: 9px;
            font-weight: 500;
            letter-spacing: 0.3px;
            opacity: 1;
            transition: opacity 0.2s;
        }
        
        .mobile-nav-item img {
            width: 24px; 
            height: 24px; 
            border-radius: 6px; /* Softer radius */
            object-fit: cover;
            border: 2px solid transparent;
            transition: all 0.25s ease;
        }

        /* Active State */
        .mobile-nav-item.active {
            color: #ffffff;
        }
        
        .mobile-nav-item.active i {
            color: var(--color-brand-primary);
            transform: translateY(-2px);
            filter: drop-shadow(0 0 10px rgba(139, 92, 246, 0.4)); /* Subtle neon glow */
        }
        
        .mobile-nav-item.active img {
            border-color: var(--color-brand-primary);
            transform: scale(1.05);
            box-shadow: 0 0 10px rgba(139, 92, 246, 0.3);
        }

        .mobile-nav-item.active span {
            font-weight: 600;
            color: white;
        }

        /* Click Ripple Effect (simulated via scale) */
        .mobile-nav-item:active i, .mobile-nav-item:active img {
            transform: scale(0.9);
        }
        
        /* Media Query updates */
        @media (max-width: 768px) {
            .mobile-nav { display: flex !important; }
            body.in-profile-gate .mobile-nav { display: none !important; }
            /* Adjust bottom padding for main view so content isn't hidden */
            #main-view { padding-bottom: 85px !important; }
        }
"""

# 2. Replace the old CSS block
# We'll use regex to find the block starting with .mobile-nav { ... } up to the media queries
# The previous Grep showed lines 638-658 approx.
# Let's try to match the exact previous block structure to replace it safely.
# Previous content:
#         .mobile-nav {
#             display: none;
#             position: fixed;
#             bottom: 0;
# ...
#         .mobile-nav-item.active { color: white; }

# Since regex replacement of multi-line large blocks can be tricky with exact spacing,
# I will identify start and end markers.
start_marker = "/* Mobile Nav */"
end_marker = ".mobile-nav-item.active { color: white; }"

if start_marker in content and end_marker in content:
    # We will construct a regex that captures everything between these
    pattern = re.compile(r"/\* Mobile Nav \*/.*?" + re.escape(end_marker), re.DOTALL)
    
    # Check if we can find it
    match = pattern.search(content)
    if match:
        print("Found CSS block, replacing...")
        content = content.replace(match.group(0), new_css)
    else:
        print("Regex match failed, trying fallback string replacement.")
        # Fallback: manual string construction of what we think is there from previous read
        # It's risky. Let's try to find the specific .mobile-nav { definition
        pass
else:
    # If markers not found (maybe changed), append to end of head style
    print("Markers not found, appending CSS to head.")
    content = content.replace("</style>", new_css + "\n</style>")

# 3. Update Icons to be more minimalist/filled (Remix Icons)
# Home: ri-home-5-line (inactive) -> ri-home-5-fill (active) logic is handled by JS usually,
# but here we have static HTML. Let's stick to consistent icons.
# Current: ri-home-fill, ri-tv-line, ri-movie-2-line, ri-list-check
# Better set: ri-home-4-line / ri-home-4-fill
# Let's update the static HTML part
if '<i class="ri-home-fill"></i>' in content:
    content = content.replace('<i class="ri-home-fill"></i>', '<i class="ri-home-4-fill"></i>')

if '<i class="ri-tv-line"></i>' in content:
    content = content.replace('<i class="ri-tv-line"></i>', '<i class="ri-tv-2-fill"></i>') # TV

if '<i class="ri-movie-2-line"></i>' in content:
    content = content.replace('<i class="ri-movie-2-line"></i>', '<i class="ri-film-fill"></i>') # Movie

if '<i class="ri-list-check"></i>' in content:
    content = content.replace('<i class="ri-list-check"></i>', '<i class="ri-play-list-add-fill"></i>') # My List

# 4. Remove the inline styles in JS that might conflict?
# In app.renderHeader, we saw: document.getElementById('main-header').style.display = 'none'; etc.
# That is fine.

# 5. Fix the "upload_progress" style if it was messy (from previous turn)
# I added it via string replacement, it should be fine.

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Mobile menu design updated to minimalist streaming style.")
