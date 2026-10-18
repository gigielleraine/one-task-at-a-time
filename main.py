import os
import random
import secrets
from flask import Flask, redirect, render_template, request, session, url_for
import database

# This task app is designed to help individuals simplify and organise their day to day tasks.
app = Flask(__name__)

# Load secret key from environment variable, or generate a secure random one
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))

# Ensure the database table exists when the app starts
database.init_db()

def get_random_task(task_list, current_id=None):
    """Selects a random task row, avoiding the current task ID if possible."""
    if not task_list:
        return None
    
    if len(task_list) == 1:
        return task_list[0]
    
    available_tasks = [task for task in task_list if task['id'] != current_id]
    
    if not available_tasks:
        return random.choice(task_list)
        
    return random.choice(available_tasks)

@app.route('/')
def home():
    """Displays the main web page and handles switching tasks."""
    active_tasks = database.get_active_tasks()
    completed_tasks = database.get_completed_tasks()
    
    current_id = request.args.get('current', type=int)
    next_task = get_random_task(active_tasks, current_id=current_id)
    
    # Read the current theme from the secure session (defaults to 'light')
    theme = session.get('theme', 'light')
    
    return render_template(
        'index.html',
        task=next_task,
        active_tasks=active_tasks,
        completed_tasks=completed_tasks,
        theme=theme
    )

@app.route('/add', methods=['POST'])
def add():
    """Handles adding a new task via form submission."""
    new_title = request.form.get('title', '')
    database.add_task(new_title)
    return redirect(url_for('home'))

@app.route('/complete/<int:task_id>', methods=['POST'])
def complete(task_id):
    """Handles marking a task as completed."""
    database.complete_task(task_id)
    return redirect(url_for('home'))

@app.route('/toggle-theme', methods=['POST'])
def toggle_theme():
    """Switches between light and dark mode in the user's session."""
    current_theme = session.get('theme', 'light')
    session['theme'] = 'dark' if current_theme == 'light' else 'light'
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=False)
