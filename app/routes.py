from app import app, db
from .forms import PatientUploadForm, MedicationUploadForm, A1CUploadForm, BPUploadForm, \
    RAFUploadForm, FileDownload, EncUploadForm, EncDxUploadForm, EncProcUploadForm, ProvUploadForm
from werkzeug.utils import secure_filename
import config
import os
from flask import flash, redirect, render_template, url_for, request, send_file
from .functions import format_and_import_patient_data, format_and_import_medication_data, \
    format_and_import_A1C_data, format_and_import_BP_data, format_and_import_RAF_data, \
    format_and_import_encounter_data, format_and_import_provider_data, format_and_import_enc_dx_data, \
    format_and_import_enc_proc_data
from .models import Patient, Medication, A1C, EncounterBP, RAFScore, EncounterDx, TableMetadata, \
    Provider, Encounter, EncounterProc
import sqlalchemy as sa
import sqlalchemy.orm as so
from .queries import diabetics_query, hypertensives_query, patient_complexity_query
import pandas as pd
import datetime as dt

@app.route('/')
@app.route('/index', methods = ['GET', 'POST'])
def index():

    def get_query_dict(query, columns: list) -> dict:
        return [{col: getattr(row, col) for col in columns} for row in query]

    
    def get_table_import_time(table_name: str) -> str:
        time: dt.datetime = db.session.query(sa.func.max(TableMetadata.time_imported)).where(TableMetadata.table_name == table_name).scalar()
        if time: 
            return time.strftime('%m/%d/%y %H:%M:%S')
        else:
            return None
        
    
    prov_import_time = get_table_import_time(Provider.__tablename__)
    prov_count = db.session.query(sa.func.count(Provider.providerid)).scalar()
    prov_query = db.session.query(Provider).limit(5).all()
    prov_columns = Provider.__table__.columns.keys()
    providers = get_query_dict(prov_query, prov_columns)

    
    patient_import_time = get_table_import_time(Patient.__tablename__)
    patient_count = db.session.query(sa.func.count(Patient.enterpriseid)).scalar()
    patients_query = db.session.query(Patient).limit(5).all()
    patient_columns = Patient.__table__.columns.keys()
    patients = get_query_dict(patients_query, patient_columns)

    
    medication_import_time = get_table_import_time(Medication.__tablename__)
    medication_count = db.session.query(sa.func.count(Medication.id)).scalar()
    medications_query = db.session.query(Medication).limit(5).all()
    medication_columns = Medication.__table__.columns.keys()
    medications = get_query_dict(medications_query, medication_columns)

    
    a1c_import_time = get_table_import_time(A1C.__tablename__)
    a1c_count = db.session.query(sa.func.count(A1C.id)).scalar()
    a1c_query = db.session.query(A1C).limit(5).all()
    a1c_columns = A1C.__table__.columns.keys()
    a1c_data = get_query_dict(a1c_query, a1c_columns)

    
    bp_import_time = get_table_import_time(EncounterBP.__tablename__)
    bp_count = db.session.query(sa.func.count(EncounterBP.id)).scalar()
    bp_query = db.session.query(EncounterBP).limit(5).all()
    bp_columns = EncounterBP.__table__.columns.keys()
    bp_data = get_query_dict(bp_query, bp_columns)

    raf_import_time = get_table_import_time(RAFScore.__tablename__)
    raf_count = db.session.query(sa.func.count(RAFScore.id)).scalar()
    raf_query = db.session.query(RAFScore).limit(5).all()
    raf_columns = RAFScore.__table__.columns.keys()
    raf_data = get_query_dict(raf_query, raf_columns)

    enc_count = db.session.query(sa.func.count(Encounter.encounterid)).scalar()
    enc_import_time = get_table_import_time(Encounter.__tablename__)
    enc_query = db.session.query(Encounter).limit(5).all()
    enc_columns = Encounter.__table__.columns.keys()
    enc_data = get_query_dict(enc_query, enc_columns)

    encdx_count = db.session.query(sa.func.count(EncounterDx.encounterid)).scalar()
    encdx_import_time = get_table_import_time(EncounterDx.__tablename__)
    encdx_query = db.session.query(EncounterDx).limit(5).all()
    encdx_columns = EncounterDx.__table__.columns.keys()
    encdx_data = get_query_dict(encdx_query, encdx_columns)

    encproc_count = db.session.query(sa.func.count(EncounterProc.encounterid)).scalar()
    encproc_import_time = get_table_import_time(EncounterProc.__tablename__)
    encproc_query = db.session.query(EncounterProc).limit(5).all()
    encproc_columns = EncounterProc.__table__.columns.keys()
    encproc_data = get_query_dict(encproc_query, encproc_columns)

    context = {
        "data":[
            {
                "title":"Provider Data",
                "import_time": prov_import_time,
                "count": prov_count,
                "columns": prov_columns,
                "rows": providers,
            },
            {
                "title":"Patient Data",
                "import_time": patient_import_time,
                "count": patient_count,
                "columns":patient_columns,
                "rows": patients,
            },
            {
                "title":"Medication Data",
                "import_time": medication_import_time,
                "count": medication_count,
                "columns": medication_columns,
                "rows": medications,
            },
            {
                "title":"A1C Data",
                "import_time": a1c_import_time,
                "count": a1c_count,
                "columns": a1c_columns,
                "data": a1c_data,
            }, 
            {
                "title":"Blood Pressure Data",
                "import_time": bp_import_time,
                "count": bp_count,
                "columns": bp_columns,
                "rows": bp_data,
            },
            {    
                "title":"RAF Score Data",
                "import_time":raf_import_time,
                "count": raf_count,
                "columns": raf_columns,
                "rows": raf_data,
            },
            { 
                "title":"Encounter Data",
                "import_time": enc_import_time,
                "count": enc_count,
                "columns": enc_columns,
                "rows": enc_data
            },
            { 
                "title":"Encounter Diagnoses Data",
                "import_time": encdx_import_time,
                "count": encdx_count,
                "columns": encdx_columns,
                "rows": encdx_data
            },
            { 
                "title":"Encounter Procedure Data",
                "import_time": encproc_import_time,
                "count": encproc_count,
                "columns": encproc_columns,
                "rows": encproc_data
            }
        ]}
    return render_template('index.html', **context)

