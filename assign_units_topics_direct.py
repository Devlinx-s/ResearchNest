import random
import sqlite3
from pathlib import Path

def assign_units_topics():
    # Path to the database
    db_path = Path('instance/researchnest.db')
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    
    try:
        # Connect to the database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all questions
        cursor.execute("SELECT id FROM questions")
        questions = cursor.fetchall()
        
        if not questions:
            print("No questions found in the database.")
            return
            
        # Get all units
        cursor.execute("SELECT id FROM units")
        units = cursor.fetchall()
        
        if not units:
            print("No units found in the database.")
            return
            
        # Get all topics with their unit_id
        cursor.execute("SELECT id, unit_id FROM topics")
        topics = cursor.fetchall()
        
        if not topics:
            print("No topics found in the database.")
            return
        
        # Group topics by unit_id
        topics_by_unit = {}
        for topic_id, unit_id in topics:
            if unit_id not in topics_by_unit:
                topics_by_unit[unit_id] = []
            topics_by_unit[unit_id].append(topic_id)
        
        # Update questions with random units and topics
        updated_count = 0
        for (question_id,) in questions:
            # Randomly select a unit with topics
            unit_id = random.choice(list(topics_by_unit.keys()))
            
            # Randomly select a topic from the unit
            topic_id = random.choice(topics_by_unit[unit_id])
            
            # Update the question
            cursor.execute(
                "UPDATE questions SET unit_id = ?, topic_id = ? WHERE id = ?",
                (unit_id, topic_id, question_id)
            )
            updated_count += 1
        
        # Commit changes
        conn.commit()
        print(f"Successfully updated {updated_count} questions with random units and topics.")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    assign_units_topics()
