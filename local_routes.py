from flask import session, render_template, request, flash, redirect, url_for, send_file, jsonify
from flask_login import current_user
from sqlalchemy import desc, func, extract
from datetime import datetime
import os

from local_app import app, db
from local_replit_auth import require_login, make_replit_blueprint, require_admin
from models import ResearchPaper, Department, User, DownloadLog, Keyword
from forms import UploadPaperForm, SearchForm, UserProfileForm
from utils import allowed_file, extract_pdf_metadata, extract_keywords_from_text, save_uploaded_file, format_file_size

app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

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
            status='approved'  # Auto-approve for local development
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
        current_user.department = form.department.data
        current_user.year = form.year.data
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', form=form)

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
                         papers=papers_pagination.items,
                         pagination=papers_pagination,
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
    
    return render_template('admin_users.html', 
                         users=users_pagination.items,
                         pagination=users_pagination)

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