import os
import re
import json
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from app import app, db
from models import Question, QuestionDocument, Unit, Topic, Subject

# Set up NLTK data path
import nltk
import shutil

# Define NLTK data paths
nltk_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nltk_data')
os.makedirs(nltk_data_path, exist_ok=True)

# Add our custom path to the beginning of the NLTK data path
nltk.data.path.insert(0, nltk_data_path)

# Function to manually load NLTK data
def load_nltk_data():
    # Check if we have the required data files
    punkt_path = os.path.join(nltk_data_path, 'tokenizers', 'punkt')
    stopwords_path = os.path.join(nltk_data_path, 'corpora', 'stopwords')
    tagger_path = os.path.join(nltk_data_path, 'taggers', 'averaged_perceptron_tagger')
    
    # Check and load punkt
    if os.path.exists(punkt_path):
        print(f"Found punkt data at {punkt_path}")
    else:
        print("Downloading punkt data...")
        nltk.download('punkt', download_dir=nltk_data_path, quiet=False)
    
    # Check and load stopwords
    if os.path.exists(stopwords_path):
        print(f"Found stopwords data at {stopwords_path}")
    else:
        print("Downloading stopwords data...")
        nltk.download('stopwords', download_dir=nltk_data_path, quiet=False)
    
    # Check and load averaged_perceptron_tagger
    if os.path.exists(os.path.join(tagger_path, 'averaged_perceptron_tagger.pickle')):
        print(f"Found averaged_perceptron_tagger data at {tagger_path}")
    else:
        print("Downloading averaged_perceptron_tagger data...")
        nltk.download('averaged_perceptron_tagger', download_dir=nltk_data_path, quiet=False)

# Load required NLTK data
print("Loading NLTK data...")
try:
    load_nltk_data()
    print("NLTK data loaded successfully")
