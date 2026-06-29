import re

def split_text_into_chunks(text: str, max_size: int = 1200) -> list[str]:
    """
    Professionally splits long text into chunks, preferring to break at:
    1. Paragraphs (\n\n or \n)
    2. Sentences (. ! ?)
    3. Clauses (, ; :)
    4. Words (space)
    """
    if not text:
        return []
        
    # Standardize newlines
    text = text.replace('\r\n', '\n')
    
    chunks = []
    current_chunk = ""
    
    # 1. Split by paragraphs first
    paragraphs = re.split(r'(\n+)', text)
    
    def add_to_chunk(segment: str):
        nonlocal current_chunk
        if len(current_chunk) + len(segment) <= max_size:
            current_chunk += segment
        else:
            # If segment itself is larger than max_size, we need to break it further by sentences
            if len(segment) > max_size:
                # Support Arabic sentence boundaries as well as English
                sentences = re.split(r'(?<=[.!?。؟])\s+', segment)
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) <= max_size:
                        current_chunk += " " + sentence if current_chunk and not current_chunk.endswith(('\n', ' ')) else sentence
                    else:
                        if current_chunk.strip():
                            chunks.append(current_chunk.strip())
                        
                        # If a single sentence is STILL > max_size, break by commas/clauses
                        if len(sentence) > max_size:
                            clauses = re.split(r'(?<=[,;:—،؛])\s+', sentence)
                            current_chunk = ""
                            for clause in clauses:
                                if len(current_chunk) + len(clause) <= max_size:
                                    current_chunk += " " + clause if current_chunk else clause
                                else:
                                    if current_chunk.strip():
                                        chunks.append(current_chunk.strip())
                                    
                                    # Absolute worst case: break by words
                                    if len(clause) > max_size:
                                        words = clause.split(' ')
                                        current_chunk = ""
                                        for word in words:
                                            if len(current_chunk) + len(word) + 1 <= max_size:
                                                current_chunk += " " + word if current_chunk else word
                                            else:
                                                if current_chunk.strip():
                                                    chunks.append(current_chunk.strip())
                                                current_chunk = word
                                    else:
                                        current_chunk = clause
                        else:
                            current_chunk = sentence
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = segment

    for p in paragraphs:
        if not p.strip() and not current_chunk:
            continue
        add_to_chunk(p)
        
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
        
    # Clean up any purely empty chunks
    return [c for c in chunks if c.strip()]
