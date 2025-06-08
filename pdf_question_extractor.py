import os
import re
import fitz  # PyMuPDF
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ExtractedQuestion:
    """Data class to hold extracted question information."""
    question_number: str
    question_text: str
    page_number: int
    section: str
    question_type: str
    marks: int = 1
    has_formula: bool = False
    has_diagram: bool = False
    metadata: Optional[Dict[str, Any]] = None

class PDFQuestionExtractor:
    """Enhanced PDF question extractor with improved text and structure analysis."""
    
    def __init__(self, pdf_path: str):
        """Initialize with path to PDF file."""
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.current_section = ""
        self.questions: List[ExtractedQuestion] = []
    
    def extract_questions(self) -> List[ExtractedQuestion]:
        """Extract all questions from the PDF."""
        print(f"Extracting questions from: {os.path.basename(self.pdf_path)}")
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            
            # Update current section if section header is found
            self._update_section(text)
            
            # Extract questions from this page
            self._extract_questions_from_page(text, page_num + 1)
        
        return self.questions
    
    def _update_section(self, text: str) -> None:
        """Update current section based on section headers in text."""
        section_match = re.search(r'Section [A-Z]: ([^\n]+)', text)
        if section_match:
            self.current_section = section_match.group(1).strip()
    
    def _extract_questions_from_page(self, text: str, page_num: int) -> None:
        """Extract questions from a single page's text."""
        # Split text into lines and process each potential question
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if line starts with a question number
            question_match = re.match(r'^(\d+)\.\s*(.*)', line)
            if question_match:
                question_num = question_match.group(1)
                question_text = [question_match.group(2)]
                
                # Collect continuation lines until next question or end
                i += 1
                while i < len(lines) and not re.match(r'^\d+\.\s+', lines[i]):
                    question_text.append(lines[i])
                    i += 1
                
                # Create question object
                full_text = ' '.join(question_text).strip()
                if full_text:  # Only add if we have actual question text
                    question = ExtractedQuestion(
                        question_number=question_num,
                        question_text=full_text,
                        page_number=page_num,
                        section=self.current_section,
                        question_type=self._determine_question_type(full_text),
                        marks=self._extract_marks(full_text),
                        has_formula=self._contains_formula(full_text),
                        has_diagram=self._contains_diagram_marker(full_text)
                    )
                    self.questions.append(question)
            else:
                i += 1
    
    def _determine_question_type(self, text: str) -> str:
        """Determine the type of question based on its content."""
        text_lower = text.lower()
        
        if re.search(r'\b(a|b|c|d|e)\)', text_lower):
            return "Multiple Choice"
        elif re.search(r'draw|diagram|label', text_lower):
            return "Diagram-based"
        elif 'explain' in text_lower or 'describe' in text_lower:
            return "Long Answer"
        elif 'calculate' in text_lower or 'solve' in text_lower:
            return "Problem Solving"
        else:
            return "Short Answer"
    
    def _extract_marks(self, text: str) -> int:
        """Extract marks from question text if specified."""
        marks_match = re.search(r'\((\d+)\s*marks?\)', text, re.IGNORECASE)
        if marks_match:
            return int(marks_match.group(1))
        return 1  # Default marks
    
    def _contains_formula(self, text: str) -> bool:
        """Check if question contains mathematical formulas."""
        # Simple check for common formula indicators
        formula_indicators = ['=', '^', '_', '\\frac', '\\sqrt', '\\sum']
        return any(indicator in text for indicator in formula_indicators)
    
    def _contains_diagram_marker(self, text: str) -> bool:
        """Check if question contains diagram-related markers."""
        return bool(re.search(r'diagram|figure|draw|label', text, re.IGNORECASE))
    
    def __del__(self):
        """Ensure the PDF document is properly closed."""
        if hasattr(self, 'doc'):
            self.doc.close()

# Helper function to integrate with existing code
def extract_questions_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """Extract questions from PDF and return as a list of dictionaries."""
    extractor = PDFQuestionExtractor(pdf_path)
    questions = extractor.extract_questions()
    
    # Convert to list of dictionaries for compatibility
    return [{
        'question_number': q.question_number,
        'question_text': q.question_text,
        'page_number': q.page_number,
        'section': q.section,
        'question_type': q.question_type,
        'marks': q.marks,
        'has_formula': q.has_formula,
        'has_diagram': q.has_diagram
    } for q in questions]
