from flask import render_template

def init_routes(app):
    @app.route('/')
    def login():
        return render_template('login.html')
 
    @app.route('/registerUser')
    def register():
        return render_template('register.html')
    
    @app.route('/fabrics')
    def index():
        return render_template('fabricData.html')