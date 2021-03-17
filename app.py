"""Flask app for Notes"""

from flask import Flask, request, redirect, render_template, jsonify, flash, session
from models import db, connect_db, User, Note
from forms import AddUserForm, LogInForm, NoteForm, EmailForm
from sqlalchemy.exc import IntegrityError
from flask_mail import Mail, Message
from secrets import token_urlsafe

app = Flask(__name__)

app.config.update(
    MAIL_SERVER='smtp@gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME = 'rithmtest20@gmail.com',
    MAIL_PASSWORD = 'RithmSchool20!'
)
mail = Mail(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///notes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = 'youllneverguess'

connect_db(app)
db.create_all()

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def check_incorrect_user(username):
    user = User.query.get(session.get('cur_user'))
    if session.get('cur_user') == username or user.is_admin:
        return False
    flash("Please log in to access this page!")
    return True

def check_already_logged_in():
    return session.get('cur_user')

@app.before_first_request
def add_admin():
    if not User.query.get('c'):
        admin = User.create_admin()
        db.session.add(admin)
        db.session.commit()


@app.route("/")
def index():
    """ Loads Home Page """
   
    return redirect('/register')
    admin = create


@app.route("/register", methods=['GET', 'POST'])
def register_user():
    """ Loads Home Page """
    if check_already_logged_in():
        return redirect(f"/users/{session['cur_user']}")
    form = AddUserForm()
    if request.method == "POST":
        if form.validate_on_submit():

            # Is this the best way to check for duplicate user?
            try:
                user = User.register_user(form)
                # error gets thrown after add/commit
                db.session.add(user)
                db.session.commit()
                session["cur_user"] = user.username
            
                return redirect(f'/users/{user.username}')

            except IntegrityError:
                flash("Username/email already taken")
                return redirect('/register')

    return render_template("user_form.html", form=form)


@app.route('/login', methods = ["GET", "POST"])
def log_in():
    """Displays log in page"""
    if check_already_logged_in():
        return redirect(f"/users/{session['cur_user']}")
    form = LogInForm()

    if request.method == "POST":
        if form.validate_on_submit():
            
            user = User.authenticate_user(form.username.data, form.password.data)
            if user:
                session["cur_user"] = user.username

            return redirect(f'/users/{user.username}') 
        
    return render_template("log_in_form.html", form=form)




@app.route('/logout', methods = ["POST"])
def log_out():
    session.pop("cur_user", None)
    flash("You are logged out!")
    return redirect('/')


@app.route('/users/<username>')
def show_user_page(username):
    """Secret page for only logged in users"""
    
    # need to check this in buried paths as well
    if check_incorrect_user(username):
        return redirect('/login')
    
    user = User.query.get_or_404(username)

    return render_template("user_page.html", user=user)

@app.route('/users/<username>/delete', methods = ["POST"])
def delete_user(username):
    """Deletes user and their notes"""

    if check_incorrect_user(username):
        return redirect('/login')

    user = User.query.get_or_404(username)
    for note in user.notes:
        db.session.delete(note)
    db.session.delete(user)
    db.session.commit()

    session.pop("cur_user", None)
    flash("User deleted!")

    return redirect('/')


@app.route('/users/<username>/notes/add', methods = ["GET", "POST"])
def add_new_note(username):
    """Shows/processes form for adding new note"""

    if check_incorrect_user(username):
        return redirect('/login')

    form = NoteForm()

    if form.validate_on_submit():
        
        note = Note(title=form.title.data, content=form.content.data, owner=username)
        db.session.add(note)
        db.session.commit()

        return redirect(f'/users/{username}') 

    return render_template("note_form.html", form=form, username=username)

@app.route('/notes/<int:note_id>/update', methods = ["GET", "POST"])
def edit_note(note_id):
    """Note page"""
    
    note = Note.query.get_or_404(note_id)
    if check_incorrect_user(note.user.username):
        return redirect('/login')
    form = NoteForm(obj=note)
    
    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data
        db.session.commit()
        return redirect(f"/users/{note.user.username}")

    return render_template("note_edit.html", note_id=note_id, form=form)

@app.route('/notes/<int:note_id>/delete', methods=["POST"])
def delete_note(note_id):
    """Delete note"""

    note = Note.query.get_or_404(note_id)
    if check_incorrect_user(note.user.username):
        return redirect('/login')

    username = note.user.username
    db.session.delete(note)
    db.session.commit()
    return redirect(f"/users/{username}")


@app.route('/passwordreset', methods = ["GET", "POST"])
def reset_pw():
    form = EmailForm()
    
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            user.token = token_urlsafe()

            msg = Message("Please click this link to reset your password:")

    return render_template("resetform.html", form=form)