except Exception as e:
    print(f"Error loading NLTK data: {str(e)}")
    raise

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
    """Extract questions from PDF documents with improved text and structure analysis."""
    
    def __init__(self, pdf_path: str):
        """Initialize with path to PDF file."""
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.current_section = ""
        self.progress_callback = None
        self.total_pages = len(self.doc)
    
    def set_progress_callback(self, callback):
        """Set a callback function to report progress.
        
        The callback should accept the following parameters:
        - current_page: Current page being processed (0-based)
        - total_pages: Total number of pages
        - message: Optional status message
        """
        self.progress_callback = callback
    
    def _report_progress(self, current_page, message=None):
        """Report progress using the callback if available."""
        if self.progress_callback:
            self.progress_callback(current_page, self.total_pages, message)
    
    def extract_questions(self) -> List[ExtractedQuestion]:
        """Extract all questions from the PDF with progress reporting."""
        app.logger.info(f"Extracting questions from: {os.path.basename(self.pdf_path)}")
        questions = []
        
        try:
            self._report_progress(0, "Starting question extraction...")
            
            for page_num in range(len(self.doc)):
                page = self.doc[page_num]
                
                # Report progress for this page
                self._report_progress(
                    page_num,
                    f"Extracting questions from page {page_num + 1} of {self.total_pages}..."
                )
                
                # Get page text and update section
                text = page.get_text()
                self._update_section(text)
                
                # Extract questions from this page
                page_questions = self._extract_questions_from_page(text, page_num + 1)
                questions.extend(page_questions)
                
                # Log progress
                if page_num % 5 == 0 or page_num == len(self.doc) - 1:
                    app.logger.info(
                        f"Processed page {page_num + 1}/{len(self.doc)} - "
                        f"Found {len(page_questions)} questions on this page, "
                        f"Total so far: {len(questions)}"
                    )
                
            # Final progress update
            self._report_progress(
                len(self.doc) - 1,
                f"Completed extraction of {len(questions)} questions from {len(self.doc)} pages"
            )
            
        except Exception as e:
            error_msg = f"Error extracting questions from page {page_num + 1}: {str(e)}"
            app.logger.error(error_msg, exc_info=True)
            self._report_progress(
                page_num if 'page_num' in locals() else 0,
                f"Error: {error_msg[:200]}"
            )
            raise
            
        return questions
    
    def _update_section(self, text: str) -> None:
        """Update current section based on section headers in text."""
        section_match = re.search(r'Section\s+([A-Z]):\s*([^\n]+)', text)
        if section_match:
            self.current_section = section_match.group(2).strip()
    
    def _extract_questions_from_page(self, text: str, page_num: int) -> List[ExtractedQuestion]:
        """
        Extract questions from a single page's text with improved handling of various formats.
        
        Args:
            text: The text content of the page
            page_num: The page number
            
        Returns:
            List of ExtractedQuestion objects
        """
        questions = []
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if line starts with a question number/letter
            question_match = self._match_question_pattern(line)
            if question_match:
                question_num = question_match.group(1).strip()
                question_text = [question_match.group(2).strip() if question_match.group(2) else '']
                
                # Initialize variables for tracking question parts
                in_question = True
                options_started = False
                
                # Collect continuation lines until next question or end
                i += 1
                while i < len(lines) and in_question:
                    next_line = lines[i].strip()
                    
                    # Skip empty lines within the same question
                    if not next_line:
                        i += 1
                        continue
                    
                    # Check if next line starts a new question
                    next_question_match = self._match_question_pattern(next_line)
                    if next_question_match:
                        in_question = False
                        continue
                        
                    # Check for common question endings
                    if self._is_question_end(next_line, question_text):
                        in_question = False
                        continue
                        
                    # Handle options in multiple choice questions
                    if re.match(r'^([a-zA-Z]|[ivx]+\)|\d+\.)\s+', next_line):
                        if not options_started and len(question_text) > 0 and len(question_text[-1]) < 50:
                            # If we have very short question text, this might be part of the question
                            question_text.append(next_line)
                        else:
                            options_started = True
                            # For now, we'll include options in the question text
                            question_text.append(next_line)
                    else:
                        # Regular question text
                        question_text.append(next_line)
                    
                    i += 1
                
                # Clean up question text
                full_text = ' '.join(question_text).strip()
                
                # Skip if question text is too short (likely a false positive)
                if len(full_text) < 10:
                    i += 1
                    continue
                    
                # Create the question object
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
                questions.append(question)
                
                # If we've identified this as a multiple choice question, try to extract the options
                if question.question_type == "Multiple Choice":
                    self._extract_multiple_choice_options(question, question_text)
            else:
                i += 1
                
        return questions
    
    def _match_question_pattern(self, text: str) -> re.Match:
        """Match text against various question patterns."""
        patterns = [
            # Numbered questions (1., 2., etc.)
            r'^(\d+)[\.\)\]\}\s]\s*(.*)',
            # Lettered questions (a), b), etc.)
            r'^\(?([a-z])\)\s*(.*)',
            # Q1, Q2 or Q1:, Q2:
            r'^[Qq]\s*(\d+)[\.\)\:]?\s*(.*)',
            # Question 1, Problem 2, etc.
            r'^(?:Question|Problem|Exercise|Task)\s*(\d+)[\.\)\: ]?\s*(.*)',
            # Section-based numbering (1.1, 1.2, etc.)
            r'^(\d+\.\d+)[\.\)\s]\s*(.*)',
            # Bullet points with numbers or letters
            r'^[•\-*]\s*(\d+|[a-z])\)?\s*(.*)'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, text)
            if match:
                return match
        return None
    
    def _determine_question_type(self, text: str) -> str:
        """
        Determine the type of question based on its content, structure, and keywords.
        Returns one of: 'Multiple Choice', 'True/False', 'Matching', 'Fill-in-the-Blank', 
        'Short Answer', 'Long Answer', 'Problem Solving', 'Diagram-based', 'Essay', 'Calculation',
        'Proof', 'Case Study', or 'Other'.
        """
        text_lower = text.lower().strip()
        
        # Check for multiple choice (A), B), C), etc. or (i), (ii), (iii), etc.)
        if (re.search(r'\b(a|b|c|d|e)\)', text_lower) or 
            re.search(r'\([ivx]+\)', text_lower) or
            re.search(r'\b(true|false|t|f)\b', text_lower, re.IGNORECASE)):
            return "Multiple Choice"
            
        # Check for true/false questions
        if (re.search(r'\b(true|false)\b', text_lower) and 
            any(word in text_lower for word in ['circle', 'select', 'choose', 'tick', 'mark'])):
            return "True/False"
            
        # Check for matching questions
        if (re.search(r'match\s+(?:column|the following|items?|pairs?|statements?)', text_lower) or
            re.search(r'column\s+(a|i).*column\s+(b|ii)', text_lower, re.DOTALL)):
            return "Matching"
            
        # Check for fill-in-the-blank
        if (re.search(r'\b(?:fill\s*in|complete|fill\s*the\s*blank)', text_lower) or
            re.search(r'\b_+\b', text) or  # Underscore placeholders
            re.search(r'\b(?:write|provide|give|state)\s+(?:the|a)?\s*[^\n?]*\?', text_lower)):
            return "Fill-in-the-Blank"
        
        # Check for diagram-based questions
        if self._contains_diagram_marker(text_lower):
            return "Diagram-based"
            
        # Check for calculation problems
        if (any(word in text_lower for word in ['calculate', 'compute', 'solve for', 'find', 'determine', 'evaluate', 'simplify']) or
            re.search(r'\b(?:what is|what are|how (?:much|many|long|far|fast|tall|wide|high))\b', text_lower) or
            self._contains_formula(text_lower)):
            return "Problem Solving"
            
        # Check for proof questions
        if (any(word in text_lower for word in ['prove', 'show that', 'demonstrate', 'verify', 'derive']) or
            re.search(r'\b(?:prove|show)\s+(?:that\s+)?[A-Z]', text)):
            return "Proof"
            
        # Check for case studies
        if (any(word in text_lower for word in ['case study', 'case of', 'scenario', 'situation']) or
            re.search(r'\bgiven\s+(?:that\s+)?[A-Z]', text)):
            return "Case Study"
            
        # Check for essay questions
        if (any(word in text_lower for word in ['discuss', 'analyze', 'critique', 'evaluate', 'justify', 'examine', 'explore', 'elaborate', 'compare and contrast']) or
            len(text.split()) > 50):  # Long questions are likely essays
            return "Essay"
            
        # Check for short answer
        if (any(word in text_lower for word in ['what', 'when', 'where', 'who', 'which', 'why', 'how', 'name', 'list']) or
            '?' in text_lower or
            len(text.split()) < 30):  # Short questions
            return "Short Answer"
            
        # Default to long answer for anything that doesn't fit above
        return "Long Answer"
    
    def _extract_marks(self, text: str) -> int:
        """Extract marks from question text if specified."""
        marks_match = re.search(r'\((\d+)\s*(?:marks?|points?)\)', text, re.IGNORECASE)
        if marks_match:
            return int(marks_match.group(1))
        
        # Check for marks at the end of the question
        marks_match = re.search(r'\[(\d+)\s*(?:marks?|points?)\]', text, re.IGNORECASE)
        if marks_match:
            return int(marks_match.group(1))
            
        return 1  # Default marks
    
    def _contains_formula(self, text: str) -> bool:
        """Check if question contains mathematical formulas with enhanced detection."""
        # Basic math symbols
        math_symbols = r'[∑∫∂∆√∛∜∞≤≥≠≈≡±×÷∈∉⊆⊂∪∩∅]|\\[a-zA-Z]+|\^[0-9a-zA-Z{}()]+|_[0-9a-zA-Z{}()]+|\b(?:sin|cos|tan|cot|sec|csc|log|ln|exp|sqrt|integral|derivative|lim|sum|prod|int|iint|iiint)\b'
        
        # Common formula patterns
        formula_patterns = [
            r'\$[^$]+\$',  # LaTeX inline math
            r'\\\(.*?\\\)|\\\[.*?\\\]',  # LaTeX display math
            r'\b(?:eq\.?|equation|formula|theorem|proof|corollary|lemma|proposition)\b',
            r'[a-zA-Z]\s*[=≠≈]\s*[a-zA-Z0-9+\-*/^()]+',  # Equations like x = 2y + 3
            r'\d+\s*[a-zA-Zα-ωΑ-Ω]\b',  # Variables with coefficients
            r'[a-zA-Z]\s*[+\-*/^]\s*[a-zA-Z0-9()]',  # Basic operations with variables
            r'\b(?:if|then|therefore|because|since|given|let|assume|suppose|consider)\b.*?[=≠≈<>]',  # Conditional math
        ]
        
        # Check for any math symbols or patterns
        if re.search(math_symbols, text, re.IGNORECASE):
            return True
            
        # Check for formula patterns
        if any(re.search(pattern, text, re.IGNORECASE | re.DOTALL) for pattern in formula_patterns):
            return True
            
        # Check for common math notation
        if re.search(r'[a-zA-Z]\s*[{}]\s*[=:]', text):  # Set notation or function definitions
            return True
            
        return False
    
    def _is_question_end(self, line: str, question_text: List[str]) -> bool:
        """
        Determine if the current line indicates the end of a question.
        
        Args:
            line: The current line being processed
            question_text: List of lines in the current question
            
        Returns:
            bool: True if this line indicates the end of the question
        """
        # Common question endings
        endings = [
            r'\b(?:end\s+of\s+questions?|stop|that\s+is\s+all|no\s+more\s+questions)',
            r'\b(?:total|maximum|max)\s*[\[({]?\s*\d+\s*(?:marks?|points?|pts?\b)\s*[\])}]?',
            r'\b(?:page|p\.?\s*)\d+\s*(?:of|/)\s*\d+\s*$',
            r'\b(?:continued\s+on\s+next\s+page|cont\.?\s*\d+)\b',
            r'\b(?:section|part|chapter)\s+[A-Z0-9]+\b',
            r'^\s*\*{3,}\s*$',  # Lines with *** or more
            r'^\s*_{3,}\s*$',  # Lines with ___ or more
            r'^\s*-{3,}\s*$'   # Lines with --- or more
        ]
        
        # Check for ending patterns
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in endings):
            return True
            
        # Check if this looks like the start of a new section or header
        if (re.match(r'^\s*[A-Z][A-Z\s]+$', line) and  # All caps line
            len(line.split()) < 5 and  # Short line (likely a header)
            len(question_text) > 1):  # Already have some question text
            return True
            
        # Check for page numbers or footers
        if (re.search(r'^\s*\d+\s*$', line) or  # Just a number
            re.search(r'^[A-Za-z]+\s+\d+\s*$', line)):  # Month Year or similar
            return True
            
        return False
        
    def _extract_multiple_choice_options(self, question: ExtractedQuestion, question_text: List[str]) -> None:
        """
        Extract multiple choice options from question text and update the question object.
        
        Args:
            question: The question object to update
            question_text: List of text lines for the question
        """
        options = {}
        current_option = None
        option_pattern = re.compile(r'^\s*([a-zA-Z]|[ivx]+\)|\d+\.)\s*(.*)')
        
        # Process each line to find options
        for line in question_text:
            match = option_pattern.match(line)
            if match:
                option_key = match.group(1).strip().lower()
                option_text = match.group(2).strip()
                
                # Skip if this looks like part of the question text
                if current_option is None and len(option_text.split()) > 5:  # Too long for an option
                    continue
                    
                current_option = option_key
                options[option_key] = option_text
            elif current_option is not None:
                # Continue the current option if the line is indented or starts with a space
                if line.startswith((' ', '\t')) and line.strip():
                    options[current_option] += ' ' + line.strip()
        
        # Update the question object with the extracted options
        if options:
            if not hasattr(question, 'metadata'):
                question.metadata = {}
            question.metadata['options'] = options
            
            # If we have a question mark in the first line, try to separate the question from options
            first_line = question_text[0] if question_text else ''
            if '?' in first_line and len(question_text) > 1:
                question_parts = first_line.split('?', 1)
                if len(question_parts) > 1 and question_parts[1].strip():
                    question.question_text = question_parts[0] + '?'
                    # The rest might be part of the first option
                    first_option = question_parts[1].strip()
                    if first_option and not any(k in first_option.lower() for k in options.keys()):
                        # If we don't already have this as an option, add it
                        first_letter = chr(ord('a') + len(options))
                        options[first_letter] = first_option
    
    def _contains_diagram_marker(self, text: str) -> bool:
        """Check if question contains diagram-related markers with enhanced detection."""
        # Basic diagram indicators
        diagram_indicators = [
            r'\b(?:diagram|figure|draw|sketch|illustration|graph|chart|plot|image|picture|schematic|blueprint|map)\b',
            r'\blabel\s*(?:the|each|all|any|every|some|these|those|following|below|above|on|in|at|for|with|of)?\s*',
            r'\b(?:show|indicate|mark|identify|point out|highlight|circle|box|shade|color|colour|outline|trace|plot)\b.*\b(on|in|at|for|with|of)\b.*\b(diagram|figure|graph|chart|image|picture|drawing|illustration)',
            r'\b(refer|according|see|based on|using|use|given|following|shown|displayed|illustrated|depicted|represented)\b.*\b(diagram|figure|graph|chart|image|picture|drawing|illustration)',
            r'\b(diagram|figure|graph|chart|image|picture|drawing|illustration)\s*[0-9]*\s*(?:shows|showing|illustrates|depicts|represents|demonstrates|presents|displays|contains|includes)',
            r'\b(?:as|like|similar to|resembling|in the style of|in the form of|in the shape of|in the pattern of)\b.*\b(diagram|figure|graph|chart|image|picture|drawing|illustration)',
            r'\b(?:with|having|containing|including|featuring|showing|displaying|illustrating|depicting|representing|demonstrating|presenting)\b.*\b(diagram|figure|graph|chart|image|picture|drawing|illustration)',
        ]
        
        # Check for any diagram indicators
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in diagram_indicators):
            return True
            
        # Check for coordinate system references
        if re.search(r'\b(?:x-?axis|y-?axis|origin|coordinate\s*system|grid|axes|quadrant|abscissa|ordinate)\b', text, re.IGNORECASE):
            return True
            
        # Check for geometric shape references
        if re.search(r'\b(?:point|line|segment|ray|angle|triangle|square|rectangle|circle|ellipse|polygon|polyhedron|prism|pyramid|cylinder|cone|sphere|cube|rhombus|trapezoid|parallelogram|pentagon|hexagon|octagon|dodecagon|tetrahedron|octahedron|dodecahedron|icosahedron|ellipsoid|hyperboloid|paraboloid|torus)\b', text, re.IGNORECASE):
            return True
            
        return False
    
    def __del__(self):
        """Ensure the PDF document is properly closed."""
        if hasattr(self, 'doc'):
            self.doc.close()


