from app import app

if __name__ == "__main__":
    app.run(debug=True)

import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db
from app.models import Patient, A1C, EncounterBP, Medication

@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 
            'Patient': Patient, 'A1C': A1C,
            'BP': EncounterBP, 'Medication': Medication}