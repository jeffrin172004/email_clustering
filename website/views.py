from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import User,EmailCluster
from . import db
#from .email_fetcher import fetch_emails
import json
from datetime import datetime
from .test import process_emails  # Import from test.py

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    clusters = []
    if request.method == 'POST':
        from_date = request.form.get('from_date')
        try:
            # Validate date
            datetime.strptime(from_date, '%Y-%m-%d')
            # Fetch and process emails
            processed_clusters = process_emails(from_date)
            # Save to database
            for i, summary in enumerate(processed_clusters['summary']):
                email_ids = processed_clusters['email'][i]
                new_cluster = EmailCluster(
                    summary=summary,
                    email_ids=json.dumps([eid for eid, _ in email_ids]),  # Store email IDs
                    email_count=len(email_ids),
                    start_date=datetime.strptime(from_date, '%Y-%m-%d'),
                    user_id=current_user.id
                )
                db.session.add(new_cluster)
            db.session.commit()
            flash('Emails processed and clustered successfully!', category='success')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', category='failed')
        except Exception as e:
            flash(f'Error processing emails: {str(e)}', category='failed')
    
    # Fetch clusters for display
    clusters = EmailCluster.query.filter_by(user_id=current_user.id).all()
    clusters = [
        {
            'summary': cluster.summary,
            'email_ids': json.loads(cluster.email_ids),
            'email_count': cluster.email_count
        } for cluster in clusters
    ]
    
    return render_template("home.html", user=current_user, clusters=clusters)

