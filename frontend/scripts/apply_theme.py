import os
import re

TARGET_DIR = r"d:\TTS\frontend\src"

REPLACEMENTS = {
    r'\bbg-slate-900\b(?!/)': 'bg-white dark:bg-slate-900',
    r'\bbg-slate-900/': 'bg-white/90 dark:bg-slate-900/',
    r'\bbg-slate-950/': 'bg-slate-50/90 dark:bg-slate-950/',
    r'\bbg-slate-950\b': 'bg-slate-50 dark:bg-slate-950',
    r'\btext-white\b': 'text-slate-900 dark:text-white',
    r'\btext-slate-400\b': 'text-slate-600 dark:text-slate-400',
    r'\btext-slate-300\b': 'text-slate-700 dark:text-slate-300',
    r'\btext-slate-500\b': 'text-slate-500 dark:text-slate-500',
    r'\bborder-slate-800/': 'border-slate-200 dark:border-slate-800/',
    r'\bborder-slate-800\b': 'border-slate-200 dark:border-slate-800',
    r'\bborder-slate-700/': 'border-slate-300 dark:border-slate-700/',
    r'\bborder-slate-700\b': 'border-slate-300 dark:border-slate-700',
    r'\bbg-black/40\b': 'bg-slate-100 dark:bg-black/40',
    r'\bbg-slate-800\b': 'bg-slate-100 dark:bg-slate-800',
    r'\bbg-slate-800/': 'bg-slate-100 dark:bg-slate-800/',
    r'\bbg-slate-700/': 'bg-slate-200 dark:bg-slate-700/',
    r'\bhover:bg-slate-800\b': 'hover:bg-slate-100 dark:hover:bg-slate-800',
    r'\bhover:bg-slate-700\b': 'hover:bg-slate-200 dark:hover:bg-slate-700',
    r'\bhover:text-white\b': 'hover:text-slate-900 dark:hover:text-white',
}

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    original = content
    for pattern, replacement in REPLACEMENTS.items():
        # Only replace if not already containing dark:
        # Actually a simple way is just replace, but we don't want to double replace
        # We can use regex to ensure it doesn't already have a dark: counterpart nearby, but it's simpler:
        # Just replace, and if there are duplicates like bg-white dark:bg-white dark:bg-slate-900, we'll fix it later.
        pass

    # A better approach: split into className="...", and only replace inside strings.
    # Actually, simple string replace is fine for tailwind classes if we are careful.
    
    # Let's do a more robust approach.
    for pattern, replacement in REPLACEMENTS.items():
        # negative lookbehind to ensure we don't replace if it's already dark:
        regex = r'(?<!dark:)' + pattern
        content = re.sub(regex, replacement, content)
        
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {os.path.basename(filepath)}")

for root, _, files in os.walk(TARGET_DIR):
    for file in files:
        if file.endswith('.jsx'):
            process_file(os.path.join(root, file))

print("Done.")