@app.route('/upload', methods = ['GET', 'POST'])
def upload():

    patient_form =  PatientUploadForm()
    medication_form = MedicationUploadForm()
    A1C_form = A1CUploadForm()
    BP_form = BPUploadForm()
    RAF_form = RAFUploadForm()
    Enc_form = EncUploadForm()
    EncDx_form = EncDxUploadForm()
    EncProc_form = EncProcUploadForm()
    prov_form = ProvUploadForm()


    if patient_form.validate_on_submit():
        file = request.files['uploaded_file']
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        format_and_import_patient_data(upload_path)
        return redirect(url_for("index"))
    
    if medication_form.validate_on_submit():
        file = request.files['uploaded_file']
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        format_and_import_medication_data(upload_path)
        return redirect(url_for("index"))        

    if A1C_form.validate_on_submit():
        file = request.files['uploaded_file']
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        format_and_import_A1C_data(upload_path)
        return redirect(url_for('index'))
    
    if BP_form.validate_on_submit():
        file = request.files['uploaded_file']
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        format_and_import_BP_data(upload_path)
        return redirect(url_for('index'))
    
    if RAF_form.validate_on_submit():
        file = request.files['uploaded_file']
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        format_and_import_RAF_data(upload_path)
        return redirect(url_for('index'))
    
    if Enc_form.validate_on_submit():
        file = request.files['uploaded_file']
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        format_and_import_encounter_data(upload_path)
        return redirect(url_for('index'))
    
    if prov_form.validate_on_submit():
        file = request.files['uploaded_file']
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        format_and_import_provider_data(upload_path)
        return redirect(url_for('index'))
    
    if EncDx_form.validate_on_submit():
        file = request.files['uploaded_file']
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        format_and_import_enc_dx_data(upload_path)
        return redirect(url_for('index'))
    
    if EncProc_form.validate_on_submit():
        file = request.files['uploaded_file']
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        format_and_import_enc_proc_data(upload_path)
        return redirect(url_for('index'))


    context = {'forms': [
                    {"title":"Patient Upload",
                    "subtitles":[
                            "Requires the columns <strong>EnterpriseID, Age, Sex, Primary Provider, Med Names</strong>"
                            ],
                    "form": patient_form
                    },
                    {"title": "Medication Upload",
                     "subtitles":["Requires the columns <strong>EnterpriseID, med names (single)</strong>"],
                     "form": medication_form
                     },
                    {"title":"A1C Data Upload",
                     "subtitles":["Requires the columns <strong>EnterpriseID, labdate, labvalue</strong>"],
                     "form": A1C_form
                     },
                    {"title":"Blood Pressure Data Upload",
                     "subtitles":["Requires the columns <strong>EnterpriseID, Enc BP, Enc BP date</strong>"],
                     "form": BP_form
                     },
                    {"title":"RAF Score Data Upload",
                     "subtitles":["Requires the columns <strong>EnterpriseID, HCC RAF Score</strong>"],
                     "form": RAF_form
                     },
                    {"title":"Encounter Data Upload",
                     "subtitles":["Requires the columns <strong>EnterpriseID, cln enc date, prvdr, and icd10encounterdiagcode</strong>"],
                     "form": Enc_form
                     },
                    {"title":"Encounter Diagnosis Data Upload",
                     "subtitles":["Requires the columns <strong>'cln enc id' and 'icd10encounterdiagcode'</strong>"],
                     "form": EncDx_form
                     },
                    {"title":"Encounter Procedure Code Data Upload",
                     "subtitles":["Requires the columns <strong>'cln enc id' and 'enc srv proccode'</strong>"],
                     "form": EncProc_form
                     },
                    {"title":"Provider Data Upload",
                     "subtitles":["Requires the columns <strong>'prvdrid', 'prvdr', 'prvdrfrstnme', 'prvdrlstnme' and 'prvdrtype'</strong>"],
                     "form": prov_form
                     },
                ]}
    return render_template('upload.html', **context)

