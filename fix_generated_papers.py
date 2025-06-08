from app import app, db
from models import GeneratedQuestionPaper, Subject

def fix_generated_papers():
    with app.app_context():
        # Get all generated papers
        papers = GeneratedQuestionPaper.query.all()
        
        for paper in papers:
            # If the paper has a subject_id but the relationship isn't loaded
            if paper.subject_id and not hasattr(paper, 'subject'):
                # Get the subject
                subject = Subject.query.get(paper.subject_id)
                if subject:
                    paper.subject = subject
                    print(f"Updated subject for paper {paper.id} to {subject.name}")
        
        # Commit any changes
        db.session.commit()
        print("Finished updating generated papers")

if __name__ == "__main__":
    fix_generated_papers()
