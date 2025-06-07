import os
import re
import json
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from app import app, db
from models import Question, QuestionDocument, Unit, Topic, Subject

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class QuestionExtractor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.question_patterns = [
            r'^\s*(\d+)\.\s*',  # 1. Question
            r'^\s*([a-z])\)\s*',  # a) Question
            r'^\s*([A-Z])\)\s*',  # A) Question
            r'^\s*([ivx]+)\.\s*',  # i. ii. iii. Roman numerals
            r'^\s*Q\s*(\d+)[\.\:]\s*',  # Q1: Question
            r'^\s*Question\s*(\d+)[\.\:]\s*',  # Question 1: 
        ]
        self.formula_keywords = ['equation', 'formula', 'calculate', 'solve', 'find', 'derive', 'prove']
        
    def process_document(self, document_id):
        """Main function to process a question document."""
        document = QuestionDocument.query.get(document_id)
        if not document:
            return False
            
        try:
            # Update status to processing
            document.extraction_status = 'extracting'
            db.session.commit()
            
            # Extract questions from PDF
            questions = self.extract_questions_from_pdf(document.file_path)
            
            # Process each question
            for question_data in questions:
                self.save_question(question_data, document)
            
            # Update document status
            document.extraction_status = 'completed'
            document.total_questions = len(questions)
            document.processed_at = datetime.now()
            db.session.commit()
            
            return True
            
        except Exception as e:
            document.extraction_status = 'failed'
            db.session.commit()
            print(f"Error processing document {document_id}: {str(e)}")
            return False
    
    def extract_questions_from_pdf(self, file_path):
        """Extract questions, images, and formulas from PDF."""
        questions = []
        doc = fitz.open(file_path)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Extract text
            text = page.get_text()
            
            # Extract images from this page
            page_images = self.extract_images_from_page(page, page_num, file_path)
            
            # Split text into potential questions
            page_questions = self.identify_questions_in_text(text, page_num)
            
            # Associate images with questions
            for question in page_questions:
                question['images'] = self.associate_images_with_question(
                    question, page_images, page
                )
                questions.append(question)
        
        doc.close()
        return questions
    
    def identify_questions_in_text(self, text, page_num):
        """Identify individual questions in text using patterns."""
        questions = []
        lines = text.split('\n')
        current_question = []
        question_number = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line starts a new question
            is_new_question = False
            for pattern in self.question_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    # Save previous question if exists
                    if current_question and question_number:
                        question_text = ' '.join(current_question).strip()
                        if question_text:
                            questions.append({
                                'question_number': question_number,
                                'question_text': question_text,
                                'page_number': page_num + 1,
                                'has_formula': self.detect_formula(question_text),
                                'difficulty_level': self.estimate_difficulty(question_text),
                                'marks': self.extract_marks(question_text)
                            })
                    
                    # Start new question
                    question_number = match.group(1)
                    current_question = [re.sub(pattern, '', line, flags=re.IGNORECASE).strip()]
                    is_new_question = True
                    break
            
            if not is_new_question and current_question:
                current_question.append(line)
        
        # Save last question
        if current_question and question_number:
            question_text = ' '.join(current_question).strip()
            if question_text:
                questions.append({
                    'question_number': question_number,
                    'question_text': question_text,
                    'page_number': page_num + 1,
                    'has_formula': self.detect_formula(question_text),
                    'difficulty_level': self.estimate_difficulty(question_text),
                    'marks': self.extract_marks(question_text)
                })
        
        return questions
    
    def extract_images_from_page(self, page, page_num, file_path):
        """Extract images from a PDF page."""
        images = []
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            try:
                # Get image data
                xref = img[0]
                pix = fitz.Pixmap(page.parent, xref)
                
                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    # Save image
                    img_filename = f"page_{page_num+1}_img_{img_index+1}.png"
                    img_dir = os.path.join(os.path.dirname(file_path), 'extracted_images')
                    os.makedirs(img_dir, exist_ok=True)
                    img_path = os.path.join(img_dir, img_filename)
                    pix.save(img_path)
                    
                    # Get image position
                    img_rect = page.get_image_rects(xref)[0] if page.get_image_rects(xref) else None
                    
                    images.append({
                        'path': img_path,
                        'filename': img_filename,
                        'position': img_rect,
                        'page': page_num + 1
                    })
                
                pix = None
                
            except Exception as e:
                print(f"Error extracting image {img_index} from page {page_num}: {str(e)}")
                continue
                
        return images
    
    def associate_images_with_question(self, question, page_images, page):
        """Associate images with questions based on position."""
        question_images = []
        # Simple association - could be improved with more sophisticated positioning
        if page_images:
            question_images = page_images  # For now, associate all page images
        return question_images
    
    def detect_formula(self, text):
        """Detect if question contains mathematical formulas."""
        formula_indicators = [
            r'[∑∫∂∆√π∞≤≥≠±×÷]',  # Mathematical symbols
            r'\b(sin|cos|tan|log|ln|exp|sqrt|integral|derivative)\b',  # Mathematical functions
            r'[a-zA-Z]\^[0-9]',  # Exponents
            r'\b\d+\s*[a-zA-Z]\b',  # Variables with coefficients
        ]
        
        for pattern in formula_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                return True
                
        # Check for formula keywords
        for keyword in self.formula_keywords:
            if keyword.lower() in text.lower():
                return True
                
        return False
    
    def estimate_difficulty(self, text):
        """Estimate question difficulty based on text analysis."""
        word_count = len(text.split())
        
        # Simple heuristics
        if word_count < 20:
            return 'easy'
        elif word_count < 50:
            return 'medium'
        else:
            return 'hard'
    
    def extract_marks(self, text):
        """Extract marks/points from question text."""
        # Look for patterns like [5 marks], (10 points), etc.
        patterns = [
            r'\[(\d+)\s*marks?\]',
            r'\((\d+)\s*marks?\)',
            r'\[(\d+)\s*points?\]',
            r'\((\d+)\s*points?\)',
            r'(\d+)\s*marks?',
            r'(\d+)\s*points?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return 1  # Default marks
    
    def save_question(self, question_data, document):
        """Save extracted question to database."""
        question = Question(
            question_text=question_data['question_text'],
            question_number=question_data['question_number'],
            page_number=question_data['page_number'],
            has_formula=question_data['has_formula'],
            has_image=len(question_data.get('images', [])) > 0,
            difficulty_level=question_data['difficulty_level'],
            marks=question_data['marks'],
            document_id=document.id,
            image_paths=json.dumps([img['path'] for img in question_data.get('images', [])])
        )
        
        # Auto-categorize question
        self.categorize_question(question, document.subject)
        
        db.session.add(question)
        db.session.commit()
    
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

class QuestionPaperGenerator:
    def __init__(self):
        pass
    
    def generate_question_paper(self, subject_id, unit_ids=None, topic_ids=None, 
                              total_marks=100, difficulty_distribution=None):
        """Generate a question paper based on specified criteria."""
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        
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
        filename = f"question_paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = os.path.join(app.config.get('UPLOAD_FOLDER', 'uploads'), 'generated', filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        subject = Subject.query.get(subject_id)
        story.append(Paragraph(f"{subject.name} - Question Paper", title_style))
        story.append(Spacer(1, 20))
        
        # Instructions
        instructions = """
        <b>Instructions:</b><br/>
        1. Answer all questions.<br/>
        2. Write your answers clearly.<br/>
        3. Time allowed: 3 hours.<br/>
        4. Total marks: {}<br/>
        """.format(total_marks)
        story.append(Paragraph(instructions, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Questions
        for i, question in enumerate(questions, 1):
            # Question text
            question_text = f"<b>{i}. {question.question_text}</b> ({question.marks} marks)"
            story.append(Paragraph(question_text, styles['Normal']))
            
            # Add images if present
            if question.has_image and question.image_paths:
                try:
                    image_paths = json.loads(question.image_paths)
                    for img_path in image_paths:
                        if os.path.exists(img_path):
                            story.append(Spacer(1, 10))
                            img = Image(img_path, width=4*inch, height=3*inch)
                            story.append(img)
                except:
                    pass
            
            story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story)
        
        return filename, file_path
    
    def select_questions(self, subject_id, unit_ids, topic_ids, total_marks, difficulty_distribution):
        """Select questions based on criteria."""
        query = Question.query.join(QuestionDocument).filter(
            QuestionDocument.subject_id == subject_id,
            QuestionDocument.status == 'approved'
        )
        
        if unit_ids:
            query = query.filter(Question.unit_id.in_(unit_ids))
        
        if topic_ids:
            query = query.filter(Question.topic_id.in_(topic_ids))
        
        all_questions = query.all()
        
        # Group by difficulty
        questions_by_difficulty = {
            'easy': [q for q in all_questions if q.difficulty_level == 'easy'],
            'medium': [q for q in all_questions if q.difficulty_level == 'medium'],
            'hard': [q for q in all_questions if q.difficulty_level == 'hard']
        }
        
        selected_questions = []
        remaining_marks = total_marks
        
        # Select questions based on difficulty distribution
        for difficulty, percentage in difficulty_distribution.items():
            target_marks = int(total_marks * percentage)
            available_questions = questions_by_difficulty[difficulty]
            
            current_marks = 0
            for question in available_questions:
                if current_marks + question.marks <= target_marks and remaining_marks >= question.marks:
                    selected_questions.append(question)
                    current_marks += question.marks
                    remaining_marks -= question.marks
                    
                if current_marks >= target_marks:
                    break
        
        return selected_questions