import random
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from models import Question, Unit, Topic
from app import create_app, db

def assign_units_topics():
    # Create app and database session
    app = create_app()
    with app.app_context():
        # Get all questions
        questions = Question.query.all()
        
        # Get all units
        units = Unit.query.all()
        if not units:
            print("No units found in the database.")
            return
            
        # Get all topics grouped by unit_id
        topics_by_unit = {}
        for unit in units:
            topics = Topic.query.filter_by(unit_id=unit.id).all()
            if topics:
                topics_by_unit[unit.id] = topics
        
        if not topics_by_unit:
            print("No topics found in the database.")
            return
        
        # Update questions with random units and topics
        updated_count = 0
        for question in questions:
            # Skip if already has a unit and topic
            if question.unit_id and question.topic_id:
                continue
                
            # Randomly select a unit with topics
            unit_id = random.choice(list(topics_by_unit.keys()))
            topics = topics_by_unit[unit_id]
            
            # Randomly select a topic from the unit
            topic = random.choice(topics)
            
            # Update the question
            question.unit_id = unit_id
            question.topic_id = topic.id
            updated_count += 1
        
        # Commit changes
        db.session.commit()
        print(f"Successfully updated {updated_count} questions with random units and topics.")

if __name__ == "__main__":
    assign_units_topics()
