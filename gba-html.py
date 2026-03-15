#!/usr/bin/env python3
"""
gba_games_js Games Grid Generator
Creates an Xemu-style grid website from your gba_games_js games JSON
Shows title as text overlay when image fails to load
Uses cartridge code for image filenames
"""

import json
import os

# Configuration
JSON_FILE = "gba_games_js.json"
OUTPUT_HTML = "gba_games_js.html"
PLACEHOLDER_IMAGE = "https://raw.githubusercontent.com/igiteam/gba-covers/refs/heads/master/gba-cover-default.png"
RAW_BASE_URL = "https://raw.githubusercontent.com/igiteam/gba-covers/refs/heads/main/covers"

def load_games_data():
    """Load games from JSON file and match with cover images"""
    if not os.path.exists(JSON_FILE):
        print(f"Error: {JSON_FILE} not found!")
        return None
    
    LABELS_FOLDER = "covers"
    if not os.path.exists(LABELS_FOLDER):
        print(f"Error: '{LABELS_FOLDER}' folder not found!")
        return None
    
    # Load JSON data
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        games = json.load(f)
    
    print(f"Loaded {len(games)} games from JSON")
    
    # Get all cover files
    cover_files = {}
    for f in os.listdir(LABELS_FOLDER):
        if f.endswith('.png'):
            # Store cover by filename for easy lookup
            cover_files[f] = os.path.join(LABELS_FOLDER, f)
    
    print(f"Found {len(cover_files)} cover images in {LABELS_FOLDER}/")
    
    # Default cover URL to filter out
    DEFAULT_COVER_URL = "https://raw.githubusercontent.com/igiteam/gba.js/main/gba_covers/gba_default_cover.png"
    
    # Match games with covers
    matched_games = []
    matched_count = 0
    no_cover_count = 0
    default_cover_count = 0
    
    for game in games:
        # Skip if no title
        if 'title' not in game or not game['title']:
            continue
        
        # Check if game has default cover URL
        if 'cover_url' in game and game['cover_url'] == DEFAULT_COVER_URL:
            default_cover_count += 1
            print(f"⏭️ Skipping (default cover): {game['title']}")
            continue  # Skip this game entirely
        
        # Check if this game has a cover
        if 'cover_filename' in game and game['cover_filename'] in cover_files:
            # Game already has cover_filename in JSON
            game['has_local_cover'] = True
            game['cover_file_exists'] = True
            matched_games.append(game)
            matched_count += 1
            print(f"✓ Has cover: {game['title']} -> {game['cover_filename']}")
        else:
            # Try to find cover by other means
            cover_found = False
            
            # Try to find cover by binary_id
            if 'binary_id' in game and game['binary_id']:
                # Look for cover containing the binary_id
                for cover_file in cover_files.keys():
                    if game['binary_id'].lower() in cover_file.lower():
                        game['cover_filename'] = cover_file
                        game['has_local_cover'] = True
                        game['cover_file_exists'] = True
                        matched_games.append(game)
                        matched_count += 1
                        cover_found = True
                        print(f"✓ Matched by binary_id: {game['title']} -> {cover_file}")
                        break
            
            # Try to find cover by title
            if not cover_found and 'title' in game:
                # Clean title for matching
                title_clean = game['title'].replace(' - ', ' ').replace(':', '').replace('-', ' ')
                title_parts = title_clean.lower().split()
                
                for cover_file in cover_files.keys():
                    cover_lower = cover_file.lower()
                    # Check if all significant title words appear in cover filename
                    matches = 0
                    for part in title_parts:
                        if len(part) > 3 and part in cover_lower:  # Only check words longer than 3 chars
                            matches += 1
                    
                    if matches >= len(title_parts) * 0.5:  # At least 50% of words match
                        game['cover_filename'] = cover_file
                        game['has_local_cover'] = True
                        game['cover_file_exists'] = True
                        matched_games.append(game)
                        matched_count += 1
                        cover_found = True
                        print(f"✓ Matched by title: {game['title']} -> {cover_file}")
                        break
            
            if not cover_found:
                # No cover found for this game
                no_cover_count += 1
                print(f"✗ No cover match: {game['title']}")
    
    print(f"\n📊 Cover Matching Results:")
    print(f"   - Total games in JSON: {len(games)}")
    print(f"   - Games with default cover (skipped): {default_cover_count}")
    print(f"   - Games with matching covers: {matched_count}")
    print(f"   - Games without covers (skipped): {no_cover_count}")
    print(f"   - Total games included: {matched_count}")
    
    if matched_count == 0:
        print("\n❌ No matches found!")
        print("   Please check your covers folder and JSON data.")
        print("   Expected cover filenames like: '007 - Everything or Nothing (USA, Europe) (En,Fr,De).png'")
    
    return matched_games

