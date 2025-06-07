import os
import uuid
import fitz  # PyMuPDF
import re
from werkzeug.utils import secure_filename
from app import app
import logging

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'pdf'

def generate_unique_filename(original_filename):
    """Generate a unique filename while preserving the extension."""
    name, ext = os.path.splitext(secure_filename(original_filename))
    unique_name = f"{uuid.uuid4().hex}_{name}{ext}"
    return unique_name

def extract_pdf_metadata(file_path):
    """Extract comprehensive metadata from PDF file using PyMuPDF."""
    from datetime import datetime
    
    metadata = {
        'title': '',
        'authors': '',
        'keywords': '',
        'abstract': '',
        'publication_year': None
    }
    
    try:
        doc = fitz.open(file_path)
        
        # Extract metadata from PDF properties
        pdf_metadata = doc.metadata
        if pdf_metadata:
            metadata['title'] = pdf_metadata.get('title', '').strip()
            metadata['authors'] = pdf_metadata.get('author', '').strip()
            metadata['keywords'] = pdf_metadata.get('keywords', '').strip()
        
        # Extract text from first few pages for analysis
        full_text = ""
        if doc.page_count > 0:
            for page_num in range(min(3, doc.page_count)):
                full_text += doc[page_num].get_text() + "\n"
        
        # Enhanced title extraction if missing
        if not metadata['title'] and full_text:
            lines = full_text.split('\n')
            for i, line in enumerate(lines[:15]):
                line = line.strip()
                if (10 < len(line) < 150 and 
                    not line.lower().startswith(('abstract', 'introduction', 'keywords', 'references')) and
                    not re.match(r'^\d+\.', line) and  # Not numbered section
                    re.search(r'[a-zA-Z]', line)):  # Contains letters
                    # Prefer lines that look like titles
                    if (line.isupper() or line.istitle() or 
                        any(word in line.lower() for word in ['analysis', 'study', 'research', 'approach', 'method'])):
                        metadata['title'] = line
                        break
                    elif not metadata['title'] and len(line) > 20:  # Fallback
                        metadata['title'] = line
        
        # Enhanced author extraction
        if not metadata['authors'] and full_text:
            # Look for author patterns in first page
            first_page_text = doc[0].get_text() if doc.page_count > 0 else ""
            
            # Common author patterns
            author_patterns = [
                r'(?i)(?:by|author[s]?[:\s]*)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]*\.?)*(?:\s*,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]*\.?)*)*)',
                r'^([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s*,\s*[A-Z][a-z]+\s+[A-Z][a-z]+)*)\s*$',
                r'([A-Z][a-z]+\s+[A-Z]\.\s*[A-Z][a-z]+(?:\s*,\s*[A-Z][a-z]+\s+[A-Z]\.\s*[A-Z][a-z]+)*)'
            ]
            
            for pattern in author_patterns:
                matches = re.findall(pattern, first_page_text, re.MULTILINE)
                if matches:
                    # Take the first reasonable match
                    for match in matches:
                        if len(match) > 5 and len(match) < 100:
                            metadata['authors'] = match.strip()
                            break
                    if metadata['authors']:
                        break
        
        # Extract abstract
        if full_text:
            abstract_patterns = [
                r'(?i)abstract[:\s]*\n?(.*?)(?:\n\s*(?:keywords|introduction|1\.|references))',
                r'(?i)abstract[:\s]*\n?(.*?)(?:\n\s*\n\s*[A-Z])',  # Until next section
            ]
            
            for pattern in abstract_patterns:
                match = re.search(pattern, full_text, re.DOTALL)
                if match:
                    abstract = re.sub(r'\s+', ' ', match.group(1)).strip()
                    if 50 < len(abstract) < 2000:  # Reasonable abstract length
                        metadata['abstract'] = abstract
                        break
        
        # Extract keywords if not in metadata
        if not metadata['keywords'] and full_text:
            keywords_patterns = [
                r'(?i)keywords?[:\s]*\n?(.*?)(?:\n\s*(?:introduction|1\.))',
                r'(?i)key\s*words?[:\s]*\n?(.*?)(?:\n\s*\n)'
            ]
            
            for pattern in keywords_patterns:
                match = re.search(pattern, full_text, re.DOTALL)
                if match:
                    keywords = re.sub(r'\s+', ' ', match.group(1)).strip()
                    if 10 < len(keywords) < 300:
                        metadata['keywords'] = keywords
                        break
        
        # Extract publication year
        current_year = datetime.now().year
        year_matches = re.findall(r'\b(19|20)\d{2}\b', full_text)
        if year_matches:
            years = [int(year) for year in year_matches if 1990 <= int(year) <= current_year]
            if years:
                # Prefer years closer to current year for recent research
                metadata['publication_year'] = max(years)
        
        doc.close()
        
        # Clean up extracted data
        for key, value in metadata.items():
            if isinstance(value, str):
                metadata[key] = re.sub(r'\s+', ' ', value).strip()
        
    except Exception as e:
        logging.error(f"Error extracting PDF metadata: {str(e)}")
    
    return metadata

def extract_keywords_from_text(text, max_keywords=10):
    """Simple keyword extraction from text."""
    if not text:
        return []
    
    # Simple approach: find common academic terms and frequent words
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'this', 'that', 'these', 'those', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can'}
    
    # Extract words (basic approach)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Count frequency
    word_freq = {}
    for word in words:
        if word not in stop_words and len(word) > 3:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Get most frequent words
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    keywords = [word for word, freq in sorted_words[:max_keywords] if freq > 1]
    
    return keywords

def save_uploaded_file(file, paper_id, department_name, year):
    """Save uploaded file to the appropriate directory."""
    if file and allowed_file(file.filename):
        filename = generate_unique_filename(file.filename)
        
        # Create directory structure: uploads/papers/year/department/
        year_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(year))
        dept_dir = os.path.join(year_dir, secure_filename(department_name))
        
        os.makedirs(dept_dir, exist_ok=True)
        
        file_path = os.path.join(dept_dir, filename)
        file.save(file_path)
        
        return filename, file_path
    
    return None, None

def get_file_size(file_path):
    """Get file size in bytes."""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0

def format_file_size(size_bytes):
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"
