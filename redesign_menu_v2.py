
import re

file_path = "c:\\Users\\Camero\\Downloads\\Mov\\index_pro.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update HTML Icons to "Line" versions for minimalist look
# Current: ri-home-4-fill, ri-tv-2-fill, ri-film-fill, ri-play-list-add-fill
# Target: ri-home-4-line, ri-tv-2-line, ri-film-line, ri-play-list-add-line

# We replace them globally or contextually.
# Since these classes are likely only used in the nav, global replace is probably safe enough, but let's be careful.
# Let's find the specific block if possible, or just replace the specific strings.

replacements = {
    "ri-home-4-fill": "ri-home-4-line",
    "ri-tv-2-fill": "ri-tv-2-line",
    "ri-film-fill": "ri-film-line",
    "ri-play-list-add-fill": "ri-play-list-add-line"
}

for old, new in replacements.items():
    content = content.replace(old, new)

# 2. Update CSS for Netflix/HBO Max Minimalist Style
# We need to overwrite the previous CSS we injected.
# The previous CSS was injected at the end of <style>.
# We can search for ".mobile-nav" and replace the block or append a new override with !important.
# Since we have full control, let's look for the block.

# Previous block might look like:
# .mobile-nav { ... background: rgba(10, 10, 12, 0.92); ... }

# New CSS:
# - Background: #121212 (Dark, almost black)
# - Border-top: 1px solid #333
# - Height: 60px
# - Icons: #8c8c8c (Inactive) -> #ffffff (Active)
# - Labels: font-size 10px, font-weight 500
# - Active Indicator: Just color change (Netflix style) or Top Border Line (YouTube style)
#   Netflix uses just color. HBO Max uses just color/bold.

new_css = """
        /* Redesign V2: Minimalist (Netflix/HBO Max Style) */
        @media (max-width: 768px) {
            .mobile-nav {
                display: flex !important;
                justify-content: space-around;
                align-items: center;
                background-color: #000000 !important; /* Pure black or very dark */
                backdrop-filter: none !important; /* Remove blur for solid look */
                -webkit-backdrop-filter: none !important;
                border-top: 1px solid #1f1f1f; /* Subtle separation */
                height: 55px; /* Compact */
                padding-bottom: env(safe-area-inset-bottom);
                z-index: 10000;
                box-shadow: none !important; /* No glow */
            }

            .nav-item {
                flex: 1;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: #808080 !important; /* Inactive Gray */
                text-decoration: none;
                transition: color 0.2s ease;
                padding: 5px 0;
                -webkit-tap-highlight-color: transparent;
            }

            .nav-item i {
                font-size: 22px !important; /* Slightly smaller icons */
                margin-bottom: 2px;
                transition: transform 0.1s;
            }
            
            .nav-item span {
                font-size: 9px !important; /* Very small labels */
                font-weight: 500;
                letter-spacing: 0.2px;
            }

            /* Active State */
            .nav-item.active {
                color: #ffffff !important; /* Pure White */
            }
            
            .nav-item.active i {
                /* transform: scale(1.1); Subtle pop */
                font-weight: bold; /* If font supports it, or use text-stroke */
                /* text-shadow: 0 0 10px rgba(255,255,255,0.3); Optional subtle glow */
            }

            /* Profile Icon Specifics */
            .nav-profile-icon {
                width: 24px !important;
                height: 24px !important;
                border-radius: 4px !important; /* Netflix uses square-ish avatars usually, but circle is fine. Let's do rounded square like Netflix. */
                object-fit: cover;
                border: 1px solid transparent;
            }
            
            .nav-item.active .nav-profile-icon {
                border-color: #ffffff;
            }

            /* Header Consistency */
            .header {
                background-color: rgba(0, 0, 0, 0.85) !important; /* Semi-transparent black */
                backdrop-filter: blur(10px) !important;
                border-bottom: none !important;
                /* Gradient overlay for readability over content */
                background: linear-gradient(180deg, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.6) 100%);
            }
        }
"""

# We'll append this new CSS to ensure it overrides everything.
content = content.replace("</style>", new_css + "\n</style>")

# 3. JavaScript to toggle icon fill on active (Optional but nice)
# Netflix icons are filled when active.
# We are using "line" icons by default.
# We can add a small JS snippet to toggle class "-line" to "-fill" when active.
# Let's find `renderHeader` or just add a global listener/observer?
# Easier: modify `renderHeader` or the click handlers.
# But `renderHeader` redraws the whole app usually? No, `renderHeader` is for the top header.
# The bottom nav is static in `index_pro.html`?
# Let's check.
# The bottom nav is hardcoded in the HTML I added?
# Yes, it's in the `<body>` usually.
# Let's check where the bottom nav HTML is.
# It is likely near the end of body.

# Search for `<nav class="mobile-nav">`
# I injected it previously.
# I want to add a script that updates the icons based on the active class.
# Or I can use CSS content replacement if I used a font that supports ligatures, but RemixIcon uses classes.
# I will add a script to handle the active class and icon switching.

js_icon_switcher = """
    <script>
        // Minimalist Menu Logic: Switch Line/Fill icons
        document.addEventListener('DOMContentLoaded', () => {
            const navItems = document.querySelectorAll('.nav-item');
            
            function updateIcons() {
                navItems.forEach(item => {
                    const icon = item.querySelector('i');
                    if(icon) {
                        if (item.classList.contains('active')) {
                            // Switch to fill
                            icon.className = icon.className.replace('-line', '-fill');
                        } else {
                            // Switch to line
                            icon.className = icon.className.replace('-fill', '-line');
                        }
                    }
                });
            }

            // Observer to watch for class changes (since app router might change active class)
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.attributeName === 'class') {
                        updateIcons();
                    }
                });
            });

            navItems.forEach(item => {
                observer.observe(item, { attributes: true });
                // Also add click listener for immediate feedback
                item.addEventListener('click', () => {
                    navItems.forEach(n => n.classList.remove('active'));
                    item.classList.add('active');
                });
            });
            
            // Initial check
            updateIcons();
        });
    </script>
"""

content = content.replace("</body>", js_icon_switcher + "\n</body>")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("index_pro.html updated with Netflix-style minimalist menu (Line/Fill icons, Dark UI).")
