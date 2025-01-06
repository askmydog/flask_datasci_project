from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import FileField, SubmitField, RadioField
from wtforms.validators import DataRequired, ValidationError
from flask_wtf.file import FileRequired, FileAllowed
from werkzeug.datastructures import FileStorage



# def validate_file_ext(filename: str) -> None:
#     if '.' not in filename or filename.rsplit('.', 1)[1].lower() != 'csv':
#         raise ValidationError('The form must be in csv format') 
    
def validate_file_size(filesize: int, max_size_in_MB: int) -> None:
    max_size = max_size_in_MB * 1024**2
    if filesize > max_size:
        raise ValidationError(f"The file size is {filesize/(1024 * 1024):.2f}, which is greater than the 5MB upload limit")

def validate_file_headers(file: FileStorage, required_headers: list) -> None:
    first_line:str = file.stream.readline().decode('utf-8').strip()
    second_line:str = file.stream.readline().decode('utf-8').strip()
    file.stream.seek(0)

    if 'report' in first_line.lower():
        file_headers:list = second_line.split(',')
    else:
        file_headers:list = first_line.split(',')

    if not all(s in file_headers for s in required_headers):
        raise ValidationError(f'The file does not contain the correct headers.'
                              f' The file has the headers {", ".join(file_headers)}.'
                              f' The required headers are {", ".join(required_headers)}')


def ValidatePatientForm(form, field):

    file: FileStorage = field.data

    # Check if file is less than 5MB
    filesize = len(file.read())
    file.stream.seek(0)
    validate_file_size(filesize, 5)

    # Check if file has correct headers
    required_headers = ['enterpriseid', 'patient age', 'patientsex', 'prim prvdr', 'status', 'ptnt dcsd ysn']
    validate_file_headers(file, required_headers)

class PatientUploadForm(FlaskForm):
    uploaded_file = FileField("Patient Report", validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!'), ValidatePatientForm])
    submit = SubmitField('Patient Upload')




def ValidateMedicationForm(form, field):

    file: FileStorage = field.data

    filesize = len(file.read())
    file.stream.seek(0)
    validate_file_size(filesize, 5)

    required_headers = ['enterpriseid', 'med names (single)']
    validate_file_headers(file, required_headers)

class MedicationUploadForm(FlaskForm):
    uploaded_file = FileField("Medication Report", validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!'), ValidateMedicationForm])
    submit = SubmitField('Medication Upload')




def ValidateA1CForm(form, field):
    file: FileStorage = field.data

    filesize = len(file.read())
    file.stream.seek(0)
    validate_file_size(filesize, 5)

    required_headers = ['enterpriseid', 'labdate', 'labvalue']
    validate_file_headers(file, required_headers)

class A1CUploadForm(FlaskForm):
    uploaded_file = FileField("A1C Report", validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!'), ValidateA1CForm])
    submit = SubmitField('A1C Upload')





def ValidateBPForm(form, field):
    file: FileStorage = field.data

    filesize = len(file.read())
    file.stream.seek(0)
    validate_file_size(filesize, 5)

    required_headers = ['cln enc id', 'Enc BP']
    validate_file_headers(file, required_headers)

class BPUploadForm(FlaskForm):
    uploaded_file = FileField("BP Report", validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!'), ValidateBPForm])
    submit = SubmitField('BP Upload')




def ValidateRAFForm(form, field):
    file: FileStorage = field.data

    filesize = len(file.read())
    file.stream.seek(0)
    validate_file_size(filesize, 5)

    required_headers = ['enterpriseid', 'HCC RAF score']
    validate_file_headers(file, required_headers)

class RAFUploadForm(FlaskForm):
    uploaded_file = FileField("RAF Report", validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!'), ValidateRAFForm])
    submit = SubmitField('RAF Upload')




def ValidateEncDxForm(form, field):
    file: FileStorage = field.data

    filesize = len(file.read())
    file.stream.seek(0)
    validate_file_size(filesize, 5)

    required_headers = ['cln enc id', 'icd10encounterdiagcode']
    validate_file_headers(file, required_headers)

class EncDxUploadForm(FlaskForm):
    uploaded_file = FileField("Encounter Diagnoses Report", validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!'), ValidateEncDxForm])
    submit = SubmitField('Encounter DiagnosesUpload')




def ValidateEncProcForm(form, field):
    file: FileStorage = field.data

    filesize = len(file.read())
    file.stream.seek(0)
    validate_file_size(filesize, 5)

    required_headers = ['cln enc id', 'enc srv proccode']
    validate_file_headers(file, required_headers)

class EncProcUploadForm(FlaskForm):
    uploaded_file = FileField("Encounter Procedures Report", validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!'), ValidateEncProcForm])
    submit = SubmitField('Encounter Procedures Upload')




def ValidateEncForm(form, field):
    file: FileStorage = field.data

    filesize = len(file.read())
    file.stream.seek(0)
    validate_file_size(filesize, 5)

    required_headers = ['cln enc id', 'enterpriseid', 'cln enc date', 'appttype']
    validate_file_headers(file, required_headers)

class EncUploadForm(FlaskForm):
    uploaded_file = FileField("Encounter Report", validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!'), ValidateEncForm])
    submit = SubmitField('Encounter Upload')




def ValidateProvForm(form, field):
    file: FileStorage = field.data

    filesize = len(file.read())
    file.stream.seek(0)
    validate_file_size(filesize, 5)

    required_headers = ['prvdrid', 'prvdr', 'prvdrfrstnme', 'prvdrlstnme', 'prvdrtype']
    validate_file_headers(file, required_headers)

class ProvUploadForm(FlaskForm):
    uploaded_file = FileField("Provider Report", validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!'), ValidateProvForm])
    submit = SubmitField('Provider Upload')




class FileDownload(FlaskForm):
    file_format = RadioField('File Format', choices=[('csv', 'CSV'), ('xlsx', 'Excel')])
    submit = SubmitField('Download File')

