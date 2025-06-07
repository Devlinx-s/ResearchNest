from flask import render_template, request, flash, redirect, url_for, send_file, jsonify, session
from flask_login import current_user, login_user, logout_user
from sqlalchemy import desc, func
from datetime import datetime
import os
import json

from app import app, db
from auth import require_login, require_admin
from models import (ResearchPaper, Department, User, DownloadLog, Keyword, 
                   QuestionDocument, Question, Subject, Unit, Topic, GeneratedQuestionPaper)
from forms import (UploadPaperForm, SearchForm, UserProfileForm, LoginForm, SignupForm, 
                  ChangePasswordForm, UploadQuestionDocumentForm, GenerateQuestionPaperForm,
                  SubjectManagementForm, UnitManagementForm, TopicManagementForm)
from utils import extract_pdf_metadata, extract_keywords_from_text, save_uploaded_file, format_file_size
from question_processor import QuestionExtractor, QuestionPaperGenerator

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login with email and password."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.first_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = SignupForm()
    if form.validate_on_submit():
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email address already registered. Please use a different email.', 'error')
            return render_template('signup.html', form=form)
        
        # Create new user
        user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data or '',
            department=form.department.data or '',
            year=form.year.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html', form=form)

@app.route('/logout')
def logout():
    """Logout user."""
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/')
def index():
    """Landing page - shows recent papers if logged in, otherwise landing page."""
    if current_user.is_authenticated:
        # Show recent papers and statistics
        recent_papers = ResearchPaper.query.filter_by(status='approved').order_by(desc(ResearchPaper.uploaded_at)).limit(5).all()
        total_papers = ResearchPaper.query.filter_by(status='approved').count()
        total_downloads = db.session.query(func.sum(ResearchPaper.download_count)).scalar() or 0
        
        # Get popular papers
        popular_papers = ResearchPaper.query.filter_by(status='approved').order_by(desc(ResearchPaper.download_count)).limit(5).all()
        
        return render_template('index.html', 
                             recent_papers=recent_papers,
                             popular_papers=popular_papers,
                             total_papers=total_papers,
                             total_downloads=total_downloads)
    else:
        return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
@require_login
def upload_paper():
    """Upload a new research paper."""
    form = UploadPaperForm()
    
    if form.validate_on_submit():
        file = form.file.data
        
        # Get department info
        department = Department.query.get(form.department_id.data)
        if not department:
            flash('Invalid department selected.', 'error')
            return render_template('upload.html', form=form)
        
        # Save file
        filename, file_path = save_uploaded_file(file, None, department.name, form.publication_year.data or datetime.now().year)
        
        if not filename:
            flash('Error saving file. Please try again.', 'error')
            return render_template('upload.html', form=form)
        
        # Extract metadata from PDF
        extracted_metadata = extract_pdf_metadata(file_path)
        
        # Use form data or extracted metadata
        title = form.title.data.strip() if form.title.data else extracted_metadata.get('title', '')
        authors = form.authors.data.strip() if form.authors.data else extracted_metadata.get('authors', '')
        keywords = form.keywords.data.strip() if form.keywords.data else extracted_metadata.get('keywords', '')
        abstract = form.abstract.data.strip() if form.abstract.data else extracted_metadata.get('abstract', '')
        
        # Extract keywords from abstract if no keywords provided
        if not keywords and abstract:
            extracted_keywords = extract_keywords_from_text(abstract)
            keywords = ', '.join(extracted_keywords[:5])
        
        # Validate required fields
        if not title:
            flash('Title is required. Please provide a title for your paper.', 'error')
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            return render_template('upload.html', form=form)
        
        if not authors:
            flash('Authors field is required. Please provide author information.', 'error')
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            return render_template('upload.html', form=form)
        
        # Create research paper record
        paper = ResearchPaper(
            title=title,
            authors=authors,
            abstract=abstract or '',
            keywords=keywords or '',
            filename=filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            publication_year=form.publication_year.data or datetime.now().year,
            department_id=department.id,
            uploader_id=current_user.id,
            status='approved'  # Auto-approve for simplicity
        )
        
        db.session.add(paper)
        db.session.commit()
        
        # Update keyword frequency
        if keywords:
            keyword_list = [k.strip().lower() for k in keywords.split(',') if k.strip()]
            for keyword_text in keyword_list:
                keyword = Keyword.query.filter_by(name=keyword_text).first()
                if keyword:
                    keyword.frequency += 1
                else:
                    keyword = Keyword(name=keyword_text, frequency=1)
                    db.session.add(keyword)
        
        db.session.commit()
        
        flash('Paper uploaded successfully!', 'success')
        return redirect(url_for('paper_detail', id=paper.id))
    
    return render_template('upload.html', form=form)