def get_cartridge_image_url(game):
    """Get local cover image path"""
    if game.get('cover_file_exists', False) and 'cover_filename' in game:
        # Use local cover file
        return f"{RAW_BASE_URL}/{game['cover_filename']}"
    
    # Fallback to remote placeholder
    return PLACEHOLDER_IMAGE


def generate_html(games):
    """Generate the grid website HTML"""
    
    games.sort(key=lambda x: x['title_name_in_binaries'].lower())
    
    total_games = len(games)
    with_covers = 0
    
    html = f"""<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GBA Games Collection</title>

  <link rel="icon" href="https://cdn.sdappnet.cloud/rtx/images/gba-icon.png" type="image/png">
  <link rel="apple-touch-icon" href="https://cdn.sdappnet.cloud/rtx/images/gba-icon.png" sizes="180x180">
  <link rel="icon" type="image/png" href="https://cdn.sdappnet.cloud/rtx/images/gba-icon.png" sizes="192x192">
  <link rel="icon" type="image/png" href="https://cdn.sdappnet.cloud/rtx/images/gba-icon.png" sizes="512x512">
  <meta itemprop="name" content="GBA Games Collection">
  <meta property="og:title" content="GBA Games Collection">
  <meta property="og:url" content="">
  <meta property="og:type" content="website">
  <meta name="twitter:title" content="GBA Games Collection">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="apple-touch-icon" href="https://cdn.sdappnet.cloud/rtx/images/gba-icon.png" sizes="180x180">

  <style>
    body {{
      background-color: #1a1a1a;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      margin: 4px 20px;
      padding: 0;
    }}

    #results {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 10px;
      max-width: 1400px;
      margin: 0 auto;
      background-color: #1a1a1a;
      margin-top: 4px;
      z-index: 1000;
    }}

    .title-card {{
      background: #2a2a2a;
      border-radius: 8px;
      overflow: hidden;
      transition: transform 0.2s;
    }}

    .title-card:hover {{
      transform: scale(1.05);
      z-index: 10;
    }}

    .title-card-container {{
      width: 100%;
      position: relative;
    }}

    .title-card-image-container {{
      width: 100%;
      aspect-ratio: 1/1;
      overflow: hidden;
      position: relative;
      background-color: #1a1a1a;
    }}

    .title-card-image-container img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: opacity 0.3s;
    }}

    .title-card-image-container .fallback-title {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 10px;
      box-sizing: border-box;
      background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
      color: #888;
      font-size: 14px;
      font-weight: 500;
      word-break: break-word;
      border: 1px solid #333;
    }}

    .fill-color-Playable {{
      background-color: #42991b !important;
      color: white !important;
      font-weight: 700 !important;
    }}

    .card-body {{
      flex: 1 1 auto;
      min-height: 1px;
      padding: 0.5rem 1.25rem !important;
    }}

    .text-center {{
      text-align: center !important;
    }}

    .py-1 {{
      padding-top: 0.25rem !important;
      padding-bottom: 0.25rem !important;
    }}

    .my-0 {{
      margin-top: 0 !important;
      margin-bottom: 0 !important;
    }}

    small {{
      font-size: 80%;
    }}

    a {{
      text-decoration: none;
      color: inherit;
    }}

    /* Search container */
    #saved-search-container {{
      position: sticky;
      z-index: 10000;
      margin-left: auto;
      margin-right: auto;
      margin: 8px 0px;
    }}

    #saved-search-input {{
      padding: 10px;
      width: calc(100% - 20px);
      border: 1px solid #555;
      border-radius: 4px;
      background: #444;
      color: white;
      flex: 1;
    }}

    .search-row {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .icon {{
      width: 34px;
      height: 34px;
      border-radius: 4px;
      object-fit: cover;
    }}

    #saved-search-input::placeholder {{
      color: #aaa;
    }}

    #saved-results-count {{
      color: white;
      font-size: 14px;
      text-align: center;
      margin-top: 5px;
    }}

    /* Hide cards with failed images */
    .title-card.image-failed {{
      display: none !important;
    }}

    /* Hide cards when searching */
    .title-card-link.hidden-game {{
      display: none !important;
    }}
  </style>
</head>

<body>
  <div id="saved-search-container">
    <div class="search-row">
      <img src="https://cdn.sdappnet.cloud/rtx/images/gba-icon.png" class="icon" alt="gba logo">
      <input type="text" id="saved-search-input" placeholder="Search games...">
      <a href="https://www.aliexpress.com/item/1005007539923790.html" target="_blank">
        <img src="https://cdn.sdappnet.cloud/rtx/images/gba-icon-2.png" class="icon" alt="gba Controller">
      </a>
      <a href="https://cdn.sdappnet.cloud/rtx/gba_magazine.html" target="_blank">
        <img src="https://cdn.sdappnet.cloud/rtx/images/gba-magazine.png" class="icon" alt="gba Magazine">
      </a>
    </div>
    <div id="saved-results-count"></div>
  </div>

  <div class="row" id="results">
"""

    for game in games:
        title = game['title_name_in_binaries'].replace('"', '&quot;')
        
        cover_url = get_cartridge_image_url(game)
        has_cartridge_code = 'cartridge_code' in game and game['cartridge_code']
        
        if has_cartridge_code:
            with_covers += 1
        
        cartridge_code = game.get('cartridge_code', '')
        
        html += f"""
    <div class="col px-1 mb-4 title-card" data-title-name="{title}" data-cartridge="{cartridge_code}">
      <a target="_blank" rel="norefferer" href="https://github.com/igiteam/gba-covers">
        <div class="mx-auto title-card-container">
          <div class="title-card-image-container" style="position: relative;">
            <img
              src="{cover_url}"
              loading="lazy"
              title="{title}"
              data-cartridge="{cartridge_code}"
              onload="this.nextElementSibling.style.display='none';"
              onerror="this.closest('.title-card').classList.add('image-failed');">
            <div class="fallback-title" style="display: flex; position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(transparent, rgba(0,0,0,0.9)); color: white; padding: 15px 8px 8px 8px; font-size: 12px; text-align: center; font-weight: 500;">{title}</div>
          </div>
          <div class="fill-color-Playable card-body text-center py-1 my-0"><small><strong>Play</strong></small></div>
        </div>
      </a>
    </div>"""

    html += f"""
  </div>

  <script>
    // Store games data for search
    let gamesData = [];
    
    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {{
        // Collect all game titles
        document.querySelectorAll('.title-card').forEach(card => {{
            const title = card.getAttribute('data-title-name');
            if (title) {{
                gamesData.push({{
                    element: card,
                    title: title.toLowerCase()
                }});
            }}
        }});
        
        // Convert title cards to links
        wrapCardsWithLinks();
    }});

    // Convert title cards to links for search functionality
    function wrapCardsWithLinks() {{
        document.querySelectorAll('.title-card').forEach(card => {{
            // Skip if card image failed
            if (card.classList.contains('image-failed')) return;

            const title = card.getAttribute('data-title-name');
            
            const existingInnerLink = card.querySelector('a');
            if (existingInnerLink) {{
                while (existingInnerLink.firstChild) {{
                    card.insertBefore(existingInnerLink.firstChild, existingInnerLink);
                }}
                existingInnerLink.remove();
            }}

            let url_path = '';
            if (title) {{
                url_path = title
                    .toLowerCase()
                    .replace(/[^\\w\\s-]/g, '')
                    .replace(/\\s+/g, '-')
                    .replace(/-+/g, '-')
                    .replace(/^-|-$/g, '');
            }}

            if (url_path) {{
                const link = document.createElement('a');
                link.href = 'https://meyt.netlify.app/search/' + url_path + ' gba';
                link.className = 'title-card-link';
                link.rel = 'noopener noreferrer';
                link.target = '_blank';
                
                if (title) link.setAttribute('data-title-name', title);

                card.parentNode.insertBefore(link, card);
                link.appendChild(card);
            }}
        }});
    }}

    // Search functionality
    document.getElementById('saved-search-input').addEventListener('input', function (e) {{
        const searchTerm = e.target.value.toLowerCase().trim();
        const searchTermWithUnderscores = searchTerm.replace(/\s+/g, '_');
        const cards = document.querySelectorAll('.title-card');
        let count = 0;

        cards.forEach(card => {{
            const title = card.getAttribute('data-title-name') || '';
            
            if (searchTermWithUnderscores === '') {{
                // Show all cards when search is empty
                card.style.display = '';
                card.classList.remove('hidden-game');
                count++;
            }} else if (title.toLowerCase().includes(searchTermWithUnderscores)) {{
                // Show matching cards
                card.style.display = '';
                card.classList.remove('hidden-game');
                count++;
            }} else {{
                // Hide non-matching cards
                card.style.display = 'none';
                card.classList.add('hidden-game');
            }}
        }});

        // Also handle the wrapped links if they exist
        document.querySelectorAll('.title-card-link').forEach(link => {{
            if (searchTermWithUnderscores === '') {{
                link.classList.remove('hidden-game');
            }} else {{
                const card = link.querySelector('.title-card');
                if (card && card.style.display === 'none') {{
                    link.classList.add('hidden-game');
                }} else {{
                    link.classList.remove('hidden-game');
                }}
            }}
        }});

        document.getElementById('saved-results-count').textContent =
            searchTermWithUnderscores ? `Found ${{count}} game${{count !== 1 ? 's' : ''}}` : '';
    }});

    // Keyboard shortcut
    document.addEventListener('keydown', function(e) {{
        if (e.key === '/' && !document.getElementById('saved-search-input').matches(':focus')) {{
            e.preventDefault();
            document.getElementById('saved-search-input').focus();
        }}
    }});

    // Initial hide of any images that already failed
    document.querySelectorAll('.title-card img').forEach(img => {{
        if (img.complete && img.naturalHeight === 0) {{
            img.closest('.title-card').classList.add('image-failed');
        }}
    }});

    // Trigger initial search to show all cards
    setTimeout(() => {{
        document.getElementById('saved-search-input').dispatchEvent(new Event('input'));
    }}, 100);
  </script>
</body>

</html>
"""

    return html, with_covers

def main():
    print("GBA Games Grid Generator")
    print("=" * 50)
    
    games = load_games_data()
    if not games:
        return
    
    print("Generating grid website with cartridge code images...")
    html_content, with_covers = generate_html(games)
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Website generated: {OUTPUT_HTML}")
    print(f"\nStatistics:")
    print(f"   - Total games: {len(games)}")
    print(f"   - Games with cartridge codes: {with_covers}")
    print(f"\nImage URL format: {RAW_BASE_URL}/[cartridge_code].png")

if __name__ == "__main__":
    main()