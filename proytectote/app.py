from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='.')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'devsecret123')

mongo_uri = os.environ.get(
    'MONGO_URI',
    'mongodb://localhost:27017/appdb'
)
db_name = os.environ.get('MONGO_DBNAME', 'appdb')
client = MongoClient(mongo_uri)
db = client[db_name]
users_collection = db.users
tasks_collection = db.tasks


def get_current_user():
    email = session.get('user_email')
    if not email:
        return None
    return users_collection.find_one({'email': email})


@app.route('/')
def home():
    return render_template('inicio.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not name or not email or not password:
            flash('Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('register'))
        if users_collection.find_one({'email': email}):
            flash('Ese correo ya está registrado.', 'warning')
            return redirect(url_for('register'))
        users_collection.insert_one({
            'name': name,
            'email': email,
            'password': generate_password_hash(password),
        })
        flash('Registro exitoso. Ahora inicia sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('formulario.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = users_collection.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            session['user_email'] = email
            session['user_name'] = user['name']
            flash(f'Bienvenido, {user["name"]}!', 'success')
            return redirect(url_for('tasks_page'))
        flash('Correo o contraseña incorrectos.', 'danger')
        return redirect(url_for('login'))
    return render_template('inicio_de_sesion.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('home'))


@app.route('/recover', methods=['GET', 'POST'])
def recover():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = users_collection.find_one({'email': email})
        if not user:
            flash('Correo no encontrado.', 'danger')
            return redirect(url_for('recover'))
        if not password:
            flash('Agrega una nueva contraseña.', 'warning')
            return redirect(url_for('recover'))
        users_collection.update_one(
            {'email': email},
            {'$set': {'password': generate_password_hash(password)}}
        )
        flash('Contraseña actualizada. Inicia sesión de nuevo.', 'success')
        return redirect(url_for('login'))
    return render_template('recuperar_contraseña.html')


@app.route('/tasks', methods=['GET', 'POST'])
def tasks_page():
    current_user = get_current_user()
    if not current_user:
        flash('Debes iniciar sesión primero.', 'warning')
        return redirect(url_for('login'))
    if request.method == 'POST':
        description = request.form.get('description', '').strip()
        if description:
            tasks_collection.insert_one({
                'user_email': current_user['email'],
                'description': description,
                'done': False,
            })
            flash('Tarea creada.', 'success')
        return redirect(url_for('tasks_page'))
    user_tasks = list(tasks_collection.find({'user_email': current_user['email']}))
    return render_template('gestor_de_tareas.html', tasks=user_tasks, user=current_user)


@app.route('/tasks/delete/<task_id>')
def delete_task(task_id):
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for('login'))
    tasks_collection.delete_one({'_id': ObjectId(task_id), 'user_email': current_user['email']})
    flash('Tarea eliminada.', 'info')
    return redirect(url_for('tasks_page'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