@app.route('/search')
def search():
    """Search and filter research papers."""
    form = SearchForm(request.args)
    papers = []
    total_results = 0
    
    # Build query
    query = ResearchPaper.query.filter_by(status='approved')
    
    # Apply filters
    if form.query.data:
        search_term = f"%{form.query.data}%"
        query = query.filter(
            db.or_(
                ResearchPaper.title.ilike(search_term),
                ResearchPaper.authors.ilike(search_term),
                ResearchPaper.keywords.ilike(search_term),
                ResearchPaper.abstract.ilike(search_term)
            )
        )
    
    if form.department_id.data and form.department_id.data != 0:
        query = query.filter_by(department_id=form.department_id.data)
    
    if form.year_from.data:
        query = query.filter(ResearchPaper.publication_year >= form.year_from.data)
    
    if form.year_to.data:
        query = query.filter(ResearchPaper.publication_year <= form.year_to.data)
    
    if form.keywords.data:
        keyword_terms = [k.strip() for k in form.keywords.data.split(',')]
        for term in keyword_terms:
            if term:
                query = query.filter(ResearchPaper.keywords.ilike(f"%{term}%"))
    
    # Execute query with pagination
    page = request.args.get('page', 1, type=int)
    papers_pagination = query.order_by(desc(ResearchPaper.uploaded_at)).paginate(
        page=page, per_page=10, error_out=False
    )
    
    papers = papers_pagination.items
    total_results = papers_pagination.total
    
    return render_template('search.html', 
                         form=form, 
                         papers=papers, 
                         pagination=papers_pagination,
                         total_results=total_results,
                         format_file_size=format_file_size)

@app.route('/paper/<int:id>')
def paper_detail(id):
    """View paper details."""
    paper = ResearchPaper.query.get_or_404(id)
    
    # Check if paper is approved or user has access
    if paper.status != 'approved':
        if not current_user.is_authenticated:
            return render_template('403.html'), 403
        if paper.uploader_id != current_user.id and not current_user.is_admin:
            return render_template('403.html'), 403
    
    return render_template('paper_detail.html', paper=paper, format_file_size=format_file_size)

@app.route('/download/<int:id>')
@require_login
def download_paper(id):
    """Download a research paper and track the download."""
    paper = ResearchPaper.query.get_or_404(id)
    
    # Check if paper is approved or user is owner/admin
    if paper.status != 'approved' and paper.uploader_id != current_user.id and not current_user.is_admin:
        return render_template('403.html'), 403
    
    # Check if file exists
    if not os.path.exists(paper.file_path):
        flash('File not found. Please contact administrator.', 'error')
        return redirect(url_for('paper_detail', id=id))
    
    # Log the download
    download_log = DownloadLog(
        paper_id=paper.id,
        user_id=current_user.id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', '')[:500]
    )
    db.session.add(download_log)
    
    # Increment download count
    paper.download_count += 1
    db.session.commit()
    
    # Send file
    return send_file(paper.file_path, 
                     as_attachment=True, 
                     download_name=paper.original_filename,
                     mimetype='application/pdf')

@app.route('/my-papers')
@require_login
def my_papers():
    """View user's uploaded papers."""
    papers = ResearchPaper.query.filter_by(uploader_id=current_user.id).order_by(desc(ResearchPaper.uploaded_at)).all()
    return render_template('my_papers.html', papers=papers, format_file_size=format_file_size)

@app.route('/profile', methods=['GET', 'POST'])
@require_login
def profile():
    """User profile page."""
    form = UserProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.department = form.department.data
        current_user.year = form.year.data
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', form=form, user=current_user)

@app.route('/change-password', methods=['GET', 'POST'])
@require_login
def change_password():
    """Change user password."""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Current password is incorrect.', 'error')
    
    return render_template('change_password.html', form=form)

# Admin routes
@app.route('/admin')
@require_admin
def admin_dashboard():
    """Admin dashboard with analytics."""
    # Get statistics
    total_papers = ResearchPaper.query.count()
    total_users = User.query.count()
    total_downloads = db.session.query(func.sum(ResearchPaper.download_count)).scalar() or 0
    pending_papers = ResearchPaper.query.filter_by(status='pending').count()
    
    # Get recent papers
    recent_papers = ResearchPaper.query.order_by(desc(ResearchPaper.uploaded_at)).limit(5).all()
    
    return render_template('admin_dashboard.html',
                         total_papers=total_papers,
                         total_users=total_users,
                         total_downloads=total_downloads,
                         pending_papers=pending_papers,
                         recent_papers=recent_papers)

