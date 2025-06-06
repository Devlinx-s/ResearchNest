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
    """Extract metadata from PDF file using PyMuPDF."""
    metadata = {
        'title': None,
        'authors': None,
        'keywords': None,
        'abstract': None
    }
    
    try:
        doc = fitz.open(file_path)
        
        # Extract metadata from PDF properties
        pdf_metadata = doc.metadata
        if pdf_metadata:
            metadata['title'] = pdf_metadata.get('title', '').strip()
            metadata['authors'] = pdf_metadata.get('author', '').strip()
            metadata['keywords'] = pdf_metadata.get('keywords', '').strip()
        
        # If title is missing, try to extract from first page
        if not metadata['title'] and doc.page_count > 0:
            first_page = doc[0]
            text = first_page.get_text()
            
            # Look for title patterns
            lines = text.split('\n')
            for i, line in enumerate(lines[:10]):  # Check first 10 lines
                line = line.strip()
                if len(line) > 10 and len(line) < 200:  # Reasonable title length
                    # Check if it looks like a title (longer than usual, often in caps or title case)
                    if line.isupper() or line.istitle():
                        metadata['title'] = line
                        break
        
        # Extract abstract if available
        if doc.page_count > 0:
            full_text = ""
            for page_num in range(min(3, doc.page_count)):  # Check first 3 pages
                full_text += doc[page_num].get_text()
            
            # Look for abstract section
            abstract_match = re.search(r'abstract[:\s]+(.*?)(?:\n\s*\n|\n\s*keywords|\n\s*introduction)', 
                                     full_text, re.IGNORECASE | re.DOTALL)
            if abstract_match:
                abstract = abstract_match.group(1).strip()
                if len(abstract) > 50:  # Reasonable abstract length
                    metadata['abstract'] = abstract[:1000]  # Limit length
        
        doc.close()
        
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
