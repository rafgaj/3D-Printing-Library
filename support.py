import pyvista as pv
from functools import wraps
from flask import redirect, session



def generate_thumbnail(stl_file_path, output_thumbnail_path):
    # STL file loading
    mesh = pv.read(stl_file_path)
    
    # Plotter creating
    plotter = pv.Plotter(off_screen=True)
    plotter.add_mesh(mesh, color='white') 
    
    # Save the thumbnail
    plotter.show(screenshot=output_thumbnail_path)



def paginate(data, page, per_page):
    
    start = (page - 1) * per_page
    end = start + per_page

    return data[start:end]



def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function