@app.route('/admin/papers')
@require_admin
def admin_papers():
    """Admin view of all papers."""
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    
    query = ResearchPaper.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    papers_pagination = query.order_by(desc(ResearchPaper.uploaded_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin_papers.html', 
                         papers=papers_pagination,
                         status_filter=status_filter,
                         format_file_size=format_file_size)

@app.route('/admin/users')
@require_admin
def admin_users():
    """Admin view of all users."""
    page = request.args.get('page', 1, type=int)
    users_pagination = User.query.order_by(desc(User.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    form = SignupForm()
    return render_template('admin_users.html', 
                         users=users_pagination,
                         form=form)

@app.route('/admin/users/add', methods=['GET', 'POST'])
@require_admin
def admin_add_user():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email address already registered. Please use a different email.', 'error')
            return redirect(url_for('admin_users'))
        user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data or '',
            department=form.department.data or '',
            year=form.year.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User added successfully!', 'success')
        return redirect(url_for('admin_users'))
    # If GET or invalid POST, show the users page with the form and errors
    page = request.args.get('page', 1, type=int)
    users_pagination = User.query.order_by(desc(User.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin_users.html', users=users_pagination, form=form)

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@require_admin
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin_users'))
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/approve/<int:id>')
@require_admin
def approve_paper(id):
    """Approve a research paper."""
    paper = ResearchPaper.query.get_or_404(id)
    paper.status = 'approved'
    paper.approved_at = datetime.now()
    db.session.commit()
    flash(f'Paper "{paper.title}" approved successfully!', 'success')
    return redirect(url_for('admin_papers'))

@app.route('/admin/reject/<int:id>')
@require_admin
def reject_paper(id):
    """Reject a research paper."""
    paper = ResearchPaper.query.get_or_404(id)
    paper.status = 'rejected'
    db.session.commit()
    flash(f'Paper "{paper.title}" rejected.', 'warning')
    return redirect(url_for('admin_papers'))

@app.route('/admin/toggle-admin/<user_id>')
@require_admin
def toggle_user_admin(user_id):
    """Toggle admin status for a user."""
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin privileges {status} for {user.email}', 'success')
    return redirect(url_for('admin_users'))

# API endpoints for analytics
@app.route('/api/analytics/papers-by-department')
@require_admin
def api_papers_by_department():
    """API endpoint for papers by department chart."""
    results = db.session.query(
        Department.name,
        func.count(ResearchPaper.id).label('count')
    ).join(ResearchPaper, Department.id == ResearchPaper.department_id)\
     .filter(ResearchPaper.status == 'approved')\
     .group_by(Department.name)\
     .all()
    
    data = {
        'labels': [result.name for result in results],
        'data': [result.count for result in results]
    }
    return jsonify(data)

@app.route('/api/analytics/uploads-by-month')
@require_admin
def api_uploads_by_month():
    """API endpoint for uploads by month chart."""
    results = db.session.query(
        func.date_trunc('month', ResearchPaper.uploaded_at).label('month'),
        func.count(ResearchPaper.id).label('count')
    ).filter(ResearchPaper.status == 'approved')\
     .group_by(func.date_trunc('month', ResearchPaper.uploaded_at))\
     .order_by('month')\
     .all()
    
    data = {
        'labels': [result.month.strftime('%Y-%m') for result in results],
        'data': [result.count for result in results]
    }
    return jsonify(data)

@app.route('/api/analytics/downloads-by-month')
@require_admin
def api_downloads_by_month():
    """API endpoint for downloads by month chart."""
    results = db.session.query(
        func.date_trunc('month', DownloadLog.downloaded_at).label('month'),
        func.count(DownloadLog.id).label('count')
    ).group_by(func.date_trunc('month', DownloadLog.downloaded_at))\
     .order_by('month')\
     .all()
    
    data = {
        'labels': [result.month.strftime('%Y-%m') for result in results],
        'data': [result.count for result in results]
    }
    return jsonify(data)

@app.route('/api/analytics/top-keywords')
@require_admin
def api_top_keywords():
    """API endpoint for top keywords chart."""
    keywords = Keyword.query.order_by(desc(Keyword.frequency)).limit(10).all()
    
    data = {
        'labels': [keyword.name for keyword in keywords],
        'data': [keyword.frequency for keyword in keywords]
    }
    return jsonify(data)

# Question Document Management Routes

@app.route('/questions')
@require_login
def question_documents():
    """View all question documents."""
    page = request.args.get('page', 1, type=int)
    subject_id = request.args.get('subject_id', type=int)
    
    query = QuestionDocument.query
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
    
    documents = query.order_by(desc(QuestionDocument.uploaded_at)).paginate(
        page=page, per_page=10, error_out=False
    )
    
    subjects = Subject.query.all()
    return render_template('questions/list.html', documents=documents, subjects=subjects)

@app.route('/questions/upload', methods=['GET', 'POST'])
@require_login
def upload_question_document():
    """Upload a new question document."""
    form = UploadQuestionDocumentForm()
    
    if form.validate_on_submit():
        file = form.file.data
        subject = Subject.query.get(form.subject_id.data)
        
        if not subject:
            flash('Invalid subject selected.', 'error')
            return render_template('questions/upload.html', form=form)
        
        # Save file
        filename, file_path = save_question_document_file(file, subject, form.academic_year.data)
        
        if not filename:
            flash('Error saving file. Please try again.', 'error')
            return render_template('questions/upload.html', form=form)
        
        # Create question document record
        document = QuestionDocument(
            title=form.title.data,
            filename=filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            subject_id=form.subject_id.data,
            document_type=form.document_type.data,
            academic_year=form.academic_year.data,
            semester=form.semester.data,
            uploader_id=current_user.id
        )
        
        db.session.add(document)
        db.session.commit()
        
        # Start background processing
        extractor = QuestionExtractor()
        extractor.process_document(document.id)
        
        flash('Question document uploaded and processing started!', 'success')
        return redirect(url_for('question_document_detail', id=document.id))
    
    return render_template('questions/upload.html', form=form)

@app.route('/questions/<int:id>')
@require_login
def question_document_detail(id):
    """View question document details and extracted questions."""
    document = QuestionDocument.query.get_or_404(id)
    questions = Question.query.filter_by(document_id=id).order_by(Question.page_number, Question.question_number).all()
    
    return render_template('questions/detail.html', document=document, questions=questions)

@app.route('/questions/<int:id>/download')
@require_login
def download_question_document(id):
    """Download a question document."""
    document = QuestionDocument.query.get_or_404(id)
    
    try:
        return send_file(
            document.file_path,
            as_attachment=True,
            download_name=document.original_filename,
            mimetype='application/pdf'
        )
    except FileNotFoundError:
        flash('File not found.', 'error')
        return redirect(url_for('question_document_detail', id=id))

@app.route('/generate-paper', methods=['GET', 'POST'])
@require_login
def generate_question_paper():
    """Generate a custom question paper."""
    form = GenerateQuestionPaperForm()
    
    if form.validate_on_submit():
        # Generate question paper
        generator = QuestionPaperGenerator()
        
        difficulty_distribution = {
            'easy': form.easy_percentage.data / 100.0,
            'medium': form.medium_percentage.data / 100.0,
            'hard': form.hard_percentage.data / 100.0
        }
        
        result = generator.generate_question_paper(
            subject_id=form.subject_id.data,
            unit_ids=form.unit_ids.data if form.unit_ids.data else None,
            topic_ids=form.topic_ids.data if form.topic_ids.data else None,
            total_marks=form.total_marks.data,
            difficulty_distribution=difficulty_distribution
        )
        
        if result:
            filename, file_path = result
            
            # Save generated paper record
            paper = GeneratedQuestionPaper(
                title=form.title.data,
                subject_id=form.subject_id.data,
                unit_ids=json.dumps(form.unit_ids.data),
                topic_ids=json.dumps(form.topic_ids.data),
                total_marks=form.total_marks.data,
                duration_minutes=form.duration_minutes.data,
                filename=filename,
                file_path=file_path,
                generated_by=current_user.id
            )
            
            db.session.add(paper)
            db.session.commit()
            
            flash('Question paper generated successfully!', 'success')
            return redirect(url_for('download_generated_paper', id=paper.id))
        else:
            flash('Unable to generate question paper. Please check your selection criteria.', 'error')
    
    return render_template('questions/generate.html', form=form)

@app.route('/generated-papers/<int:id>/download')
@require_login
def download_generated_paper(id):
    """Download a generated question paper."""
    paper = GeneratedQuestionPaper.query.get_or_404(id)
    paper.download_count += 1
    db.session.commit()
    
    try:
        return send_file(
            paper.file_path,
            as_attachment=True,
            download_name=f"{paper.title}.pdf",
            mimetype='application/pdf'
        )
    except FileNotFoundError:
        flash('File not found.', 'error')
        return redirect(url_for('my_generated_papers'))

@app.route('/my-generated-papers')
@require_login
def my_generated_papers():
    """View user's generated question papers."""
    papers = GeneratedQuestionPaper.query.filter_by(generated_by=current_user.id)\
        .order_by(desc(GeneratedQuestionPaper.generated_at)).all()
    
    return render_template('questions/my_generated.html', papers=papers)

# Subject, Unit, and Topic Management Routes

@app.route('/admin/subjects')
@require_admin
def manage_subjects():
    """Manage subjects."""
    subjects = Subject.query.order_by(Subject.name).all()
    form = SubjectManagementForm()
    
    return render_template('admin/subjects.html', subjects=subjects, form=form)

@app.route('/admin/subjects/add', methods=['POST'])
@require_admin
def add_subject():
    """Add a new subject."""
    form = SubjectManagementForm()
    
    if form.validate_on_submit():
        # Check if subject code already exists
        existing = Subject.query.filter_by(code=form.code.data).first()
        if existing:
            flash('Subject code already exists.', 'error')
            return redirect(url_for('manage_subjects'))
        
        subject = Subject(
            name=form.name.data,
            code=form.code.data,
            department_id=form.department_id.data
        )
        
        db.session.add(subject)
        db.session.commit()
        
        flash('Subject added successfully!', 'success')
    
    return redirect(url_for('manage_subjects'))

@app.route('/admin/units')
@require_admin
def manage_units():
    """Manage units."""
    units = Unit.query.order_by(Unit.subject_id, Unit.order_index).all()
    form = UnitManagementForm()
    
    return render_template('admin/units.html', units=units, form=form)

@app.route('/admin/units/add', methods=['POST'])
@require_admin
def add_unit():
    """Add a new unit."""
    form = UnitManagementForm()
    
    if form.validate_on_submit():
        unit = Unit(
            name=form.name.data,
            description=form.description.data,
            subject_id=form.subject_id.data,
            order_index=form.order_index.data
        )
        
        db.session.add(unit)
        db.session.commit()
        
        flash('Unit added successfully!', 'success')
    
    return redirect(url_for('manage_units'))

@app.route('/admin/topics')
@require_admin
def manage_topics():
    """Manage topics."""
    topics = Topic.query.order_by(Topic.unit_id, Topic.name).all()
    form = TopicManagementForm()
    
    return render_template('admin/topics.html', topics=topics, form=form)

@app.route('/admin/topics/add', methods=['POST'])
@require_admin
def add_topic():
    """Add a new topic."""
    form = TopicManagementForm()
    
    if form.validate_on_submit():
        topic = Topic(
            name=form.name.data,
            description=form.description.data,
            unit_id=form.unit_id.data,
            difficulty_level=form.difficulty_level.data
        )
        
        db.session.add(topic)
        db.session.commit()
        
        flash('Topic added successfully!', 'success')
    
    return redirect(url_for('manage_topics'))

# API endpoints for dynamic form updates
@app.route('/api/units/<int:subject_id>')
def api_get_units(subject_id):
    """Get units for a subject."""
    units = Unit.query.filter_by(subject_id=subject_id).order_by(Unit.order_index).all()
    return jsonify([{'id': unit.id, 'name': unit.name} for unit in units])

@app.route('/api/topics/<int:unit_id>')
def api_get_topics(unit_id):
    """Get topics for a unit."""
    topics = Topic.query.filter_by(unit_id=unit_id).order_by(Topic.name).all()
    return jsonify([{'id': topic.id, 'name': topic.name} for topic in topics])

def save_question_document_file(file, subject, academic_year):
    """Save uploaded question document file."""
    if file and file.filename.lower().endswith('.pdf'):
        from werkzeug.utils import secure_filename
        
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secure_filename(file.filename)}"
        
        # Create directory structure: uploads/questions/subject_code/year/
        base_dir = app.config.get('UPLOAD_FOLDER', 'uploads')
        year_dir = academic_year or datetime.now().year
        dept_dir = os.path.join(base_dir, 'questions', secure_filename(subject.code), str(year_dir))
        
        os.makedirs(dept_dir, exist_ok=True)
        
        file_path = os.path.join(dept_dir, filename)
        file.save(file_path)
        
        return filename, file_path
    
    return None, None