"""
Routes and views for the flask application.
"""
from datetime import datetime
from flask import render_template
from ModStorage import app

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['Cache-Control'] = 'no-cache, no-store'
    response.headers['Pragma'] = 'no-cache'
    return response

@app.route('/modstorage')
def modstorage():
    return render_template(
        'storage.html',
        title='modstorage',
        year=datetime.now().year,
    )

@app.route('/modVizX2')
def modvizx2():
    return render_template(
        'ModVizX2.html',
        title='modVizX2',
        year=datetime.now().year,
    )

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )


@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )
