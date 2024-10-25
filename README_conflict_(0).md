# 3D Printing Library and File Manager
#### Video Demo:  [3D Printing Library](https://youtu.be/x5dR0dKJBsw)

> GitHub and EdX username: rafgaj

> Wrocław, Poland

> October 24, 2024


### Description:

This application allows users to store, view, organize, and manage their 3D files in one place. It includes features of creating thumbnails, as well as export and download options, making it a practical tool for both hobbyists and professionals involved in 3D printing.
## Technologies:

1. Backend: Python and SQLite

    The application uses a `Flask` framework to handle application logic, process file uploads, verify them, and manage the database.
    An `SQLite` database store data about users, uploaded files and thumbnails.
    Files are stored on the server:
    `static/models/`
    `static/thumbnails/`.
    
    Form verifications are manage by `Flask WTF` addon and located in `forms.py` through the `validators`:
    ```
    from flask_wtf import FlaskForm
    from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, TextAreaField, RadioField
    from wtforms.validators import DataRequired, Length, Email, EqualTo
    from flask_wtf.file import FileRequired, FileAllowed, FileSize
    ```
    There are implemented validators to check if form is filled, correctness of the entered data, limitations for number of chars and file size, email correctnes. All alerts are provided to the user through the `flash` function and aligned with Bootstrap style.
    
    Thumbnails generation is by `PyVista` package. Function is located in `supports.py'
    ```
    import pyvista as pv
    ```
    I also tried using the `matplotlib` library, but the effect was much worse.

    Pages `index`, `library` and `search` have implemented pagination functionality. Function allowed pagination is located in `support.py`:
    ```
    def paginate(data, page, per_page):
    ```
    and implementation in each route. The style is consistent with the `Yeti` theme.

    The database was created using python. The database structure is contained in the file `db.py`.

2. Frontend: HTML, CSS, Bootstrap framework and tiny JavaScript.

    The user interface is built using HTML and CSS, with limited JavaScript only for confirmation delete functionality.
    
    Styling and responsiveness are built with use of Bootstrap framework - `Yeti` theme.

## Features:

1. __Registration__, __Log In__ and __Log Out__ users.    
    #### Description: 
    Users can register account using username, email and password. Then can login and logout.
    #### Functionality: 
    There are dedicated forms for register an login. Logout is through the button in navigation bar. As in _C$50 Finance_ project, session managment is used. User password is stored in database as hash.
    #### Files:
    `app.py`
    ```
    @app.route("/register", methods = ['GET', 'POST'])
    @app.route("/login", methods = ['GET', 'POST'])
    @app.route("/logout")
    ```
    `register.html` 
    `login.html`

2. __Upload__ 3D Files and thumbnail generation.

    #### Description: 
    Users can upload 3D files in STL format to the application for easy storage and viewing. 
    
    #### Functionality:
    An upload of STL file form with basic details, such as name, short description and private or public status decision. 
    
    Verification of uploaded files for supported STL format.
    
    Creation of an entry in the database with information about the uploaded file and assignment to a specific user. Name of teh file is created as unique thanks to add to the name `id` form database also `user_id`. 

    Thumbnail of 3D file creation after file uploading. 
    #### Files:
    `app.py`
    ```
    @app.route("/upload", methods = ['GET', 'POST'])
    ```
    `upload.html`

3. __Organize__ files.

    #### Description: 
    User can view his files in `My Library` and all users files marked as Public on the `Home` page.  
    #### Functionality:
    Access to the `My Library` is possible through the navigation bar. Library with all Public models is available from the `Home` page. 
    Access to the file details is possible by clicking file box.
    #### Files:
    `app.py`
    ```
    @app.route("/")
    @app.route("/home")
    @app.route("/upload", methods = ['GET', 'POST'])
    ```

4. __3D Preview__ and file __Details__.

    #### Description: 
    Users can view each file in a 3D preview to check its appearance before printing.
    #### Functionality:
    Access to the details is possible from all places where files are listed: `Home`, `My Library` and also from `Search` results.
    
    Display of basic details: File name, thubmnail, description, upload date and status.
    
    Links to the detail page are created dynamically.
    #### Files:
    `app.py`
    ```
    @app.route("/detail/<model_id>", methods = ['GET', 'POST'])
    ```
    `detail.html`

5. __Manage__ files: __Download__, __Delete__ and change __Status__.

    #### Description: 
    Users can download their files directly in STL format, ready for 3D printing. They can also delete files and chanege status from Public to Privete and vice versa.
    #### Functionality:
    All that operation are possible through the `Detail` page. Delete operation remove STL file and thumbnail from the server as well as clean database. 
    Thanks to use `GET` method: `if request.method == 'GET':` I was able to read current status and update in case of user will change by `POST`. User have confirm status change by `Save` button.
    #### Files:
    `app.py`
    ```
    @app.route("/<file>")
    def download(file):
    
    return send_file(file, as_attachment = True)
    ```
    ```
    os.remove(file)  
    os.remove(thumbnail)
    ```
6. Files __Status__.
    #### Description:
    User can keep files in private status - available only for him after Login. And also as Public, available for all users. 
    #### Functionality:
    The status is set when file is uploaded and can be changed by the owner on the `Detail` page. The private status is highlighted by using a different style for the filename background, it has the value `bg-dark`.
   

7. Simple __Search__ functionality.

    #### Description: 
    Users can can search files on the server.
    #### Functionality:
    The search is performed by querying the database to search the `name` and `desc` fields according to the given phrase. The results are presented in the form of a list of boxes with files with links to the `Detail` subpage.
    #### Files:
    `app.py`
    ```
    @app.route("/search")
    ```
    `search.html`