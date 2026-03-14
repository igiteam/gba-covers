#!/usr/bin/env python3
"""
GBA ROM Cover Matcher with Default Cover
Matches GBA ROM files to cover images and generates gba_matched.json and games.js
Uses gba_default_cover.png when no cover is found
"""

import json
import os
import re
from pathlib import Path
from urllib.parse import unquote
import logging
from datetime import datetime
import argparse
from collections import defaultdict

class GBACompleteMatcher:
    def __init__(self, roms_dir="gba_roms", covers_dir="gba_covers", default_cover="gba_default_cover.png"):
        """
        Initialize the matcher
        
        Args:
            roms_dir: Directory containing GBA ROM files
            covers_dir: Directory containing cover images
            default_cover: Default cover filename to use when no cover is found
        """
        self.roms_dir = Path(roms_dir)
        self.covers_dir = Path(covers_dir)
        self.default_cover = default_cover
        
        # Setup logging
        self.setup_logging()
        
        # Data storage
        self.roms = []
        self.covers = []
        self.matches = []
        self.unmatched_roms = []
        self.unmatched_covers = []
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def clean_filename_for_matching(self, filename):
        """
        Clean filename aggressively for matching
        
        Args:
            filename: Filename to clean
        
        Returns:
            Cleaned filename for matching
        """
        # Remove file extension
        name = os.path.splitext(filename)[0]
        
        # Decode URL encoding
        name = unquote(name)
        
        # Remove country/region tags and other common patterns
        patterns_to_remove = [
            r'\s*\([^)]*\)',  # Remove parentheses content
            r'\s*\[[^\]]*\]',  # Remove bracket content
            r'\s*\.\.\.',      # Remove ellipsis
            r'\s*-\s*(USA|Europe|Japan|World|Rev\d*|Beta\d*)',  # Remove region tags
            r'\s*v\d+\.\d+',  # Remove version numbers
            r'\s*\d{4}',      # Remove years
            r'[^\w\s]',       # Remove all special characters except spaces
            r'\s+',           # Replace multiple spaces with single
        ]
        
        for pattern in patterns_to_remove:
            name = re.sub(pattern, ' ', name, flags=re.IGNORECASE)
        
        # Remove common words
        common_words = [
            'the', 'and', 'for', 'with', 'from', 'that', 'this',
            'game', 'advance', 'gba', 'edition', 'version', 'special',
            'deluxe', 'ultimate', 'collection', 'pack', 'bundle'
        ]
        
        words = name.lower().split()
        filtered_words = [w for w in words if w not in common_words and len(w) > 1]
        name = ' '.join(filtered_words)
        
        return name.strip()
    
    def clean_filename_for_display(self, filename):
        """
        Clean filename for display (keeps nice formatting)
        
        Args:
            filename: Filename to clean
        
        Returns:
            Cleaned filename for display
        """
        # Remove file extension
        name = os.path.splitext(filename)[0]
        
        # Decode URL encoding
        name = unquote(name)
        
        # Remove file extensions and clean up
        name = re.sub(r'\.(gba|gb|gbc|zip)$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def generate_binary_id(self, title):
        """
        Generate binary ID from game title (no numbers at beginning)
        
        Args:
            title: Game title
        
        Returns:
            Binary ID for JavaScript variable
        """
        # Remove leading numbers and special characters
        clean_title = re.sub(r'^\d+[\s\-]*', '', title)
        
        # Replace spaces and special characters with underscores
        binary_id = re.sub(r'[^\w]+', '_', clean_title.lower())
        
        # Remove leading/trailing underscores
        binary_id = binary_id.strip('_')
        
        # If binary_id is empty after removing numbers (e.g., "007"), use fallback
        if not binary_id:
            # Use the original title but remove special chars
            binary_id = re.sub(r'[^\w]+', '_', title.lower()).strip('_')
        
        return binary_id
    
    def generate_title_name_in_binaries(self, title):
        """
        Generate title name in binaries format
        
        Args:
            title: Game title
        
        Returns:
            Formatted title for binaries
        """
        # Remove leading numbers
        clean_title = re.sub(r'^\d+[\s\-]*', '', title)
        
        # Remove special characters except spaces
        clean_title = re.sub(r'[^\w\s]', '', clean_title)
        
        # Replace spaces with underscores and make lowercase
        binary_name = clean_title.lower().replace(' ', '_')
        
        return binary_name
    
    def generate_html_player_link(self, binary_id, title):
        """
        Generate HTML player link
        
        Args:
            binary_id: Binary ID for the game
            title: Game title
        
        Returns:
            HTML link string
        """
        return f'<a class="playerLink" href="./player#{binary_id}">{title}</a><br>'
    
    def generate_html_player_link_with_img(self, binary_id, title, cover_url):
        """
        Generate HTML player link with image
        
        Args:
            binary_id: Binary ID for the game
            title: Game title
            cover_url: Cover image URL
        
        Returns:
            HTML link with image string
        """
        return f'<a class="playerLink" href="./player#{binary_id}"><img src="{cover_url}" style="width:100%"></a><br>'
    
    def get_cover_url(self, cover_filename):
        """
        Get cover URL - uses default cover if filename is None or empty
        
        Args:
            cover_filename: Cover filename or None
        
        Returns:
            Cover URL string
        """
        if not cover_filename:
            return f"https://raw.githubusercontent.com/igiteam/gba.js/main/gba_covers/{self.default_cover}"
        return f"https://raw.githubusercontent.com/igiteam/gba.js/main/gba_covers/{cover_filename}"
    
    def simple_string_similarity(self, str1, str2):
        """
        Simple string similarity calculation (faster than fuzzywuzzy)
        
        Args:
            str1: First string
            str2: Second string
        
        Returns:
            Similarity score (0-100)
        """
        if not str1 or not str2:
            return 0
        
        str1 = str1.lower()
        str2 = str2.lower()
        
        # Check for exact match
        if str1 == str2:
            return 100
        
        # Check for substring match
        if str1 in str2 or str2 in str1:
            return 90
        
        # Split into words
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return 0
        
        # Calculate word overlap
        common_words = words1.intersection(words2)
        all_words = words1.union(words2)
        
        if not all_words:
            return 0
        
        # Score based on word overlap
        score = (len(common_words) / len(all_words)) * 100
        
        return score
    
    def load_roms(self):
        """Load GBA ROM files from directory"""
        if not self.roms_dir.exists():
            self.logger.error(f"ROMs directory not found: {self.roms_dir}")
            return False
        
        # Find all GBA ROM files
        rom_extensions = ['.gba', '.gb', '.gbc']
        self.roms = []
        
        self.logger.info("Loading ROM files...")
        for ext in rom_extensions:
            rom_files = list(self.roms_dir.glob(f"*{ext}"))
            rom_files.extend(list(self.roms_dir.glob(f"*{ext.upper()}")))
            
            for rom_path in rom_files:
                rom = {
                    'path': str(rom_path),
                    'filename': rom_path.name,
                    'cleaned_for_matching': self.clean_filename_for_matching(rom_path.name),
                    'cleaned_for_display': self.clean_filename_for_display(rom_path.name),
                    'extension': ext
                }
                self.roms.append(rom)
            
            if rom_files:
                self.logger.info(f"  Found {len(rom_files)} {ext} files")
        
        self.logger.info(f"Total ROM files: {len(self.roms)}")
        return True
    
    def load_covers(self):
        """Load cover images from directory"""
        if not self.covers_dir.exists():
            self.logger.error(f"Covers directory not found: {self.covers_dir}")
            return False
        
        # Find all image files
        self.covers = []
        self.logger.info("Loading cover images...")
        
        for ext in ['.png', '.jpg', '.jpeg', '.gif']:
            cover_files = list(self.covers_dir.glob(f"*{ext}"))
            cover_files.extend(list(self.covers_dir.glob(f"*{ext.upper()}")))
            
            for cover_path in cover_files:
                cover = {
                    'path': str(cover_path),
                    'filename': cover_path.name,
                    'cleaned_for_matching': self.clean_filename_for_matching(cover_path.name),
                    'cleaned_for_display': self.clean_filename_for_display(cover_path.name)
                }
                self.covers.append(cover)
            
            if cover_files:
                self.logger.info(f"  Found {len(cover_files)} {ext} files")
        
        # Check if default cover exists
        default_cover_path = self.covers_dir / self.default_cover
        if not default_cover_path.exists():
            self.logger.warning(f"Default cover not found: {default_cover_path}")
            self.logger.warning("Please create a default cover image named 'gba_default_cover.png'")
        
        self.logger.info(f"Total cover images: {len(self.covers)}")
        return True
    
    def match_roms_to_covers_optimized(self, threshold=70):
        """
        Optimized matching algorithm
        
        Args:
            threshold: Minimum match score (0-100)
        """
        self.logger.info(f"Matching {len(self.roms)} ROMs to {len(self.covers)} covers...")
        self.logger.info("This may take a while for large collections...")
        
        # Create lookup dictionaries for faster matching
        cover_dict = {}
        for i, cover in enumerate(self.covers):
            key = cover['cleaned_for_matching']
            if key not in cover_dict:
                cover_dict[key] = []
            cover_dict[key].append((i, cover))
        
        # Also create a dictionary of cover words for partial matching
        cover_words_dict = defaultdict(list)
        for i, cover in enumerate(self.covers):
            words = cover['cleaned_for_matching'].split()
            for word in words:
                if len(word) > 3:  # Only index significant words
                    cover_words_dict[word].append(i)
        
        self.matches = []
        matched_cover_indices = set()
        
        # First pass: Try exact or near-exact matches
        self.logger.info("First pass: Exact and near-exact matches...")
        for rom_idx, rom in enumerate(self.roms):
            if rom_idx % 100 == 0:
                self.logger.info(f"  Processed {rom_idx}/{len(self.roms)} ROMs...")
            
            rom_key = rom['cleaned_for_matching']
            
            # Try exact match first
            if rom_key in cover_dict:
                for cover_idx, cover in cover_dict[rom_key]:
                    if cover_idx not in matched_cover_indices:
                        self._add_match(rom, cover, 100, "exact")
                        matched_cover_indices.add(cover_idx)
                        break
                continue
            
            # Try word-based matching
            best_match = None
            best_score = 0
            
            # Get significant words from ROM name
            rom_words = [w for w in rom_key.split() if len(w) > 3]
            
            if rom_words:
                # Find covers that share significant words
                candidate_covers = set()
                for word in rom_words:
                    if word in cover_words_dict:
                        candidate_covers.update(cover_words_dict[word])
                
                # Score candidates
                for cover_idx in candidate_covers:
                    if cover_idx in matched_cover_indices:
                        continue
                    
                    cover = self.covers[cover_idx]
                    score = self.simple_string_similarity(rom_key, cover['cleaned_for_matching'])
                    
                    if score > best_score and score >= threshold:
                        best_score = score
                        best_match = (cover_idx, cover)
            
            if best_match:
                cover_idx, cover = best_match
                self._add_match(rom, cover, best_score, "word-based")
                matched_cover_indices.add(cover_idx)
        
        # Second pass for remaining ROMs (slower but more thorough)
        self.logger.info(f"Second pass: Remaining {len(self.roms) - len(self.matches)} ROMs...")
        remaining_roms = [r for r in self.roms if r not in [m['rom'] for m in self.matches]]
        remaining_covers = [c for i, c in enumerate(self.covers) if i not in matched_cover_indices]
        
        # Only do second pass if we have a manageable number
        if len(remaining_roms) * len(remaining_covers) < 100000:  # Limit to 100k comparisons
            for rom_idx, rom in enumerate(remaining_roms):
                if rom_idx % 50 == 0:
                    self.logger.info(f"  Processed {rom_idx}/{len(remaining_roms)} remaining ROMs...")
                
                best_match = None
                best_score = 0
                
                for cover_idx, cover in enumerate(remaining_covers):
                    score = self.simple_string_similarity(
                        rom['cleaned_for_matching'], 
                        cover['cleaned_for_matching']
                    )
                    
                    if score > best_score and score >= threshold:
                        best_score = score
                        best_match = (cover_idx, cover)
                
                if best_match:
                    cover_idx, cover = best_match
                    self._add_match(rom, cover, best_score, "second-pass")
                    # Remove matched cover
                    remaining_covers.pop(cover_idx)
        
        # Track unmatched items
        self.unmatched_roms = [r for r in self.roms if r not in [m['rom'] for m in self.matches]]
        self.unmatched_covers = [c for i, c in enumerate(self.covers) if i not in matched_cover_indices]
        
        self.logger.info(f"Matched: {len(self.matches)} ROMs")
        self.logger.info(f"Unmatched ROMs: {len(self.unmatched_roms)}")
        self.logger.info(f"Unmatched covers: {len(self.unmatched_covers)}")
    
    def _add_match(self, rom, cover, score, match_type):
        """Helper to add a match to the matches list"""
        title = rom['cleaned_for_display'].title()
        binary_id = self.generate_binary_id(title)
        title_name_in_binaries = self.generate_title_name_in_binaries(title)
        
        # Generate cover URL
        cover_url = self.get_cover_url(cover['filename'])
        
        match_info = {
            'rom': rom,
            'cover': cover,
            'score': score,
            'match_type': match_type,
            'title': title,
            'binary_id': binary_id,
            'title_name_in_binaries': title_name_in_binaries,
            'cover_url': cover_url,
            'gba_list': self.generate_html_player_link(binary_id, title),
            'gba_list_img': self.generate_html_player_link_with_img(binary_id, title, cover_url)
        }
        self.matches.append(match_info)
    
    def _add_unmatched_rom(self, rom):
        """Helper to add an unmatched ROM with default cover"""
        title = rom['cleaned_for_display'].title()
        binary_id = self.generate_binary_id(title)
        title_name_in_binaries = self.generate_title_name_in_binaries(title)
        
        # Use default cover for unmatched ROMs
        cover_url = self.get_cover_url(self.default_cover)
        
        # Create dummy cover entry
        dummy_cover = {
            'path': str(self.covers_dir / self.default_cover),
            'filename': self.default_cover,
            'cleaned_for_matching': 'default cover',
            'cleaned_for_display': 'Default Cover'
        }
        
        match_info = {
            'rom': rom,
            'cover': dummy_cover,
            'score': 0,
            'match_type': 'default',
            'title': title,
            'binary_id': binary_id,
            'title_name_in_binaries': title_name_in_binaries,
            'cover_url': cover_url,
            'gba_list': self.generate_html_player_link(binary_id, title),
            'gba_list_img': self.generate_html_player_link_with_img(binary_id, title, cover_url)
        }
        self.matches.append(match_info)
    
    def add_default_cover_to_unmatched(self):
        """Add default cover to all unmatched ROMs"""
        self.logger.info(f"Adding default cover to {len(self.unmatched_roms)} unmatched ROMs...")
        
        for rom in self.unmatched_roms:
            self._add_unmatched_rom(rom)
        
        self.logger.info(f"Total games (including default covers): {len(self.matches)}")
    
    def save_gba_matched_json(self, output_file="gba_matched.json"):
        """Save matched data to gba_matched.json"""
        output_data = []
        
        for match in self.matches:
            game_data = {
                'cover_url': match['cover_url'],
                'title': match['title'],
                'title_name_in_binaries': match['title_name_in_binaries'],
                'gba_list': match['gba_list'],
                'gba_list_img': match['gba_list_img'],
                'binary_id': match['binary_id'],
                'rom_filename': match['rom']['filename'],
                'cover_filename': match['cover']['filename'],
                'match_score': match['score'],
                'match_type': match['match_type'],
                'has_cover': match['match_type'] != 'default'
            }
            output_data.append(game_data)
        
        # Sort by title
        output_data.sort(key=lambda x: x['title'].lower())
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"gba_matched.json saved with {len(output_data)} games")
            
            # Count games with actual covers
            games_with_covers = sum(1 for game in output_data if game['has_cover'])
            games_with_default = len(output_data) - games_with_covers
            self.logger.info(f"Games with actual covers: {games_with_covers}")
            self.logger.info(f"Games with default cover: {games_with_default}")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to save gba_matched.json: {e}")
            return False
    
    def save_games_js(self, output_file="games.js"):
        """Save JavaScript games object"""
        js_content = """// Auto-generated games mapping
// DO NOT EDIT MANUALLY - Generated by match_gba.py
// Games with default cover marked with "// DEFAULT"

var games = {
  // "binary-id": "Game Name",
"""
        
        # Sort matches by binary_id
        sorted_matches = sorted(self.matches, key=lambda x: x['binary_id'])
        
        for i, match in enumerate(sorted_matches):
            # Format the line
            line = f'  {match["binary_id"]}: "{match["title"]}",'
            
            # Add comment for games with default cover
            if match['match_type'] == 'default':
                line += '  // DEFAULT'
            
            # Add to JS content
            js_content += line
            
            # Add newline (except for last item)
            if i < len(sorted_matches) - 1:
                js_content += "\n"
        
        # Close the object
        js_content += "\n};\n"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(js_content)
            
            # Count games with actual covers
            games_with_covers = sum(1 for match in sorted_matches if match['match_type'] != 'default')
            self.logger.info(f"games.js saved with {len(sorted_matches)} games")
            self.logger.info(f"  Games with covers: {games_with_covers}")
            self.logger.info(f"  Games with default: {len(sorted_matches) - games_with_covers}")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to save games.js: {e}")
            return False
    
    def save_unmatched_report(self, output_file="unmatched_report.json"):
        """Save report of unmatched ROMs and covers"""
        report = {
            'metadata': {
                'generated_date': datetime.now().isoformat(),
                'total_roms': len(self.roms),
                'total_covers': len(self.covers),
                'matched_count': len([m for m in self.matches if m['match_type'] != 'default']),
                'games_with_default_cover': len([m for m in self.matches if m['match_type'] == 'default']),
                'unmatched_covers_count': len(self.unmatched_covers)
            },
            'unmatched_roms': [],
            'unmatched_covers': [],
            'low_score_matches': []
        }
        
        # Add unmatched ROMs (limited to 100)
        for unmatched in self.unmatched_roms[:100]:
            report['unmatched_roms'].append({
                'rom': unmatched['filename'],
                'cleaned_name': unmatched['cleaned_for_display'],
                'cleaned_for_matching': unmatched['cleaned_for_matching']
            })
        
        # Add unmatched covers (limited to 100)
        for cover in self.unmatched_covers[:100]:
            report['unmatched_covers'].append({
                'cover': cover['filename'],
                'cleaned_name': cover['cleaned_for_display'],
                'cleaned_for_matching': cover['cleaned_for_matching']
            })
        
        # Add low score matches (score < 80)
        for match in self.matches:
            if match['score'] < 80 and match['match_type'] != 'default':
                report['low_score_matches'].append({
                    'rom': match['rom']['filename'],
                    'cover': match['cover']['filename'],
                    'score': match['score'],
                    'title': match['title'],
                    'match_type': match['match_type']
                })
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Unmatched report saved to {output_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save unmatched report: {e}")
            return False
    
    def print_summary(self):
        """Print matching summary"""
        print("\n" + "="*60)
        print("GBA MATCHING SUMMARY")
        print("="*60)
        print(f"Total ROM files:           {len(self.roms)}")
        print(f"Total cover images:        {len(self.covers)}")
        
        games_with_covers = len([m for m in self.matches if m['match_type'] != 'default'])
        games_with_default = len([m for m in self.matches if m['match_type'] == 'default'])
        
        print(f"Games with actual covers:  {games_with_covers} ({games_with_covers/len(self.roms)*100:.1f}%)")
        print(f"Games with default cover:  {games_with_default} ({games_with_default/len(self.roms)*100:.1f}%)")
        print(f"Unmatched covers:          {len(self.unmatched_covers)}")
        
        if self.matches:
            print("\nMatch types:")
            match_types = defaultdict(int)
            for match in self.matches:
                match_types[match['match_type']] += 1
            
            for match_type, count in match_types.items():
                print(f"  {match_type}: {count}")
            
            print("\nSample games with covers (first 10):")
            print("-"*60)
            games_with_covers = [m for m in self.matches if m['match_type'] != 'default']
            for i, match in enumerate(games_with_covers[:10]):
                rom_name = match['rom']['filename'][:30]
                cover_name = match['cover']['filename'][:30]
                binary_id = match['binary_id'][:20]
                score = match['score']
                print(f"{i+1:2}. {rom_name:30} -> {cover_name:30}")
                print(f"     ID: {binary_id:20} Score: {score}%")
                print()
            
            print("\nSample games with default cover (first 10):")
            print("-"*60)
            games_with_default = [m for m in self.matches if m['match_type'] == 'default']
            for i, match in enumerate(games_with_default[:10]):
                rom_name = match['rom']['filename'][:50]
                print(f"{i+1:2}. {rom_name}")
    
    def run(self, threshold=70, add_default_to_unmatched=True):
        """Run the complete matching process"""
        self.logger.info("Starting GBA ROM to Cover matching process...")
        
        # Load data
        if not self.load_roms():
            return False
        
        if not self.load_covers():
            return False
        
        # Match ROMs to covers (optimized)
        self.match_roms_to_covers_optimized(threshold)
        
        # Add default cover to unmatched ROMs if requested
        if add_default_to_unmatched:
            self.add_default_cover_to_unmatched()
        
        # Save results
        self.save_gba_matched_json()
        self.save_games_js()
        self.save_unmatched_report()
        
        # Print summary
        self.print_summary()
        
        return True

def main():
    parser = argparse.ArgumentParser(
        description='Match GBA ROM files to cover images and generate required outputs'
    )
    parser.add_argument(
        '--roms-dir', 
        default='gba_roms',
        help='Directory containing GBA ROM files (default: gba_roms)'
    )
    parser.add_argument(
        '--covers-dir', 
        default='gba_covers',
        help='Directory containing cover images (default: gba_covers)'
    )
    parser.add_argument(
        '--default-cover',
        default='gba_default_cover.png',
        help='Default cover filename (default: gba_default_cover.png)'
    )
    parser.add_argument(
        '--threshold', 
        type=int, 
        default=70,
        help='Minimum match score percentage (default: 70)'
    )
    parser.add_argument(
        '--no-default-cover',
        action='store_true',
        help='Do not add default cover to unmatched games'
    )
    
    args = parser.parse_args()
    
    # Run matcher
    matcher = GBACompleteMatcher(
        roms_dir=args.roms_dir,
        covers_dir=args.covers_dir,
        default_cover=args.default_cover
    )
    
    success = matcher.run(
        threshold=args.threshold,
        add_default_to_unmatched=not args.no_default_cover
    )
    
    if success:
        print("\n" + "="*60)
        print("✓ MATCHING COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("Generated files:")
        print("  • gba_matched.json - Complete matched data (all games)")
        print("  • games.js - JavaScript games object (all games)")
        print("  • unmatched_report.json - Report of unmatched items")
        
        if not args.no_default_cover:
            print("\nNote: All games now have covers!")
            print("  - Games with real covers: Matched to actual images")
            print("  - Games without covers: Use default cover")
            print("\nMake sure to upload 'gba_default_cover.png' to GitHub")
        else:
            print("\nNote: Only games with matched covers are included")
            print("  Run without --no-default-cover to include all games with default cover")
    else:
        print("\n✗ Matching failed!")

if __name__ == "__main__":
    main()