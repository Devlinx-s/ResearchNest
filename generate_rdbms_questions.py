from app import app, db
from models import Question, QuestionDocument, Subject, Unit, Topic, User
from datetime import datetime, UTC

def create_questions():
    with app.app_context():
        # Get or create the subject and unit
        subject = Subject.query.filter_by(name="Database Management Systems").first()
        if not subject:
            subject = Subject(name="Database Management Systems")
            db.session.add(subject)
            db.session.commit()
        
        unit = Unit.query.filter_by(name="Relational Model", subject_id=subject.id).first()
        if not unit:
            unit = Unit(name="Relational Model", subject_id=subject.id)
            db.session.add(unit)
            db.session.commit()
        
        topics = {
            "Relational Model Concepts": [],
            "Keys and Constraints": [],
            "Relational Algebra": [],
            "SQL Fundamentals": [],
            "Normalization": [],
            "Transactions": [],
            "Indexing": [],
            "Database Design": []
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
            title="DBMS - Relational Model Question Bank",
            filename="relational_model.txt",
            original_filename="relational_model.txt",
            file_path="/path/to/relational_model.txt",
            file_size=1024,  # Placeholder size
            subject_id=subject.id,
            document_type="question_bank",
            status='approved',
            extraction_status='completed',
            extraction_progress=100,
            total_questions=50,
            total_pages=1,
            processed_pages=1,
            uploaded_at=datetime.now(UTC),
            uploader_id=admin_user.id
        )
        db.session.add(doc)
        db.session.commit()
        
        # Questions data
        questions = [
            # Relational Model Concepts (8 questions)
            {"text": "What are the fundamental concepts of the relational model?", "marks": 2, "difficulty": "easy", "topic": "Relational Model Concepts"},
            {"text": "Explain the difference between a relation and a relationship in the relational model.", "marks": 2, "difficulty": "medium", "topic": "Relational Model Concepts"},
            {"text": "What are the properties of a relation in the relational model?", "marks": 2, "difficulty": "easy", "topic": "Relational Model Concepts"},
            
            # Keys and Constraints (8 questions)
            {"text": "What is a superkey, candidate key, and primary key?", "marks": 2, "difficulty": "easy", "topic": "Keys and Constraints"},
            {"text": "Explain the difference between primary key and unique key constraints.", "marks": 2, "difficulty": "easy", "topic": "Keys and Constraints"},
            {"text": "What are foreign key constraints and referential integrity?", "marks": 2, "difficulty": "medium", "topic": "Keys and Constraints"},
            
            # Relational Algebra (8 questions)
            {"text": "What are the fundamental operations in relational algebra?", "marks": 2, "difficulty": "easy", "topic": "Relational Algebra"},
            {"text": "Write a relational algebra expression to find all customers who have placed an order.", "marks": 3, "difficulty": "medium", "topic": "Relational Algebra"},
            
            # SQL Fundamentals (8 questions)
            {"text": "What is the difference between WHERE and HAVING clauses in SQL?", "marks": 2, "difficulty": "easy", "topic": "SQL Fundamentals"},
            {"text": "Write a SQL query to find the second highest salary from an Employee table.", "marks": 3, "difficulty": "medium", "topic": "SQL Fundamentals"},
            
            # Normalization (6 questions)
            {"text": "What is database normalization and why is it important?", "marks": 2, "difficulty": "easy", "topic": "Normalization"},
            {"text": "Explain the differences between 1NF, 2NF, and 3NF.", "marks": 3, "difficulty": "medium", "topic": "Normalization"},
            
            # Transactions (5 questions)
            {"text": "What are the ACID properties of database transactions?", "marks": 2, "difficulty": "easy", "topic": "Transactions"},
            
            # Indexing (4 questions)
            {"text": "What are database indexes and how do they improve query performance?", "marks": 2, "difficulty": "medium", "topic": "Indexing"},
            
            # Database Design (3 questions)
            {"text": "What is the difference between logical and physical database design?", "marks": 2, "difficulty": "medium", "topic": "Database Design"}
        ]
        
        # Additional questions to reach 50
        additional_questions = [
            # More Relational Model Concepts
            {"text": "What is a relation schema and relation instance?", "marks": 2, "difficulty": "easy", "topic": "Relational Model Concepts"},
            {"text": "Explain the difference between a tuple and an attribute.", "marks": 1, "difficulty": "easy", "topic": "Relational Model Concepts"},
            
            # More Keys and Constraints
            {"text": "What is a composite key and when would you use it?", "marks": 2, "difficulty": "easy", "topic": "Keys and Constraints"},
            {"text": "Explain the concept of a surrogate key.", "marks": 1, "difficulty": "easy", "topic": "Keys and Constraints"},
            
            # More Relational Algebra
            {"text": "What is the difference between natural join and equi-join?", "marks": 2, "difficulty": "medium", "topic": "Relational Algebra"},
            {"text": "Write a relational algebra expression for division operation.", "marks": 3, "difficulty": "hard", "topic": "Relational Algebra"},
            
            # More SQL Fundamentals
            {"text": "Explain the difference between INNER JOIN, LEFT JOIN, RIGHT JOIN, and FULL OUTER JOIN.", "marks": 3, "difficulty": "medium", "topic": "SQL Fundamentals"},
            {"text": "What are SQL views and what are their advantages?", "marks": 2, "difficulty": "easy", "topic": "SQL Fundamentals"},
            {"text": "Write a SQL query to find duplicate emails in a table.", "marks": 2, "difficulty": "easy", "topic": "SQL Fundamentals"},
            
            # More Normalization
            {"text": "What is BCNF and how is it different from 3NF?", "marks": 3, "difficulty": "hard", "topic": "Normalization"},
            {"text": "What are the advantages and disadvantages of normalization?", "marks": 2, "difficulty": "medium", "topic": "Normalization"},
            
            # More Transactions
            {"text": "What is a deadlock and how can it be prevented?", "marks": 3, "difficulty": "hard", "topic": "Transactions"},
            {"text": "Explain the concept of transaction isolation levels.", "marks": 3, "difficulty": "hard", "topic": "Transactions"},
            
            # More Indexing
            {"text": "What is the difference between clustered and non-clustered indexes?", "marks": 2, "difficulty": "medium", "topic": "Indexing"},
            
            # More Database Design
            {"text": "What is an ERD and how is it used in database design?", "marks": 2, "difficulty": "easy", "topic": "Database Design"},
            
            # Additional questions from various topics
            {"text": "What is a stored procedure and what are its advantages?", "marks": 2, "difficulty": "medium", "topic": "SQL Fundamentals"},
            {"text": "Explain the concept of data independence in DBMS.", "marks": 2, "difficulty": "medium", "topic": "Relational Model Concepts"},
            {"text": "What are the different types of joins in SQL?", "marks": 2, "difficulty": "easy", "topic": "SQL Fundamentals"},
            {"text": "What is a trigger in SQL and when would you use it?", "marks": 2, "difficulty": "medium", "topic": "SQL Fundamentals"},
            {"text": "Explain the difference between DELETE, TRUNCATE, and DROP commands.", "marks": 2, "difficulty": "easy", "topic": "SQL Fundamentals"},
            {"text": "What is a subquery and what are its types?", "marks": 2, "difficulty": "medium", "topic": "SQL Fundamentals"},
            {"text": "Explain the concept of database normalization with an example.", "marks": 3, "difficulty": "medium", "topic": "Normalization"},
            {"text": "What is a transaction log and why is it important?", "marks": 2, "difficulty": "medium", "topic": "Transactions"},
            {"text": "What are the different types of database users?", "marks": 1, "difficulty": "easy", "topic": "Relational Model Concepts"},
            {"text": "Explain the concept of data warehousing.", "marks": 2, "difficulty": "medium", "topic": "Database Design"}
        ]
        
        questions.extend(additional_questions)
        
        # Add questions to database
        for q_data in questions:
            topic = topics[q_data["topic"]]
            question = Question(
                question_text=q_data["text"],
                question_type="theory" if "explain" in q_data["text"].lower() or "what" in q_data["text"].lower() or "define" in q_data["text"].lower() else "programming",
                difficulty_level=q_data["difficulty"],
                marks=q_data["marks"],
                unit_id=unit.id,
                topic_id=topic.id,
                document_id=doc.id,
                created_at=datetime.now(UTC)
            )
            db.session.add(question)
        
        db.session.commit()
        print(f"Successfully added {len(questions)} questions on Relational Model to the database.")

if __name__ == "__main__":
    create_questions()
