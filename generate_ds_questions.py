from app import app, db
from models import Question, QuestionDocument, Subject, Unit, Topic, User
from datetime import datetime

def create_questions():
    with app.app_context():
        # Get or create the subject, unit, and topic
        subject = Subject.query.filter_by(name="Data Structures and Algorithms").first()
        if not subject:
            subject = Subject(name="Data Structures and Algorithms")
            db.session.add(subject)
            db.session.commit()
        
        unit = Unit.query.filter_by(name="Arrays and Linked Lists", subject_id=subject.id).first()
        if not unit:
            unit = Unit(name="Arrays and Linked Lists", subject_id=subject.id)
            db.session.add(unit)
            db.session.commit()
        
        topics = {
            "Array Operations": [],
            "Singly Linked Lists": [],
            "Doubly Linked Lists": [],
            "Circular Linked Lists": []
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
            title="Data Structures - Arrays and Linked Lists Question Bank",
            filename="ds_arrays_linked_lists.txt",
            original_filename="ds_arrays_linked_lists.txt",
            file_path="/path/to/ds_arrays_linked_lists.txt",
            file_size=1024,  # Placeholder size
            subject_id=subject.id,
            document_type="question_bank",
            status='approved',
            extraction_status='completed',
            extraction_progress=100,
            total_questions=50,
            total_pages=1,
            processed_pages=1,
            uploaded_at=datetime.utcnow(),
            uploader_id=admin_user.id
        )
        db.session.add(doc)
        db.session.commit()
        
        # Questions data
        questions = [
            # Array Operations (15 questions)
            {"text": "What is the time complexity of accessing an element in an array by index?", "marks": 1, "difficulty": "easy", "topic": "Array Operations"},
            {"text": "Explain the difference between static and dynamic arrays.", "marks": 2, "difficulty": "medium", "topic": "Array Operations"},
            {"text": "Write a function to find the second largest element in an unsorted array.", "marks": 3, "difficulty": "medium", "topic": "Array Operations"},
            {"text": "What is the time complexity of inserting an element at the beginning of an array?", "marks": 1, "difficulty": "easy", "topic": "Array Operations"},
            {"text": "How would you find duplicate elements in an array in O(n) time and O(1) space?", "marks": 3, "difficulty": "hard", "topic": "Array Operations"},
            
            # Singly Linked Lists (15 questions)
            {"text": "What is the time complexity of inserting a node at the beginning of a singly linked list?", "marks": 1, "difficulty": "easy", "topic": "Singly Linked Lists"},
            {"text": "Write a function to detect a loop in a singly linked list.", "marks": 3, "difficulty": "medium", "topic": "Singly Linked Lists"},
            {"text": "Explain how you would reverse a singly linked list.", "marks": 2, "difficulty": "medium", "topic": "Singly Linked Lists"},
            {"text": "What is the time complexity of searching for an element in a singly linked list?", "marks": 1, "difficulty": "easy", "topic": "Singly Linked Lists"},
            {"text": "How would you find the middle element of a singly linked list in one pass?", "marks": 2, "difficulty": "medium", "topic": "Singly Linked Lists"},
            
            # Doubly Linked Lists (10 questions)
            {"text": "What are the advantages of a doubly linked list over a singly linked list?", "marks": 2, "difficulty": "easy", "topic": "Doubly Linked Lists"},
            {"text": "Write a function to delete a node from a doubly linked list.", "marks": 3, "difficulty": "medium", "topic": "Doubly Linked Lists"},
            {"text": "What is the time complexity of inserting a node after a given node in a doubly linked list?", "marks": 1, "difficulty": "easy", "topic": "Doubly Linked Lists"},
            
            # Circular Linked Lists (10 questions)
            {"text": "What is a circular linked list and what are its applications?", "marks": 2, "difficulty": "easy", "topic": "Circular Linked Lists"},
            {"text": "Write a function to check if a linked list is circular.", "marks": 3, "difficulty": "medium", "topic": "Circular Linked Lists"},
            {"text": "What is the advantage of using a circular linked list over a regular linked list?", "marks": 1, "difficulty": "easy", "topic": "Circular Linked Lists"}
        ]
        
        # Add more questions to reach 50
        # Array Operations additional questions
        array_questions = [
            {"text": "Implement a function to rotate an array to the right by k steps.", "marks": 3, "difficulty": "medium"},
            {"text": "Find the maximum subarray sum in an array of integers.", "marks": 3, "difficulty": "medium"},
            {"text": "Given an array of 0s, 1s and 2s, sort the array in O(n) time.", "marks": 3, "difficulty": "medium"},
            {"text": "Find the missing number in an array of n-1 integers containing 1 to n.", "marks": 2, "difficulty": "easy"},
            {"text": "Find all pairs in an array that sum to a given value.", "marks": 2, "difficulty": "medium"},
            {"text": "Find the majority element in an array (appears more than n/2 times).", "marks": 2, "difficulty": "medium"},
            {"text": "Find the largest subarray with equal number of 0s and 1s.", "marks": 3, "difficulty": "hard"},
            {"text": "Find the maximum product subarray in an array.", "marks": 3, "difficulty": "hard"},
            {"text": "Find the smallest positive integer missing from an unsorted array.", "marks": 3, "difficulty": "hard"},
            {"text": "Find the kth smallest element in an unsorted array.", "marks": 3, "difficulty": "medium"}
        ]
        
        # Singly Linked List additional questions
        sll_questions = [
            {"text": "Write a function to find the intersection point of two singly linked lists.", "marks": 3, "difficulty": "medium"},
            {"text": "Remove duplicates from a sorted linked list.", "marks": 2, "difficulty": "easy"},
            {"text": "Write a function to get the nth node from the end of a linked list.", "marks": 2, "difficulty": "easy"},
            {"text": "Delete a node when only the pointer to that node is given.", "marks": 2, "difficulty": "medium"},
            {"text": "Write a function to segregate even and odd nodes in a linked list.", "marks": 3, "difficulty": "medium"},
            {"text": "Find the starting node of the loop in a linked list.", "marks": 3, "difficulty": "hard"},
            {"text": "Merge two sorted linked lists.", "marks": 3, "difficulty": "medium"},
            {"text": "Add two numbers represented by linked lists.", "marks": 3, "difficulty": "medium"},
            {"text": "Check if a linked list is a palindrome.", "marks": 3, "difficulty": "medium"},
            {"text": "Flatten a multilevel doubly linked list.", "marks": 3, "difficulty": "hard"}
        ]
        
        # Add all questions to the main questions list
        for q in array_questions:
            q["topic"] = "Array Operations"
            questions.append(q)
            
        for q in sll_questions:
            q["topic"] = "Singly Linked Lists"
            questions.append(q)
        
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
                created_at=datetime.utcnow()
            )
            db.session.add(question)
        
        db.session.commit()
        print(f"Successfully added {len(questions)} questions to the database.")

if __name__ == "__main__":
    create_questions()
