import sys
import os
from app import app, db
from question_processor import QuestionPaperGenerator
from models import Question, QuestionDocument, Subject, Unit, Topic

def test_generate_paper():
    with app.app_context():
        generator = QuestionPaperGenerator()
        
        # Test parameters - start with just subject
        subject_id = 1  # Data Structures and Algorithms
        unit_ids = None  # Start with no unit filter
        topic_ids = None  # Start with no topic filter
        total_marks = 5  # Try to get a few questions
        difficulty_distribution = {'easy': 0.3, 'medium': 0.4, 'hard': 0.3}  # Broader distribution
        
        # Get names for better logging
        subject = Subject.query.get(subject_id)
        unit = Unit.query.get(unit_ids[0]) if unit_ids else None
        topic = Topic.query.get(topic_ids[0]) if topic_ids else None
        
        print("\n=== Testing Question Paper Generation ===")
        print(f"Subject: {subject.name if subject else 'All'} (ID: {subject_id})")
        print(f"Unit: {unit.name if unit else 'All'} (ID: {unit_ids[0] if unit_ids else 'None'})")
        print(f"Topic: {topic.name if topic else 'All'} (ID: {topic_ids[0] if topic_ids else 'None'})")
        print(f"Total marks: {total_marks}")
        print(f"Difficulty distribution: {difficulty_distribution}")
        
        # Check available questions first
        query = Question.query.join(QuestionDocument).filter(
            QuestionDocument.subject_id == subject_id,
            QuestionDocument.status == 'approved',
            Question.marks > 0
        )
        
        if unit_ids:
            query = query.filter(Question.unit_id.in_(unit_ids))
        if topic_ids:
            query = query.filter(Question.topic_id.in_(topic_ids))
            
        available_questions = query.all()
        
        print(f"\nFound {len(available_questions)} available questions matching criteria:")
        for q in available_questions:
            unit_name = Unit.query.get(q.unit_id).name if q.unit_id else 'None'
            topic_name = Topic.query.get(q.topic_id).name if q.topic_id else 'None'
            print(f"- ID: {q.id}, Marks: {q.marks}, Difficulty: {q.difficulty_level}")
            print(f"  Unit: {unit_name}, Topic: {topic_name}")
            print(f"  Question: {q.question_text[:100]}...\n")
        
        # Try to generate the paper
        print("\nAttempting to generate question paper...")
        result = generator.generate_question_paper(
            subject_id=subject_id,
            unit_ids=unit_ids,
            topic_ids=topic_ids,
            total_marks=total_marks,
            difficulty_distribution=difficulty_distribution
        )
        
        if result:
            filename, file_path = result
            print(f"\n✅ Success! Generated paper saved to: {file_path}")
            
            # Verify the file exists
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path) / 1024  # KB
                print(f"   File size: {file_size:.2f} KB")
            else:
                print("   Warning: File not found at the specified path!")
                
        else:
            print("\n❌ Failed to generate paper. Possible reasons:")
            print("   - Not enough questions matching the criteria")
            print("   - No questions with the specified difficulty levels")
            print("   - Questions don't add up to the required total marks")
            print("\nCheck the application logs for more details.")

if __name__ == "__main__":
    test_generate_paper()
