from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Patient': models.Patient,
        'A1C': models.A1C,  # Add all your models here
        'BP': models.BP,
        'sa': sa,
        'so': so,
        'app': app
    }
