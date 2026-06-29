import re

def sanitize_for_tts(text: str, aggressive: bool = False) -> dict:
    """
    Cleans text for safe TTS generation.
    Returns a dict with cleaned text and stats.
    """
    if not text:
        return {"cleaned": "", "stats": {}}
        
    original_len = len(text)
    
    # Remove hidden zero-width chars and control chars
    text = re.sub(r'[\u200b\u200c\u200d\u200e\u200f\ufeff]', '', text)
    
    # Normalize smart quotes to standard quotes
    text = text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
    text = text.replace('«', '"').replace('»', '"')
    
    # Normalize strange punctuation
    text = text.replace('…', '...')
    text = text.replace('—', ' - ')
    text = text.replace('–', ' - ')
    
    # Remove emojis if aggressive
    if aggressive:
        # Very simple emoji and symbol strip
        text = text.encode('ascii', 'ignore').decode('ascii')
        # Only keep letters, numbers, standard punctuation
        text = re.sub(r'[^a-zA-Z0-9\s.,!?:\'";\-()[\]/]', '', text)
    else:
        # Strip specific dangerous SSML chars if not using SSML
        text = text.replace('<', '').replace('>', '')
    
    # Replace multiple spaces
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Replace multiple empty lines with a single empty line
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    cleaned_len = len(text)
    
    return {
        "cleaned": text.strip(),
        "stats": {
            "original_length": original_len,
            "cleaned_length": cleaned_len,
            "removed_characters": original_len - cleaned_len
        }
    }
