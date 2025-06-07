#!/usr/bin/env python3
"""
Create a test PDF with proper metadata for testing the upload functionality.
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import os

def create_test_pdf():
    """Create a test research paper PDF with metadata."""
    filename = "test_paper.pdf"
    
    # Create PDF document
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = "Machine Learning Approaches to Natural Language Processing: A Comprehensive Study"
    title_style = styles['Title']
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 12))
    
    # Authors
    authors = "John Smith, Jane Doe, Michael Johnson"
    author_style = styles['Normal']
    story.append(Paragraph(f"<b>Authors:</b> {authors}", author_style))
    story.append(Spacer(1, 12))
    
    # Abstract
    abstract_title = Paragraph("<b>Abstract</b>", styles['Heading2'])
    story.append(abstract_title)
    story.append(Spacer(1, 6))
    
    abstract_text = """
    This paper presents a comprehensive study of machine learning approaches applied to natural language processing tasks. 
    We explore various techniques including deep learning, transformer models, and traditional statistical methods. 
    Our research demonstrates significant improvements in text classification, sentiment analysis, and language generation tasks. 
    The study evaluates performance across multiple datasets and provides insights into the effectiveness of different approaches 
    for various NLP applications. Results show that transformer-based models achieve state-of-the-art performance while 
    traditional methods remain competitive for specific use cases.
    """
    story.append(Paragraph(abstract_text.strip(), styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Keywords
    keywords_title = Paragraph("<b>Keywords</b>", styles['Heading2'])
    story.append(keywords_title)
    story.append(Spacer(1, 6))
    
    keywords = "machine learning, natural language processing, deep learning, transformers, text classification"
    story.append(Paragraph(keywords, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Introduction
    intro_title = Paragraph("<b>1. Introduction</b>", styles['Heading2'])
    story.append(intro_title)
    story.append(Spacer(1, 6))
    
    intro_text = """
    Natural Language Processing (NLP) has seen tremendous advancement with the introduction of machine learning techniques. 
    This study examines the evolution of NLP methods from traditional rule-based systems to modern deep learning approaches. 
    We focus on practical applications and performance comparisons across different methodologies.
    """
    story.append(Paragraph(intro_text.strip(), styles['Normal']))
    
    # Build PDF
    doc.build(story)
    
    print(f"Test PDF created: {filename}")
    return filename

if __name__ == "__main__":
    create_test_pdf()