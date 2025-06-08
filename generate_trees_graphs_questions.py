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
        
        unit = Unit.query.filter_by(name="Trees and Graphs", subject_id=subject.id).first()
        if not unit:
            unit = Unit(name="Trees and Graphs", subject_id=subject.id)
            db.session.add(unit)
            db.session.commit()
        
        topics = {
            "Binary Trees": [],
            "Binary Search Trees": [],
            "Balanced Trees": [],
            "Heaps": [],
            "Graphs": [],
            "Graph Traversals": [],
            "Shortest Paths": [],
            "Minimum Spanning Trees": []
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
            title="Data Structures - Trees and Graphs Question Bank",
            filename="trees_graphs.txt",
            original_filename="trees_graphs.txt",
            file_path="/path/to/trees_graphs.txt",
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
            # Binary Trees (8 questions)
            {"text": "What is the difference between a full binary tree and a complete binary tree?", "marks": 2, "difficulty": "easy", "topic": "Binary Trees"},
            {"text": "Write a function to find the height of a binary tree.", "marks": 2, "difficulty": "easy", "topic": "Binary Trees"},
            {"text": "Implement level order traversal of a binary tree.", "marks": 3, "difficulty": "medium", "topic": "Binary Trees"},
            {"text": "How would you check if two binary trees are identical?", "marks": 2, "difficulty": "easy", "topic": "Binary Trees"},
            {"text": "Write a function to find the lowest common ancestor of two nodes in a binary tree.", "marks": 3, "difficulty": "medium", "topic": "Binary Trees"},
            {"text": "How would you serialize and deserialize a binary tree?", "marks": 3, "difficulty": "hard", "topic": "Binary Trees"},
            
            # Binary Search Trees (7 questions)
            {"text": "What are the properties of a Binary Search Tree?", "marks": 1, "difficulty": "easy", "topic": "Binary Search Trees"},
            {"text": "Write a function to validate if a binary tree is a BST.", "marks": 3, "difficulty": "medium", "topic": "Binary Search Trees"},
            {"text": "How would you find the kth smallest element in a BST?", "marks": 2, "difficulty": "medium", "topic": "Binary Search Trees"},
            {"text": "Implement an iterator for a BST that has next() and hasNext() methods.", "marks": 3, "difficulty": "hard", "topic": "Binary Search Trees"},
            
            # Balanced Trees (5 questions)
            {"text": "What is an AVL tree and how does it maintain balance?", "marks": 2, "difficulty": "medium", "topic": "Balanced Trees"},
            {"text": "Explain the concept of Red-Black trees.", "marks": 2, "difficulty": "hard", "topic": "Balanced Trees"},
            {"text": "Compare AVL trees and Red-Black trees in terms of balancing and performance.", "marks": 2, "difficulty": "hard", "topic": "Balanced Trees"},
            
            # Heaps (5 questions)
            {"text": "What is a binary heap and what are its properties?", "marks": 1, "difficulty": "easy", "topic": "Heaps"},
            {"text": "Implement a min-heap with insert and extractMin operations.", "marks": 3, "difficulty": "medium", "topic": "Heaps"},
            {"text": "How would you find the k largest elements in an array using a heap?", "marks": 2, "difficulty": "medium", "topic": "Heaps"},
            
            # Graphs (8 questions)
            {"text": "What are the different ways to represent a graph? Compare their space and time complexities.", "marks": 2, "difficulty": "easy", "topic": "Graphs"},
            {"text": "What is the difference between BFS and DFS?", "marks": 2, "difficulty": "easy", "topic": "Graphs"},
            {"text": "How would you detect a cycle in a directed graph?", "marks": 3, "difficulty": "medium", "topic": "Graphs"},
            
            # Graph Traversals (7 questions)
            {"text": "Implement BFS traversal for a graph.", "marks": 3, "difficulty": "medium", "topic": "Graph Traversals"},
            {"text": "Implement DFS traversal for a graph using both recursive and iterative approaches.", "marks": 3, "difficulty": "medium", "topic": "Graph Traversals"},
            {"text": "How would you find connected components in an undirected graph?", "marks": 2, "difficulty": "medium", "topic": "Graph Traversals"},
            
            # Shortest Paths (5 questions)
            {"text": "Explain Dijkstra's algorithm for finding shortest paths.", "marks": 2, "difficulty": "medium", "topic": "Shortest Paths"},
            {"text": "What is the Bellman-Ford algorithm and when would you use it?", "marks": 2, "difficulty": "hard", "topic": "Shortest Paths"},
            
            # Minimum Spanning Trees (5 questions)
            {"text": "What is a minimum spanning tree?", "marks": 1, "difficulty": "easy", "topic": "Minimum Spanning Trees"},
            {"text": "Compare Kruskal's and Prim's algorithms for finding MST.", "marks": 2, "difficulty": "medium", "topic": "Minimum Spanning Trees"}
        ]
        
        # Additional questions to reach 50
        additional_questions = [
            # More Binary Trees
            {"text": "How would you convert a binary tree to its mirror?", "marks": 2, "difficulty": "medium", "topic": "Binary Trees"},
            {"text": "Find the diameter of a binary tree.", "marks": 3, "difficulty": "medium", "topic": "Binary Trees"},
            
            # More BST
            {"text": "Convert a sorted array to a balanced BST.", "marks": 3, "difficulty": "medium", "topic": "Binary Search Trees"},
            {"text": "Find the in-order successor of a node in a BST.", "marks": 3, "difficulty": "medium", "topic": "Binary Search Trees"},
            
            # More Balanced Trees
            {"text": "Perform left and right rotations in an AVL tree.", "marks": 3, "difficulty": "hard", "topic": "Balanced Trees"},
            
            # More Heaps
            {"text": "Implement heap sort algorithm.", "marks": 3, "difficulty": "medium", "topic": "Heaps"},
            
            # More Graphs
            {"text": "Implement topological sort for a DAG.", "marks": 3, "difficulty": "medium", "topic": "Graphs"},
            {"text": "How would you find strongly connected components in a directed graph?", "marks": 3, "difficulty": "hard", "topic": "Graphs"},
            
            # More Graph Traversals
            {"text": "Find the number of islands in a 2D grid using DFS.", "marks": 3, "difficulty": "medium", "topic": "Graph Traversals"},
            
            # More Shortest Paths
            {"text": "Implement Floyd-Warshall algorithm for all pairs shortest paths.", "marks": 3, "difficulty": "hard", "topic": "Shortest Paths"},
            
            # More MST
            {"text": "Implement Kruskal's algorithm using Union-Find data structure.", "marks": 3, "difficulty": "hard", "topic": "Minimum Spanning Trees"}
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
        print(f"Successfully added {len(questions)} questions on Trees and Graphs to the database.")

if __name__ == "__main__":
    create_questions()
