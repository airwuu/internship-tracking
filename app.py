import os
import json
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import case
import pandas as pd
from datetime import datetime

load_dotenv()
# --- App & DB Config, and Models are unchanged ---
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')

if not app.config['SQLALCHEMY_DATABASE_URI']:
    raise RuntimeError("SQLALCHEMY_DATABASE_URI not set. Please create a .env file with the database URL.")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    date_applied = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False, default='Applied')
    notes = db.Column(db.Text, nullable=True)

class StatusHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    from_status = db.Column(db.String(50), nullable=False)
    to_status = db.Column(db.String(50), nullable=False)
    change_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# --- Constants are unchanged ---
STATUS_STAGES = ['Start', 'Applied', 'Online Assessment', 'Technical Screen', 'Final Round', 'Offer', 'Offer Accepted', 'Offer Declined', 'Rejected', 'Withdrew']
STATUS_COLORS = {'Start': '#45475a', 'Applied': '#89b4fa', 'Online Assessment': '#fab387', 'Technical Screen': '#a6e3a1', 'Final Round': '#f9e2af', 'Offer': '#cba6f7', 'Offer Accepted': '#94e2d5', 'Offer Declined': '#eba0ac', 'Rejected': '#f38ba8', 'Withdrew': '#6c7086'}


# --- Sankey Diagram Logic is unchanged ---
def create_sankey_data():
    """Processes database history to generate data for the Sankey diagram."""
    history = StatusHistory.query.all()
    if not history:
        return None

    data = [(h.from_status, h.to_status) for h in history]
    df = pd.DataFrame(data, columns=['source', 'target'])
    df['value'] = 1
    
    links = df.groupby(['source', 'target']).sum().reset_index()

    all_nodes = list(pd.unique(links[['source', 'target']].values.ravel('K')))
    for stage in STATUS_STAGES:
        if stage not in all_nodes:
            all_nodes.append(stage)
    node_map = {node: i for i, node in enumerate(all_nodes)}

    source_totals = links.groupby('source')['value'].sum()
    target_totals = links.groupby('target')['value'].sum()
    node_totals = pd.concat([source_totals, target_totals], axis=1).max(axis=1).fillna(0).astype(int)

    formatted_labels = []
    for node in all_nodes:
        total = node_totals.get(node, 0)
        if total > 0 and node != 'Start':
            formatted_labels.append(f"{total} {node}")
        else:
            formatted_labels.append(node)

    sankey_links = {
        'source': links['source'].map(node_map).tolist(),
        'target': links['target'].map(node_map).tolist(),
        'value': links['value'].tolist(),
        'color': [STATUS_COLORS.get(s, '#888888') for s in links['source']]
    }
    
    node_colors = [STATUS_COLORS.get(node, '#888888') for node in all_nodes]
    
    sankey_nodes = {
        'label': formatted_labels,
        'clean_label': all_nodes,
        'color': node_colors
    }
    
    return {'nodes': sankey_nodes, 'links': sankey_links}

# --- UPDATED: Load personal links ---
def load_links():
    """Loads personal links from config.json."""
    try:
        with open('config.json') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return {}

# --- UPDATED: Index route to include links ---
@app.route('/')
def index():
    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', 'date_applied_desc')
    filter_status = request.args.get('filter_status', 'All')
    applications_query = Application.query
    if filter_status and filter_status != 'All':
        applications_query = applications_query.filter(Application.status == filter_status)
    if search_query:
        applications_query = applications_query.filter((Application.company.ilike(f'%{search_query}%')) | (Application.role.ilike(f'%{search_query}%')) | (Application.notes.ilike(f'%{search_query}%')))
    if sort_by == 'status':
        status_order = case({status: i for i, status in enumerate(STATUS_STAGES)}, value=Application.status)
        applications_query = applications_query.order_by(status_order)
    elif sort_by == 'company':
        applications_query = applications_query.order_by(Application.company.asc())
    else:
        applications_query = applications_query.order_by(Application.date_applied.desc())
    applications = applications_query.all()
    sankey_json = json.dumps(create_sankey_data()) if create_sankey_data() else '{}'
    personal_links = load_links() # Load the links
    return render_template('index.html', applications=applications, sankey_data=sankey_json, status_stages=STATUS_STAGES[1:], search_query=search_query, sort_by=sort_by, filter_status=filter_status, personal_links=personal_links)

# --- All other routes (edit, delete, etc.) are unchanged ---
@app.route('/edit/<int:app_id>', methods=['GET', 'POST'])
def edit_application(app_id):
    app_to_edit = Application.query.get_or_404(app_id)
    if request.method == 'POST':
        app_to_edit.company = request.form['company']
        app_to_edit.role = request.form['role']
        app_to_edit.notes = request.form['notes']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_app.html', app=app_to_edit)

@app.route('/delete/<int:app_id>', methods=['POST'])
def delete_application(app_id):
    app_to_delete = Application.query.get_or_404(app_id)
    StatusHistory.query.filter_by(app_id=app_id).delete()
    db.session.delete(app_to_delete)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
def add_application():
    new_app = Application(company=request.form.get('company'), role=request.form.get('role'), notes=request.form.get('notes'), status='Applied')
    db.session.add(new_app)
    db.session.commit()
    history_entry = StatusHistory(app_id=new_app.id, from_status='Start', to_status='Applied')
    db.session.add(history_entry)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/update/<int:app_id>', methods=['POST'])
def update_status(app_id):
    app_to_update = Application.query.get_or_404(app_id)
    new_status = request.form.get('status')
    if app_to_update.status != new_status:
        history_entry = StatusHistory(app_id=app_to_update.id, from_status=app_to_update.status, to_status=new_status)
        db.session.add(history_entry)
        app_to_update.status = new_status
        db.session.commit()
    return redirect(url_for('index', search=request.args.get('search', ''), sort_by=request.args.get('sort_by', 'date_applied_desc'), filter_status=request.args.get('filter_status', 'All')))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
