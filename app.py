import os
from flask import Flask, flash, redirect, render_template, request, session, url_for, g, send_file
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from forms import RegistrationForm, LoginForm, UploadForm, DetailForm
from flask_session import Session
from support import generate_thumbnail, paginate, login_required
import sqlite3

app = Flask(__name__)

app.config['SECRET_KEY'] = 'bea33018e0c37fcd'
app.config['DATABASE'] = '3Dprint.db'
app.config['UPLOAD_FOLDER'] = 'static/models/'
app.config['THUMBNAIL_FOLDER'] = 'static/thumbnails/'
app.config['BASEDIR'] = os.path.abspath(os.path.dirname(__file__))
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row  
    return g.db



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



@app.route("/")
@app.route("/home")
def index():
    
    db = get_db()

    cursor = db.execute("""
                        SELECT Models.id, Models.name, Models.filepath, Models.filename, Models.thumbnail, Models.desc, Models.private, Models.timestamp, Users.username 
                        FROM Models 
                        INNER JOIN Users 
                        ON Models.user_id = Users.id
                        """)
    items = cursor.fetchall()

    # Counting only public items
    for item in items[:]:  # Copy of items[]
        if item['private'] == 1:
            items.remove(item)

    # Get page number from URL parameter, default is page 1
    page = request.args.get('page', 1, type = int)
    per_page = 6  # Nb of items on page

    # Pagination
    paginated_data = paginate(items, page, per_page)

    # Counting number of pages
    total_pages = (len(items) + per_page - 1) // per_page

    return render_template("index.html", boxes = paginated_data, page = page, total_pages = total_pages)



@app.route("/register", methods = ['GET', 'POST'])
def register():

    form = RegistrationForm()
    if form.validate_on_submit():

        db = get_db()

        # Query database for username
        username = form.username.data
        cursor = db.execute("SELECT * FROM Users WHERE username = ?", (username,))
        rows = cursor.fetchall()    
  
        # Ensure that username is unique
        if len(rows) >= 1:
            flash(f'Username {username} already exist. Please choose different.', 'danger')
            return render_template("register.html", form = form)

        # Query database for email
        email = form.email.data
        cursor = db.execute("SELECT * FROM Users WHERE email = ?", (email,))
        rows = cursor.fetchall()    
 
        # Ensure that email is unique
        if len(rows) >= 1:
            flash(f'Email {email} is already registered. Please use different.', 'danger')
            return render_template("register.html", form = form)
        
        password = generate_password_hash(form.password.data, method='pbkdf2', salt_length=16)

        # Save data to database
        db.execute("INSERT INTO Users (username, email, password) VALUES (?, ?, ?)", (username, email, password,))
        db.commit()

        # Remember which user has logged in
        cursor = db.execute("SELECT * FROM Users WHERE username = ?", (username,))
        user = cursor.fetchone()
        session["user_id"] = user["id"]

        flash(f'Account created for {username}!', 'success')
        return redirect(url_for('index'))
    
    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("register.html", form = form)



@app.route("/login", methods = ['GET', 'POST'])
def login():
    
    form = LoginForm()
    if form.validate_on_submit():

        # Forget any user_id
        session.clear()

        db = get_db()

        email = form.email.data
        password = form.password.data

        # Query database for user
        cursor = db.execute("SELECT * FROM Users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if email == user['email'] and check_password_hash(user['password'], password):
            # Remember which user has logged in
            session['user_id'] = user['id']
            flash(f'User {user['username']} logged in.', 'success')
            return redirect(url_for('index'))
        
        else:
            flash('Login failed. Please check if the email and password are correct.', 'danger')
            return redirect(url_for('login'))

    else:         
        # User reached route via GET (as by clicking a link or via redirect)
        return render_template("login.html", form = form)



@app.route("/upload", methods = ['GET', 'POST'])
@login_required
def upload():
    
    form = UploadForm()
    if form.validate_on_submit():
        
        db = get_db()
        
        # File handling and upload
        user_id = session['user_id']
        file = form.file.data
        
        # Make filename unique by adding id and user_id
        cursor = db.execute("SELECT id FROM Models ORDER BY id DESC LIMIT 1")
        last_id = cursor.fetchone()
        last_id = last_id['id']
        last_id += 1
        filename = str(last_id) + '_' + str(user_id) + '_' + secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) 
        file.save(file_path)
        
        # Handling rest of the form
        name = form.name.data
        desc = form.desc.data
        private = form.private.data
        filepath = os.path.join(app.config['UPLOAD_FOLDER'])
        
        # Thumbnail generation
        thumbnail = os.path.join(app.config['THUMBNAIL_FOLDER'], f'{filename}.png')
        generate_thumbnail(file_path, thumbnail)
        
        # Query database
        db.execute("INSERT INTO Models (user_id, name, filename, thumbnail, desc, filepath, private) VALUES (?, ?, ?, ?, ?, ?, ?)", (user_id, name, filename, thumbnail, desc, filepath, private,))
        db.commit()

        flash('File successfully uploaded.', 'success')
        return redirect(url_for('library'))
    
    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("upload.html", form = form)