class QuestionExtractor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.current_section = ""
        self.progress_callback = None
        self.total_pages = 0
        
        # Enhanced question patterns with better support for different formats
        self.question_patterns = [
            # Numbered questions (1., 2., etc.)
            r'^(\d+)[\.\)\]\}\s]\s*',
            # Lettered questions (a), b), etc.)
            r'\(?([a-z])\)\s*',
            # Roman numerals (i., ii., etc.)
            r'([ivx]+)[\.\)\s]\s*',
            # Q1, Q2 or Q1:, Q2:
            r'[Qq]\s*(\d+)[\.\)\:]\s*',
            # Question 1, Problem 2, etc.
            r'(?:Question|Problem|Exercise|Task)\s*(\d+)[\.\)\: ]?\s*',
            # Section-based numbering (1.1, 1.2, etc.)
            r'(\d+\.\d+)[\.\)\s]\s*',
            # Bullet points with numbers or letters
            r'[•\-*]\s*(\d+|[a-z])\)?\s*'
        ]
        
        # Keywords that might indicate a question
        self.question_keywords = [
            'what', 'when', 'where', 'why', 'how', 'explain', 'describe',
            'calculate', 'solve', 'find', 'prove', 'show', 'determine',
            'compare', 'contrast', 'discuss', 'evaluate', 'analyze', 'justify'
        ]
        
        # Formula and math-related keywords
        self.formula_keywords = [
            'equation', 'formula', 'calculate', 'solve', 'find', 'derive', 'prove',
            'compute', 'evaluate', 'simplify', 'factor', 'expand', 'integrate',
            'differentiate', 'graph', 'plot', 'matrix', 'vector', 'theorem', 'proof'
        ]
        
        # Difficulty indicators
        self.difficulty_indicators = {
            'easy': ['define', 'list', 'identify', 'name', 'recall', 'state', 'match'],
            'medium': ['explain', 'describe', 'summarize', 'classify', 'compare', 'contrast'],
            'hard': ['analyze', 'evaluate', 'justify', 'critique', 'design', 'formulate', 'prove']
        }
    
    def set_progress_callback(self, callback):
        """Set a callback function to report progress.
        
        The callback should accept the following parameters:
        - current_page: Current page being processed
        - total_pages: Total number of pages
        - message: Optional status message
        """
        self.progress_callback = callback
    
    def _report_progress(self, current_page, message=None):
        """Report progress using the callback if available."""
        if self.progress_callback and self.total_pages > 0:
            self.progress_callback(current_page, self.total_pages, message)
        
    def process_document(self, document_id):
        """Process a document and extract questions.
        
        Args:
            document_id: ID of the document to process
            
        Returns:
            bool: True if processing was successful, False otherwise
        """
        document = QuestionDocument.query.get(document_id)
        if not document:
            app.logger.error(f"Document {document_id} not found")
            return False
            
        try:
            app.logger.info(f"Starting extraction for document {document_id}")
            
            # Open the PDF to get total pages for progress tracking
            try:
                doc = fitz.open(document.file_path)
                self.total_pages = len(doc)
                doc.close()
                app.logger.info(f"Document has {self.total_pages} pages")
            except Exception as e:
                app.logger.warning(f"Could not get total pages for document {document_id}: {str(e)}")
                self.total_pages = 0
            
            # Report initial progress
            self._report_progress(0, "Starting document processing...")
            
            # Extract questions from PDF
            extractor = PDFQuestionExtractor(document.file_path)
            
            # Set up progress reporting for the extractor
            def extraction_progress(page_num, total_pages, message):
                self._report_progress(page_num, message)
                
            extractor.set_progress_callback(extraction_progress)
            
            # Extract questions with progress reporting
            extracted_questions = extractor.extract_questions()
            
            # Report progress before saving to database
            self._report_progress(
                self.total_pages - 1 if self.total_pages > 0 else 0,
                f"Extracted {len(extracted_questions)} questions. Saving to database..."
            )
            
            # Save extracted questions to database
            saved_count = 0
            for eq in extracted_questions:
                try:
                    self.save_question({
                        'question_number': eq.question_number,
                        'question_text': eq.question_text,
                        'page_number': eq.page_number,
                        'section': eq.section,
                        'question_type': eq.question_type,
                        'marks': eq.marks,
                        'has_formula': eq.has_formula,
                        'has_diagram': eq.has_diagram,
                        'metadata': json.dumps(eq.metadata) if hasattr(eq, 'metadata') else None
                    }, document)
                    saved_count += 1
                    
                    # Update progress every 5 questions
                    if saved_count % 5 == 0:
                        self._report_progress(
                            self.total_pages - 1 if self.total_pages > 0 else 0,
                            f"Saved {saved_count} of {len(extracted_questions)} questions..."
                        )
                        
                except Exception as save_error:
                    app.logger.error(f"Error saving question {eq.question_number if hasattr(eq, 'question_number') else 'unknown'}: {str(save_error)}", exc_info=True)
                    continue  # Continue with next question even if one fails
            
            # Update document status
            try:
                document.extraction_status = 'completed'
                document.total_questions = saved_count
                document.processed_at = datetime.utcnow()
                db.session.commit()
                
                app.logger.info(f"Successfully extracted and saved {saved_count} questions from document {document_id}")
                return True
                
            except Exception as commit_error:
                app.logger.error(f"Error updating document status: {str(commit_error)}", exc_info=True)
                db.session.rollback()
                raise  # Re-raise to be caught by outer exception handler
                
        except Exception as e:
            app.logger.error(f"Error processing document {document_id}: {str(e)}", exc_info=True)
            try:
                if document:
                    document.extraction_status = 'failed'
                    db.session.commit()
            except Exception as status_error:
                app.logger.error(f"Error updating document status to failed: {str(status_error)}", exc_info=True)
                db.session.rollback()
            return False
    
    def extract_questions_from_pdf(self, pdf_path):
        """Extract questions from a PDF file."""
        try:
            extractor = PDFQuestionExtractor(pdf_path)
            extracted_questions = extractor.extract_questions()
            
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
            } for q in extracted_questions]
            
        except Exception as e:
            app.logger.error(f"Error extracting questions from PDF {pdf_path}: {str(e)}", exc_info=True)
            return []
    
    def save_question(self, question_data, document):
        """Save a question to the database."""
        try:
            question = Question(
                question_number=question_data.get('question_number', ''),
                question_text=question_data.get('question_text', ''),
                page_number=question_data.get('page_number', 1),
                question_type=question_data.get('question_type', 'text'),
                marks=question_data.get('marks', 1),
                has_formula=question_data.get('has_formula', False),
                has_image=question_data.get('has_diagram', False),  # Map has_diagram to has_image
                document_id=document.id,
                created_at=datetime.utcnow()
            )
            db.session.add(question)
            db.session.commit()
            app.logger.debug(f"Saved question {question.id} for document {document.id}")
            return question
        except Exception as e:
            app.logger.error(f"Error saving question for document {document.id}: {str(e)}", exc_info=True)
            db.session.rollback()
            return None
    
    def categorize_question(self, question, subject):
        """Automatically categorize question by topic and unit."""
        if not subject:
            return
            
        # Get all units and topics for this subject
        units = Unit.query.filter_by(subject_id=subject.id).all()
        if not units:
            return
            
        # Prepare text for analysis
        question_text = question.question_text.lower()
        tokens = word_tokenize(question_text)
        tokens = [token for token in tokens if token.isalpha() and token not in self.stop_words]
        clean_text = ' '.join(tokens)
        
        best_unit = None
        best_topic = None
        best_unit_score = 0
        best_topic_score = 0
        
        # Compare with each unit and its topics
        for unit in units:
            unit_text = f"{unit.name} {unit.description or ''}".lower()
            unit_score = self.calculate_similarity(clean_text, unit_text)
            
            if unit_score > best_unit_score:
                best_unit_score = unit_score
                best_unit = unit
            
            # Check topics within this unit
            for topic in unit.topics:
                topic_text = f"{topic.name} {topic.description or ''}".lower()
                topic_score = self.calculate_similarity(clean_text, topic_text)
                
                if topic_score > best_topic_score:
                    best_topic_score = topic_score
                    best_topic = topic
        
        # Assign if confidence is above threshold
        if best_unit_score > 0.1:  # Threshold for unit assignment
            question.unit_id = best_unit.id
            question.unit_confidence = best_unit_score
            
        if best_topic_score > 0.1:  # Threshold for topic assignment
            question.topic_id = best_topic.id
            question.topic_confidence = best_topic_score
    
    def calculate_similarity(self, text1, text2):
        """Calculate similarity between two texts using TF-IDF."""
        if not text1.strip() or not text2.strip():
            return 0
            
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return similarity[0][0]
        except:
            return 0

    def __init__(self):
        pass
    
    def generate_question_paper(self, subject_id, unit_ids=None, topic_ids=None, 
                          total_marks=100, difficulty_distribution=None):
        """Generate a question paper based on specified criteria with ResearchNest signature and watermark."""
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Image, 
            PageBreak, Table, TableStyle, PageTemplate, Frame
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch, cm
        from reportlab.lib import colors
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from datetime import datetime
        import os
        import sys
        from flask import current_app
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        # Define a fallback static folder path if not in app context
        try:
            static_folder = current_app.static_folder
        except RuntimeError:
            # If we're not in an app context, use a relative path
            static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app', 'static')
        
        # Register font for watermark
        try:
            pdfmetrics.registerFont(TTFont('Roboto-Light', 'app/static/fonts/Roboto-Light.ttf'))
            pdfmetrics.registerFont(TTFont('Roboto-Bold', 'app/static/fonts/Roboto-Bold.ttf'))
        except:
            # Fallback to default font if custom font not available
            pass
        
        # Default difficulty distribution
        if not difficulty_distribution:
            difficulty_distribution = {'easy': 0.3, 'medium': 0.5, 'hard': 0.2}
        
        # Get questions based on criteria
        questions = self.select_questions(
            subject_id, unit_ids, topic_ids, total_marks, difficulty_distribution
        )
        
        if not questions:
            return None
        
        # Generate PDF
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'ResearchNest_QuestionPaper_{timestamp}.pdf'
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'question_papers', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Add custom styles
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            alignment=1,  # Center aligned
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#2c3e50')
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=1,
            fontName='Helvetica',
            textColor=colors.HexColor('#34495e')
        )
        
        question_style = ParagraphStyle(
            'Question',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            leading=14,
            fontName='Helvetica',
            textColor=colors.HexColor('#2c3e50')
        )
        
        instruction_style = ParagraphStyle(
            'Instruction',
            parent=styles['Italic'],
            fontSize=10,
            spaceAfter=16,
            leading=12,
            fontName='Helvetica-Oblique',
            textColor=colors.HexColor('#7f8c8d')
        )
        
        # Create a custom header and footer function with watermark
        def add_header_footer(canvas, doc):
            canvas.saveState()
            
            # Add watermark
            canvas.saveState()
            canvas.setFont('Helvetica', 60)
            # Using a very light gray color instead of alpha transparency
            canvas.setFillColor(colors.HexColor('#f0f0f0'))
            canvas.translate(A4[0]/2, A4[1]/2)
            canvas.rotate(45)
            canvas.drawCentredString(0, 0, "RESEARCHNEST")
            canvas.restoreState()
            
            # Draw header line
            canvas.setStrokeColor(colors.HexColor('#3498db'))
            canvas.setLineWidth(1)
            canvas.line(50, A4[1] - 60, A4[0] - 50, A4[1] - 60)
            
            # Add header
            canvas.setFont('Helvetica-Bold', 10)
            canvas.setFillColor(colors.HexColor('#3498db'))
            canvas.drawString(50, A4[1] - 45, "RESEARCHNEST - ACADEMIC QUESTION PAPER")
            
            # Add page number
            page_num = canvas.getPageNumber()
            canvas.drawRightString(A4[0] - 50, A4[1] - 45, f"Page {page_num}")
            
            # Draw footer line
            canvas.setStrokeColor(colors.HexColor('#e74c3c'))
            canvas.setLineWidth(0.5)
            canvas.line(50, 50, A4[0] - 50, 50)
            
            # Add footer text
            canvas.setFont('Helvetica', 8)
            canvas.setFillColor(colors.HexColor('#7f8c8d'))
            
            # Left side - Copyright notice
            current_year = datetime.now().year
            text = f"© {current_year} ResearchNest. All rights reserved."
            canvas.drawString(50, 35, text)
            
            # Right side - Generation timestamp
            text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            text_width = canvas.stringWidth(text, 'Helvetica', 8)
            canvas.drawString(A4[0] - 50 - text_width, 35, text)
            
            # Add ResearchNest logo or text fallback
            logo_path = os.path.join(static_folder, 'img', 'researchnest-logo.png')
            logo_found = False
            
            # Try to load the logo if it exists
            if os.path.exists(logo_path):
                try:
                    logo = Image(logo_path, width=2*cm, height=0.7*cm)
                    logo.drawOn(canvas, (A4[0] - 2*cm)/2, 35)  # Center the logo
                    logo_found = True
                except Exception as e:
                    app.logger.warning(f"Could not add logo: {str(e)}")
            
            # If logo not found or failed to load, use text fallback
            if not logo_found:
                try:
                    canvas.setFont('Helvetica-Bold', 12)
                    canvas.setFillColor(colors.HexColor('#3498db'))
                    text = "RESEARCHNEST"
                    text_width = canvas.stringWidth(text, 'Helvetica-Bold', 12)
                    canvas.drawString((A4[0] - text_width)/2, 35, text)
                except Exception as e:
                    app.logger.warning(f"Could not add text fallback: {str(e)}")
            
            canvas.restoreState()
        
        # Get subject information for document metadata
        subject_name = 'General'
        try:
            subject = Subject.query.get(subject_id)
            if subject:
                subject_name = subject.name
        except Exception as e:
            app.logger.warning(f"Could not load subject: {str(e)}")
        
        # Create document with custom header and footer
        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=80,  # More space for header
            bottomMargin=70,  # More space for footer
            title=f"ResearchNest Question Paper - {timestamp}",
            author="ResearchNest Platform",
            subject=f"Generated Question Paper - {subject_name}",
            creator="ResearchNest Platform",
            producer="ResearchNest"
        )
        
        # Override build method to include header and footer on all pages
        def build_with_watermark(story, **kwargs):
            return SimpleDocTemplate.build(
                doc, 
                story, 
                onFirstPage=add_header_footer, 
                onLaterPages=add_header_footer, 
                **kwargs
            )
            
        doc.build = build_with_watermark
        
        # Start building the document
        story = []
        
        # Add title and subtitle
        story.append(Paragraph("RESEARCHNEST", title_style))
        story.append(Paragraph("Question Paper", subtitle_style))
        
        # Add a decorative line
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b><font color='#e74c3c'>" + "•"*50 + "</font></b>", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Add paper metadata in a table for better organization
        subject = Subject.query.get(subject_id)
        meta_data = []
        
        if subject:
            meta_data.append(['Subject', subject.name])
            
            # Add units if specified
            if unit_ids:
                units = Unit.query.filter(Unit.id.in_(unit_ids)).all()
                if units:
                    unit_names = ", ".join([unit.name for unit in units])
                    meta_data.append(['Unit(s)', unit_names])
            
            # Add topics if specified
            if topic_ids:
                topics = Topic.query.filter(Topic.id.in_(topic_ids)).all()
                if topics:
                    topic_names = ", ".join([topic.name for topic in topics])
                    meta_data.append(['Topic(s)', topic_names])
        
        # Add paper details
        meta_data.extend([
            ['Total Marks', str(total_marks)],
            ['Time Allowed', '3 hours'],
        ])
        
        # Add difficulty distribution if available
        if difficulty_distribution:
            easy_pct = int(difficulty_distribution['easy'] * 100)
            medium_pct = int(difficulty_distribution['medium'] * 100)
            hard_pct = int(difficulty_distribution['hard'] * 100)
            difficulty_text = f"Easy: {easy_pct}%, Medium: {medium_pct}%, Hard: {hard_pct}%"
            meta_data.append(['Difficulty', difficulty_text])
        
        # Create table for metadata with styling
        meta_table = Table(meta_data, colWidths=[150, 350])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),  # Light gray for header column
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6c757d')),  # Dark gray text for header
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Bold for header column
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),  # Light border
            ('LEFTPADDING', (0, 0), (0, -1), 0),
            ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ]))
        
        story.append(meta_table)
        story.append(Spacer(1, 30))
        
        # Add instructions with better formatting
        instructions = [
            "<b>GENERAL INSTRUCTIONS:</b>",
            "1. All questions are compulsory.",
            "2. Write your answers clearly and legibly.",
            "3. Figures to the right indicate full marks.",
            "4. Assume suitable data if necessary.",
            "5. Use of non-programmable scientific calculator is allowed.",
            "6. Draw neat diagrams wherever necessary.",
            f"7. Total time: 3 hours | Total marks: {total_marks}"
        ]
        
        instruction_paragraphs = []
        for line in instructions:
            if line.startswith("<b>"):
                instruction_paragraphs.append(Paragraph(f"<b>{line[3:-4].upper()}</b>", instruction_style))
            else:
                instruction_paragraphs.append(Paragraph(line, instruction_style))
        
        story.extend(instruction_paragraphs)
        story.append(PageBreak())  # Start questions on a new page
        
        # Add questions section header
        story.append(Paragraph("<b>SECTION - A</b> (Answer All Questions)", styles['Heading2']))
        story.append(Spacer(1, 20))
        
        # Questions
        for i, question in enumerate(questions, 1):
            # Create a styled question number and text
            question_text = f"<b>Q.{i}</b> {question.question_text} <font color='#7f8c8d'><i>[{question.marks} Mark{'s' if question.marks > 1 else ''}]</i></font>"
            
            # Add the question to the story
            story.append(Paragraph(question_text, question_style))
            
            # Add space for answer if needed
            story.append(Spacer(1, 10))
            
            # Add images if present
            if question.has_image and question.image_paths:
                try:
                    image_paths = json.loads(question.image_paths)
                    for img_path in image_paths:
                        if os.path.exists(img_path):
                            # Try to get image dimensions and maintain aspect ratio
                            try:
                                from PIL import Image as PILImage
                                with PILImage.open(img_path) as img:
                                    width, height = img.size
                                    aspect_ratio = width / height
                                    max_width = 4.5 * inch
                                    display_width = min(max_width, width / 2)
                                    display_height = display_width / aspect_ratio
                                    
                                    # Ensure the image isn't too tall
                                    if display_height > 6 * inch:
                                        display_height = 6 * inch
                                        display_width = display_height * aspect_ratio
                                    
                                    img = Image(img_path, width=display_width, height=display_height)
                                    story.append(img)
                            except Exception as e:
                                app.logger.warning(f"Could not resize image: {str(e)}")
                                img = Image(img_path, width=4*inch, height=3*inch)
                                story.append(img)
                            
                            story.append(Spacer(1, 10))
                except Exception as e:
                    app.logger.warning(f"Error processing image: {str(e)}")
            
            # Add space between questions
            story.append(Spacer(1, 20))
            
            # Add page break every 3 questions to prevent crowding
            if i % 3 == 0 and i < len(questions):
                story.append(PageBreak())
                story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story)
        
        return filename, file_path
    def select_questions(self, subject_id, unit_ids, topic_ids, total_marks, difficulty_distribution):
        """Select questions based on criteria."""
        from flask import current_app
        from sqlalchemy import or_
        
        # Start building the query
        query = Question.query.join(QuestionDocument).filter(
            QuestionDocument.subject_id == subject_id,
            QuestionDocument.status == 'approved',
            Question.marks > 0  # Only include questions with positive marks
        )
        
        # Add unit filter if specified
        if unit_ids:
            query = query.filter(Question.unit_id.in_(unit_ids))
        
        # Add topic filter if specified
        if topic_ids:
            query = query.filter(Question.topic_id.in_(topic_ids))
        
        # Get all matching questions
        all_questions = query.all()
        
        if not all_questions:
            current_app.logger.warning(f"No questions found for subject_id={subject_id}, "
                                     f"unit_ids={unit_ids}, topic_ids={topic_ids}")
            return []
        
        # Log question counts for debugging
        current_app.logger.info(f"Found {len(all_questions)} questions matching the criteria")
        
        # Group by difficulty
        questions_by_difficulty = {
            'easy': [q for q in all_questions if q.difficulty_level.lower() == 'easy'],
            'medium': [q for q in all_questions if q.difficulty_level.lower() == 'medium'],
            'hard': [q for q in all_questions if q.difficulty_level.lower() == 'hard']
        }
        
        # Log difficulty distribution for debugging
        for difficulty, questions in questions_by_difficulty.items():
            current_app.logger.info(f"Found {len(questions)} {difficulty} questions")
        
        selected_questions = []
        remaining_marks = total_marks
        
        # Sort each difficulty group by marks (ascending) to better fit the target marks
        for difficulty in questions_by_difficulty:
            questions_by_difficulty[difficulty].sort(key=lambda x: x.marks)
        
        # Select questions based on difficulty distribution
        for difficulty, percentage in difficulty_distribution.items():
            if percentage <= 0:
                continue
                
            target_marks = int(total_marks * percentage)
            available_questions = questions_by_difficulty.get(difficulty, [])
            
            if not available_questions:
                current_app.logger.warning(f"No {difficulty} questions available for selection")
                continue
                
            current_marks = 0
            
            # Try to find questions that match the target marks
            for question in available_questions:
                if (current_marks + question.marks <= target_marks and 
                    remaining_marks >= question.marks):
                    selected_questions.append(question)
                    current_marks += question.marks
                    remaining_marks -= question.marks
                
                # If we've reached or exceeded target marks, move to next difficulty
                if current_marks >= target_marks or remaining_marks <= 0:
                    break
            
            current_app.logger.info(f"Selected {current_marks}/{target_marks} marks of {difficulty} questions")
        
        # If we couldn't find enough questions, try to fill the remaining marks with any available questions
        if remaining_marks > 0 and len(selected_questions) < len(all_questions):
            current_app.logger.info(f"Trying to fill remaining {remaining_marks} marks with any suitable questions")
            
            # Get all questions not yet selected, sorted by marks (ascending)
            remaining_questions = [q for q in all_questions if q not in selected_questions]
            remaining_questions.sort(key=lambda x: x.marks)
            
            for question in remaining_questions:
                if question.marks <= remaining_marks:
                    selected_questions.append(question)
                    remaining_marks -= question.marks
                    
                    if remaining_marks <= 0:
                        break
        
        # Log final selection
        if selected_questions:
            total_selected_marks = sum(q.marks for q in selected_questions)
            current_app.logger.info(f"Selected {len(selected_questions)} questions with {total_selected_marks} total marks")
            return selected_questions
        
        current_app.logger.warning("No questions could be selected with the given criteria")
        return []