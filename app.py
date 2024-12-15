from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Налаштування додатку
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SECRET_KEY'] = 'ZXd1aHJ1ZmRzaG5mdWRobmZ3dWhlaHdlaGUyMzQ3MjM0MjM='
db = SQLAlchemy(app)

# Налаштування Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Модель користувача (для логінів)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

# Модель студента
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade_id = db.Column(db.Integer, db.ForeignKey('grade.id'), nullable=False)

# Модель вчителя
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    grade_id = db.Column(db.Integer, db.ForeignKey('grade.id'), nullable=False)

# Модель класу
class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False)
    students = db.relationship('Student', backref='grade', lazy=True)
    teachers = db.relationship('Teacher', backref='grade', lazy=True)

# Завантаження користувача за ID для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Головна сторінка
@app.route('/')
def index():
    return render_template('index.html')

# Реєстрація користувача
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Користувач вже існує.')
            return redirect(url_for('register'))
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

# Логін користувача
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Неправильне ім\'я користувача або пароль.')
    return render_template('login.html')

# Панель керування (сторінка для перегляду студентів, вчителів та класів)
@app.route('/dashboard')
@login_required
def dashboard():
    students = Student.query.all()
    teachers = Teacher.query.all()
    grades = Grade.query.all()
    return render_template('dashboard.html', students=students, teachers=teachers, grades=grades)

# Додавання нового студента
@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    grades = Grade.query.all()
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade_id = request.form['grade']
        new_student = Student(name=name, age=age, grade_id=grade_id)
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_student.html', grades=grades)

# Додавання нового вчителя
@app.route('/add_teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
    grades = Grade.query.all()
    if request.method == 'POST':
        name = request.form['name']
        subject = request.form['subject']
        grade_id = request.form['grade']
        new_teacher = Teacher(name=name, subject=subject, grade_id=grade_id)
        db.session.add(new_teacher)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_teacher.html', grades=grades)

# Додавання нового класу
@app.route('/add_grade', methods=['GET', 'POST'])
@login_required
def add_grade():
    if request.method == 'POST':
        name = request.form['name']
        new_grade = Grade(name=name)
        db.session.add(new_grade)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_grade.html')

# Вихід з облікового запису
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Створення таблиць у базі даних
with app.app_context():
    db.create_all()

# Запуск додатку
if __name__ == '__main__':
    app.run(debug=True)