@app.route("/library")
@login_required
def library():
    
    db = get_db()
    user_id = session['user_id']
    cursor = db.execute("SELECT id, name, filepath, filename, thumbnail, desc, private, timestamp FROM Models WHERE user_id = ?", (user_id,))
    items = cursor.fetchall()

    # Get page number from URL parameter, default is page 1
    page = request.args.get('page', 1, type = int)
    per_page = 6  # Liczba elementów na stronie

    # Pagination
    paginated_data = paginate(items, page, per_page)

    # Counting number of pages
    total_pages = (len(items) + per_page - 1) // per_page

    return render_template("library.html", boxes = paginated_data, page = page, total_pages = total_pages)



@app.route("/<file>")
def download(file):
    
    return send_file(file, as_attachment = True)



@app.route("/detail/<model_id>", methods = ['GET', 'POST'])
def detail(model_id):
    
    db = get_db()
    form = DetailForm()
    
    cursor = db.execute("""
                        SELECT Models.id, Models.name, Models.filepath, Models.filename, Models.thumbnail, Models.desc, Models.private, Models.timestamp, Models.user_id, Users.username, Users.id
                        FROM Models 
                        INNER JOIN Users 
                        ON Models.user_id = Users.id
                        WHERE Models.id = ?
                        """, (model_id,))
    model = cursor.fetchone()
  
    file = model['filepath'] + model['filename']
    thumbnail = model['thumbnail']
    
    if request.method == 'GET':
        form.private.data = model['private']

    if request.form.get('download'):     
        try:
        # Check if file exist
            if file:
                #flash(f'File {model['filename']} downloaded successfully.', 'success')
                return redirect(url_for('download', file = file))
            else:
                flash(f'File {model['filename']} not exist.', 'danger')
        except Exception as e:
            flash(f'Error while downloading the file: {str(e)}', 'danger')
            
        return redirect(url_for('detail', model_id = model['id']))

    elif form.validate_on_submit() and request.form.get('delete'):
        try:
            if file:
                os.remove(file)  
                os.remove(thumbnail)
                db.execute("DELETE FROM Models WHERE id = ?", (model_id,))
                db.commit()
                flash(f'File {model['filename']} has been deleted.', 'success')
            else:
                flash(f'File {model['filename']} not exist.', 'danger')
        except Exception as e:
            flash(f'Error durig file delete: {str(e)}', 'danger')

        return redirect(url_for('library'))
        
    elif form.validate_on_submit() and request.form.get('submit'):
        private_new = form.private.data
        print(private_new)
        db.execute("UPDATE Models SET private = ? WHERE id = ?", (private_new, model_id,))
        db.commit()
        flash('Status saved.', 'success')
    
        return redirect(url_for('detail', model_id = model['id']))
 
    return render_template("detail.html", model = model, form = form)



@app.route("/search")
def search():
    
    query = request.args.get('query')
    
    if query:
        db = get_db()
        cursor = db.execute("SELECT * FROM Models WHERE name LIKE ? OR desc LIKE ?", ('%' + query + '%', '%' + query + '%'))
        results = cursor.fetchall()
        print(results)
        
    # Get page number from URL parameter, default is page 1
    page = request.args.get('page', 1, type = int)
    per_page = 6  # Liczba elementów na stronie

    # Pagination
    paginated_data = paginate(results, page, per_page)

    # Counting number of pages
    total_pages = (len(results) + per_page - 1) // per_page
    
    return render_template('search.html', results = paginated_data, page = page, total_pages = total_pages, query = query)



@app.route("/forgot", methods=['GET', 'POST'])
def forgot():

    form = RegistrationForm()

    if form.validate_on_submit():
        flash(f'Email sent to {form.email.data}!', 'success')
        return redirect(url_for('index'))
    
    return render_template("forgot.html", form = form)



@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for('index'))



@app.teardown_appcontext
def close_connection(exception):

    db = g.pop('db', None)
    if db is not None:
        db.close()



if __name__ == '__main__':
    app.run(debug = True)