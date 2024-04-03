# run.py
from app import create_app
from flask_sqlalchemy import SQLAlchemy

app = create_app()

if __name__ == "__main__":
    app.config["APPLICATION_ROOT"] = "/Fabrico"
    app.run(debug=True)
    
    
