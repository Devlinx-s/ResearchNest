from app import app, db
from models import Question, QuestionDocument, Subject, Unit, Topic, User
from datetime import datetime, UTC

def create_questions():
    with app.app_context():
        # Get or create the subject and unit
        subject = Subject.query.filter_by(name="Data Structures and Algorithms").first()
        if not subject:
            subject = Subject(name="Data Structures and Algorithms")
            db.session.add(subject)
            db.session.commit()
        
        unit = Unit.query.filter_by(name="Stacks and Queues", subject_id=subject.id).first()
        if not unit:
            unit = Unit(name="Stacks and Queues", subject_id=subject.id)
            db.session.add(unit)
            db.session.commit()
        
        topics = {
            "Stacks": [],
            "Queues": [],
            "Applications": [],
            "Implementation": []
        }
        
        # Create topics if they don't exist
        for topic_name in topics.keys():
            topic = Topic.query.filter_by(name=topic_name, unit_id=unit.id).first()
            if not topic:
                topic = Topic(name=topic_name, unit_id=unit.id)
                db.session.add(topic)
            topics[topic_name] = topic
        db.session.commit()
        
        # Get an admin user to set as uploader
        admin_user = User.query.filter_by(is_admin=True).first()
        if not admin_user:
            print("Error: No admin user found. Please create an admin user first.")
            return
            
        # Create a document to hold these questions
        doc = QuestionDocument(
            title="Data Structures - Stacks and Queues Question Bank",
            filename="stacks_queues.txt",
            original_filename="stacks_queues.txt",
            file_path="/path/to/stacks_queues.txt",
            file_size=1024,  # Placeholder size
            subject_id=subject.id,
            document_type="question_bank",
            status='approved',
            extraction_status='completed',
            extraction_progress=100,
            total_questions=40,
            total_pages=1,
            processed_pages=1,
            uploaded_at=datetime.now(UTC),
            uploader_id=admin_user.id
        )
        db.session.add(doc)
        db.session.commit()
        
        # Questions data
        questions = [
            # Stack Questions (15)
            {"text": "What is the time complexity of push and pop operations in a stack?", "marks": 1, "difficulty": "easy", "topic": "Stacks"},
            {"text": "Explain how you would implement a stack using an array.", "marks": 2, "difficulty": "easy", "topic": "Stacks"},
            {"text": "Write a function to check for balanced parentheses in an expression using stack.", "marks": 3, "difficulty": "medium", "topic": "Stacks"},
            {"text": "What is the difference between array and linked list implementation of stacks?", "marks": 2, "difficulty": "medium", "topic": "Stacks"},
            {"text": "Implement a stack that supports getMin() in O(1) time.", "marks": 3, "difficulty": "hard", "topic": "Stacks"},
            {"text": "How would you use a stack to evaluate postfix expressions?", "marks": 3, "difficulty": "medium", "topic": "Stacks"},
            {"text": "Implement two stacks in a single array efficiently.", "marks": 3, "difficulty": "hard", "topic": "Stacks"},
            
            # Queue Questions (15)
            {"text": "What is the time complexity of enqueue and dequeue operations in a queue?", "marks": 1, "difficulty": "easy", "topic": "Queues"},
            {"text": "Explain how you would implement a queue using two stacks.", "marks": 3, "difficulty": "medium", "topic": "Queues"},
            {"text": "What is a circular queue and what are its advantages?", "marks": 2, "difficulty": "easy", "topic": "Queues"},
            {"text": "Implement a queue using a linked list.", "marks": 2, "difficulty": "medium", "topic": "Queues"},
            {"text": "What is a priority queue and how does it differ from a normal queue?", "marks": 2, "difficulty": "medium", "topic": "Queues"},
            {"text": "Implement a queue that supports getMin() in O(1) time.", "marks": 3, "difficulty": "hard", "topic": "Queues"},
            
            # Application Questions (5)
            {"text": "How can stacks be used in function call management?", "marks": 2, "difficulty": "easy", "topic": "Applications"},
            {"text": "Explain how a queue is used in breadth-first search (BFS).", "marks": 2, "difficulty": "medium", "topic": "Applications"},
            {"text": "How would you use a stack to reverse a string?", "marks": 2, "difficulty": "easy", "topic": "Applications"},
            {"text": "Describe how a queue is used in a print spooler.", "marks": 1, "difficulty": "easy", "topic": "Applications"},
            
            # Implementation Questions (5)
            {"text": "Implement a stack using a queue.", "marks": 3, "difficulty": "medium", "topic": "Implementation"},
            {"text": "How would you implement a queue using only one stack?", "marks": 3, "difficulty": "hard", "topic": "Implementation"},
            {"text": "Implement a deque (double-ended queue) using a circular array.", "marks": 3, "difficulty": "hard", "topic": "Implementation"}
        ]
        
        # Add more questions to reach 40
        additional_questions = [
            # More Stack Questions
            {"text": "What is the difference between stack and queue data structures?", "marks": 1, "difficulty": "easy", "topic": "Stacks"},
            {"text": "How would you reverse a stack using recursion?", "marks": 3, "difficulty": "medium", "topic": "Stacks"},
            {"text": "Implement a function to find the next greater element for every element in an array using stack.", "marks": 3, "difficulty": "hard", "topic": "Stacks"},
            
            # More Queue Questions
            {"text": "What is a deque and how does it differ from a normal queue?", "marks": 1, "difficulty": "easy", "topic": "Queues"},
            {"text": "How would you implement a queue with a fixed-size array?", "marks": 2, "difficulty": "medium", "topic": "Queues"},
            {"text": "Implement a circular queue with a fixed size.", "marks": 3, "difficulty": "medium", "topic": "Queues"},
            
            # More Application Questions
            {"text": "How can stacks be used in undo/redo operations?", "marks": 2, "difficulty": "medium", "topic": "Applications"},
            {"text": "Explain how a stack can be used for expression evaluation.", "marks": 2, "difficulty": "medium", "topic": "Applications"},
            
            # More Implementation Questions
            {"text": "Implement a queue using a circular linked list.", "marks": 3, "difficulty": "hard", "topic": "Implementation"},
            {"text": "How would you implement a stack that can return the minimum element in O(1) time using O(1) extra space?", "marks": 3, "difficulty": "hard", "topic": "Implementation"}
        ]
        
        questions.extend(additional_questions)
        
        # Add questions to database
        for q_data in questions:
            topic = topics[q_data["topic"]]
            question = Question(
                question_text=q_data["text"],
                question_type="theory" if "explain" in q_data["text"].lower() or "what" in q_data["text"].lower() else "programming",
                difficulty_level=q_data["difficulty"],
                marks=q_data["marks"],
                unit_id=unit.id,
                topic_id=topic.id,
                document_id=doc.id,
                created_at=datetime.now(UTC)
            )
            db.session.add(question)
        
        db.session.commit()
        print(f"Successfully added {len(questions)} questions on Stacks and Queues to the database.")

if __name__ == "__main__":
    create_questions()