from flask import Flask, render_template, request, send_file
import pandas as pd
import os

@app.route('/dm_output', methods=['GET', 'POST'])
def dm_output():
    form = FileDownload()

    # Fetch query results
    query_result = diabetics_query()
    columns = query_result.keys()
    rows = query_result.fetchall()

    if form.validate_on_submit():
        # Convert query result to DataFrame
        df = pd.DataFrame(rows, columns=columns)
        
        # Prepare file name
        filename = 'poorly_cont_dm_output'
        file_format = form.file_format.data

        # Ensure DOWNLOAD_FOLDER exists
        download_folder = app.config['DOWNLOAD_FOLDER']
        
        filepath = os.path.join(download_folder, f"{filename}_{dt.datetime.now().strftime("%Y%m%d_%H%M")}.{file_format}")
        
        print(filepath)
        # Save file to DOWNLOAD_FOLDER
        if file_format == 'csv':
            df.to_csv(filepath, index=False)
        else:
            df.to_excel(filepath, index=False, engine='openpyxl')
        
        # Send file as response
        return send_file(filepath, as_attachment=True)

    # Prepare context for rendering template
    context = {
        "title": "Poorly Controlled Diabetic Query",
        "form": form,
        'column_names': columns,
        'rows': rows
    }
    return render_template('output.html', **context)




@app.route('/htn_output', methods=['GET', 'POST'])
def htn_output():
    form = FileDownload()

    # Fetch query results
    query_result = hypertensives_query()
    columns = query_result.keys()
    rows = query_result.fetchall()

    if form.validate_on_submit():
        # Convert query result to DataFrame
        df = pd.DataFrame(rows, columns=columns)
        
        # Prepare file name
        filename = 'poorly_cont_htn_output'
        file_format = form.file_format.data

        # Ensure DOWNLOAD_FOLDER exists
        download_folder = app.config['DOWNLOAD_FOLDER']
        
        filepath = os.path.join(download_folder, f"{filename}_{dt.datetime.now().strftime("%Y%m%d_%H%M")}.{file_format}")
        
        print(filepath)
        # Save file to DOWNLOAD_FOLDER
        if file_format == 'csv':
            df.to_csv(filepath, index=False)
        else:
            df.to_excel(filepath, index=False, engine='openpyxl')
        
        # Send file as response
        return send_file(filepath, as_attachment=True)

    # Prepare context for rendering template
    context = {
        "title": "Poorly Controlled Hypertensive Query",
        "form": form,
        'column_names': columns,
        'rows': rows
    }
    return render_template('output.html', **context)

@app.route('/comp_output', methods=['GET', 'POST'])
def pat_complex_output():
    form = FileDownload()

    # Fetch query results
    query_result = patient_complexity_query()
    columns = query_result.keys()
    rows = query_result.fetchall()

    if form.validate_on_submit():
        # Convert query result to DataFrame
        df = pd.DataFrame(rows, columns=columns)
        
        # Prepare file name
        filename = 'patient_complex_output'
        file_format = form.file_format.data

        # Ensure DOWNLOAD_FOLDER exists
        download_folder = app.config['DOWNLOAD_FOLDER']
        
        filepath = os.path.join(download_folder, f"{filename}_{dt.datetime.now().strftime("%Y%m%d_%H%M")}.{file_format}")
        
        print(filepath)
        # Save file to DOWNLOAD_FOLDER
        if file_format == 'csv':
            df.to_csv(filepath, index=False)
        else:
            df.to_excel(filepath, index=False, engine='openpyxl')
        
        # Send file as response
        return send_file(filepath, as_attachment=True)

    # Prepare context for rendering template
    context = {
        "title": "Patient Complexity Query",
        "form": form,
        'column_names': columns,
        'rows': rows
    }
    return render_template('output.html', **context)