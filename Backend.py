from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flasgger import Swagger  # Importiere Swagger

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)
ma = Marshmallow(app)
swagger = Swagger(app)  # Initialisiere Swagger mit deiner Flask-Anwendung

# Task-Modell für die Datenbank
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)

# Task Schema für die Serialisierung mit Marshmallow
class TaskSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Task

    id = ma.auto_field()
    content = ma.auto_field()
    completed = ma.auto_field()

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

# Beispiel-Benutzername und Passwort (normalerweise sollten diese sicherer gespeichert werden)
USERNAME = 'user'
PASSWORD = 'password'

# Token-basierte Authentifizierung
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login endpoint
    ---
    responses:
      302:
        description: Redirect to index if login successful
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    User logout endpoint
    ---
    responses:
      302:
        description: Redirect to login page after logout
    """
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.before_request
def check_logged_in():
    """
    Check if user is logged in before processing request
    ---
    """
    if not session.get('logged_in') and request.endpoint not in ('login',):
        return redirect(url_for('login'))

# Routen für CRUD-Operationen
@app.route('/', methods=['GET'])
def index():
    """
    Home page endpoint
    ---
    responses:
      200:
        description: Renders index page
    """
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/tasks', methods=['GET'])
def get_tasks():
    """
    Retrieve all tasks endpoint
    ---
    responses:
      200:
        description: List of tasks
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Task'  # Verweise auf dein Task-Schema
    """
    tasks = Task.query.all()
    return jsonify(tasks_schema.dump(tasks))

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """
    Retrieve a specific task by ID endpoint
    ---
    parameters:
      - name: task_id
        in: path
        description: ID of the task to retrieve
        required: true
        schema:
          type: integer
          format: int64
    responses:
      200:
        description: Task details
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Task'  # Verweise auf dein Task-Schema
      404:
        description: Task not found
    """
    task = Task.query.get_or_404(task_id)
    return jsonify(task_schema.dump(task))

@app.route('/tasks', methods=['POST'])
def create_task():
    """
    Create a new task endpoint
    ---
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Task'  # Verweise auf dein Task-Schema
    responses:
      201:
        description: Task created successfully
      400:
        description: Content is required
    """
    content = request.json.get('content')
    if not content:
        return jsonify({'message': 'Content is required!'}), 400

    new_task = Task(content=content)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task created successfully!'}), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """
    Update a task by ID endpoint
    ---
    parameters:
      - name: task_id
        in: path
        description: ID of the task to update
        required: true
        schema:
          type: integer
          format: int64
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Task'  # Verweise auf dein Task-Schema
    responses:
      200:
        description: Task updated successfully
    """
    task = Task.query.get_or_404(task_id)
    content = request.json.get('content')
    completed = request.json.get('completed')

    if content:
        task.content = content
    if completed is not None:
        task.completed = completed

    db.session.commit()
    return jsonify({'message': 'Task updated successfully!'})

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    Delete a task by ID endpoint
    ---
    parameters:
      - name: task_id
        in: path
        description: ID of the task to delete
        required: true
        schema:
          type: integer
          format: int64
    responses:
      200:
        description: Task deleted successfully
    """
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully!'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
