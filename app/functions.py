from werkzeug.datastructures import FileStorage
import pandas as pd
import datetime as dt
from .models import Patient, Medication, A1C, BP, RAFScore, EncounterDx, TableMetadata, Provider, Encounter, EncounterProc
import re
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db
from flask import flash

def get_header_line(file_path: str) -> int:
    """Checks to see if first row is report title, returns row with actual column headers.
    """

    # Open file path and read first line, then reset cursor so that file can be read correctly thereafter
    with open(file_path, 'r') as file:
         first_line = file.readline().strip()
         file.seek(0)  

    # If the word "report" is found in the first line, return the number for the second line (1), otherwise return number for first line (0)
    return 1 if "report" in first_line.lower() else 0


def validate_header_df(df: pd.DataFrame, required_columns: list) -> None:
    """Checks if required columns are in dataframe.  Returns ValueError if not found"""

    if not all([s in df.columns for s in required_columns]):
        raise ValueError(f"Patient data requires {required_columns}. The uploaded file had {df.columns}")
    
def set_table_import_time(table_name: str) -> None:
    """Sets date table imported in TableMetadata table"""

    import_time = dt.datetime.now()

    new_table_metadata = TableMetadata(table_name=table_name, time_imported=import_time)

    db.session.add(new_table_metadata)

    db.session.commit()
    

def format_and_import_patient_data(file_path: str) -> None:
    """
    Cleans and imports patient data from a CSV file into the database.

    Args:
        file_path (str): The relative file path to the CSV file.
    """

    # Delete all existing records in the Patient table
    # Patient.objects.all().delete()
    # try:
    # Load CSV into a pandas DataFrame

    header_line = get_header_line(file_path)

    pat_df = pd.read_csv(file_path, header=header_line)

    # Check if required columns exist
    required_columns = ['enterpriseid', 'patient age', 'patientsex', 'prim prvdr', 'status']

    validate_header_df(pat_df, required_columns)

    # Remove rows with null values
    pat_df.dropna(subset=required_columns, inplace=True)

    # Create Patient instances
    patient_records = [
        Patient(
            enterpriseid=row['enterpriseid'],
            age=row['patient age'],
            sex=row['patientsex'],
            prim_prov=row['prim prvdr'],
            status = row['status'],
            deceased = row['ptnt dcsd ysn'],
            prim_insurance_name = row['patient primary ins pkg name'],
            prim_insurance_type = row['patient primary ins pkg type'],
            sec_insurance_name = row['patient secondary ins pkg name'],
            sec_insurance_type = row['patient secondary ins pkg type'],
        )
        for _, row in pat_df.iterrows()
    ]

    # # Bulk insert records into the database
    # sqlengine = sa.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

    # with so.Session(sqlengine) as session:
    db.session.query(Patient).delete() # Clear existing Patient table of all entries
    db.session.bulk_save_objects(patient_records) # Bulk save all new patient records
    db.session.commit()    

    set_table_import_time(Patient.__tablename__)

    flash(f"Successfully imported {len(patient_records)} records.", category='success')

    # except FileNotFoundError:
    #     print(f"Error: File '{file_full_path}' not found.")
    # except pd.errors.EmptyDataError:
    #     print("Error: The file is empty or not a valid CSV.")
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}")


def format_and_import_medication_data(file_path: str) -> None:
    header_line = get_header_line(file_path)

    med_df = pd.read_csv(file_path, header=header_line)
    
    # Check if required columns exist
    required_columns = ['enterpriseid', 'med names (single)']

    validate_header_df(med_df, required_columns)

    # Remove rows with null values
    med_df.dropna(subset=required_columns, inplace=True)


        # print(row)
    medclasses = {
    'Insulin': "|".join([
        "insulin", "insulin aspart", "NovoLog", "Fiasp",
        "insulin lispro", "Humalog", "Admelog",
        "insulin glulisine", "Apidra",
        "regular insulin", "Humulin R", "Novolin R",
        "NPH insulin", "Humulin N", "Novolin N",
        "insulin detemir", "Levemir",
        "insulin glargine", "Lantus", "Toujeo", "Basaglar", "Semglee"
        "insulin degludec", "Tresiba",
        "insulin isophane/regular", "Humulin 70/30", "Novolin 70/30",
        "insulin lispro protamine/lispro", "Humalog Mix 75/25", "Humalog Mix 50/50",
        "insulin aspart protamine/aspart", "NovoLog Mix 70/30",
        "insulin inhalation", "Afrezza"
        ]),
    'GLP1': "|".join([
        'ozempic','rebylsus','wegovy','semaglutide',
        'mounjaro','zepbound', 'tirzepatide',
        'trulicity','dulaglutide', 
        'victoza', 'saxenda', 'liraglutide',
        'byetta', 'bydureon', 'exenatide', 
        'adlyxin', ' lixisenatide'
        ]), 
    'Metformin':"|".join([
        'janumet', 'glucophage', 'kombiglyze', 'jentadueto', 'glucovance', 'metformin'
        ]),
    'Statin':"|".join([
        "atorvastatin", "Lipitor",
        "fluvastatin", "Lescol",
        "fluvastatin extended-release", "Lescol XL",
        "lovastatin", "Mevacor",
        "lovastatin", "Altoprev",
        "pitavastatin", "Livalo",
        "pitavastatin", "Zypitamag",
        "pravastatin", "Pravachol",
        "rosuvastatin", "Crestor",
        "rosuvastatin", "Ezallor Sprinkle",
        "simvastatin", "Zocor"
        ]),
    'SSRI': "|".join([
        "fluoxetine", "Prozac",
        "fluoxetine", "Sarafem",
        "sertraline", "Zoloft",
        "citalopram", "Celexa",
        "escitalopram", "Lexapro",
        "paroxetine", "Paxil",
        "paroxetine", "Paxil CR",
        "paroxetine", "Brisdelle",
        "fluvoxamine", "Luvox",
        "fluvoxamine", "Luvox CR",
        "vilazodone", "Viibryd",
        "vortioxetine", "Trintellix"
        ]),
    'SNRI': "|".join([
        "venlafaxine", "Effexor",
        "venlafaxine extended-release", "Effexor XR",
        "desvenlafaxine", "Pristiq",
        "desvenlafaxine", "Khedezla",
        "duloxetine", "Cymbalta",
        "levomilnacipran", "Fetzima",
        "milnacipran", "Savella"  # Approved for fibromyalgia, not depression
        ]),
    'Benzo': "|".join([
        "alprazolam", "Xanax",
        "alprazolam extended-release", "Xanax XR",
        "clonazepam", "Klonopin",
        "diazepam", "Valium",
        "lorazepam", "Ativan",
        "chlordiazepoxide", "Librium",
        "oxazepam", "Serax",
        "temazepam", "Restoril",
        "triazolam", "Halcion",
        "midazolam", "Versed",
        "flurazepam", "Dalmane",
        "estazolam", "Prosom",
        "clobazam", "Onfi",
        "clorazepate", "Tranxene"
        ]),
    "Opioid": "|".join([
        "morphine", "MS Contin", "Roxanol", "Kadian",
        "codeine", "Tylenol with Codeine",
        "hydrocodone", "Vicodin", "Norco", "Lortab",
        "oxycodone", "OxyContin", "Roxicodone", "Percocet", "Percodan",
        "fentanyl", "Duragesic", "Actiq", "Sublimaze",
        "hydromorphone", "Dilaudid", "Exalgo",
        "methadone", "Dolophine",
        "meperidine", "Demerol",
        "buprenorphine", "Subutex", "Belbuca",
        "buprenorphine/naloxone", "Suboxone",
        "tramadol", "Ultram", "Ultracet",
        "tapentadol", "Nucynta"
        ]),
    'Thiazide': "|".join([
        "hydrochlorothiazide", "Microzide",
        "chlorthalidone", "Hygroton",
        "chlorothiazide", "Diuril",
        "indapamide", "Lozol",
        "metolazone", "Zaroxolyn",
        "bendroflumethiazide", "Naturetin",
        "methyclothiazide", "Enduron"
        ]),
    'Non-DHPCCB':"|".join([
        "verapamil", "Calan", "Calan SR", "Isoptin", "Isoptin SR", "Verelan", "Verelan PM",
        "diltiazem", "Cardizem", "Cardizem CD", "Cardizem LA", "Cartia XT", "Dilacor XR", "Tiazac", "Taztia XT"
        ]),
    'DHP-CCB':"|".join([
        "amlodipine", "Norvasc",
        "felodipine", "Plendil",
        "isradipine", "Dynacirc",
        "nicardipine", "Cardene", "Cardene SR",
        "nifedipine", "Adalat CC", "Procardia", "Procardia XL",
        "nisoldipine", "Sular",
        "clevidipine", "Cleviprex"
        ]),
    'ACE': "|".join([
        "benazepril", "Lotensin",
        "captopril", "Capoten",
        "enalapril", "Vasotec", "Epaned",
        "fosinopril", "Monopril",
        "lisinopril", "Prinivil", "Zestril", "Qbrelis",
        "moexipril", "Univasc",
        "perindopril", "Aceon",
        "quinapril", "Accupril",
        "ramipril", "Altace",
        "trandolapril", "Mavik"
        ]),
    'ARB':"|".join([
        "azilsartan", "Edarbi",
        "candesartan", "Atacand",
        "eprosartan", "Teveten",
        "irbesartan", "Avapro",
        "losartan", "Cozaar",
        "olmesartan", "Benicar",
        "telmisartan", "Micardis",
        "valsartan", "Diovan"
        ]),
    'BetaBlocker': "|".join([
            "atenolol", "Tenormin",
            "bisoprolol", "Zebeta",
            "carvedilol", "Coreg", "Coreg CR",
            "labetalol", "Trandate", "Normodyne",
            "metoprolol", "Lopressor", "Toprol XL",
            "nadolol", "Corgard",
            "propranolol", "Inderal", "Inderal LA", "Inderal XL", "InnoPran XL",
            "timolol", "Blocadren",
            "acebutolol", "Sectral",
            "betaxolol", "Kerlone",
            "esmolol", "Brevibloc",
            "nebivolol", "Bystolic",
            "pindolol", "Visken",
            "sotalol", "Betapace", "Betapace AF", "Sorine"
            ]),
    'Stimulant':"|".join([
        "amphetamine/dextroamphetamine", "Adderall", "Adderall XR",
        "dextroamphetamine", "Dexedrine", "Zenzedi", "ProCentra",
        "lisdexamfetamine", "Vyvanse",
        "methylphenidate", "Ritalin", "Ritalin SR", "Ritalin LA", "Concerta", "Daytrana", "Quillivant XR", "Quillichew ER",
        "dexmethylphenidate", "Focalin", "Focalin XR",
        "methamphetamine", "Desoxyn",
        "armodafinil", "Nuvigil",
        "modafinil", "Provigil",
        "phentermine", "Adipex-P", "Lomaira",
        "phentermine/topiramate", "Qsymia",
        "benzphetamine", "Didrex",
        "diethylpropion", "Tenuate"
        ]),
    'Atypical-Antidep':"|".join([
        "bupropion", "Wellbutrin", "Wellbutrin SR", "Wellbutrin XL", "Zyban", "Aplenzin", "Forfivo XL",
        "mirtazapine", "Remeron", "Remeron SolTab",
        "trazodone", "Desyrel", "Oleptro",
        "nefazodone", "Serzone",
        "vilazodone", "Viibryd",
        "vortioxetine", "Trintellix"
        ]),
    'Atypical-Antipsych':"|".join([
        "aripiprazole", "Abilify", "Abilify Maintena", "Aristada",
        "asenapine", "Saphris", "Secuado",
        "brexpiprazole", "Rexulti",
        "cariprazine", "Vraylar",
        "clozapine", "Clozaril", "Versacloz", "FazaClo",
        "iloperidone", "Fanapt",
        "lurasidone", "Latuda",
        "olanzapine", "Zyprexa", "Zyprexa Zydis", "Zyprexa Relprevv",
        "paliperidone", "Invega", "Invega Sustenna", "Invega Trinza",
        "quetiapine", "Seroquel", "Seroquel XR",
        "risperidone", "Risperdal", "Risperdal Consta", "Perseris",
        "ziprasidone", "Geodon"
        ]),
    'Typical-Antipsych':"|".join([
        "chlorpromazine", "Thorazine",
        "fluphenazine", "Prolixin",
        "haloperidol", "Haldol",
        "loxapine", "Loxitane", "Adasuve",
        "mesoridazine", "Serentil",
        "molindone", "Moban",
        "perphenazine", "Trilafon",
        "pimozide", "Orap",
        "prochlorperazine", "Compazine",
        "thioridazine", "Mellaril",
        "thiothixene", "Navane",
        "trifluoperazine", "Stelazine"
        ]),
    'PPI':"|".join([
        "omeprazole", "Prilosec", "Prilosec OTC",
        "esomeprazole", "Nexium", "Nexium 24HR",
        "lansoprazole", "Prevacid", "Prevacid 24HR", "Prevacid SoluTab",
        "dexlansoprazole", "Dexilant",
        "pantoprazole", "Protonix",
        "rabeprazole", "AcipHex",
        "esomeprazole/naproxen", "Vimovo"  # Combination product
        ]),
    'NSAID':"|".join([
        "ibuprofen", "Advil", "Motrin",
        "naproxen", "Aleve", "Naprosyn", "Anaprox",
        "celecoxib", "Celebrex",
        "diclofenac", "Voltaren", "Cataflam", "Zorvolex",
        "indomethacin", "Indocin", "Tivorbex",
        "meloxicam", "Mobic", "Vivlodex",
        "piroxicam", "Feldene",
        "ketorolac", "Toradol", "Acular",
        "etodolac", "Lodine",
        "nabumetone", "Relafen",
        "sulindac", "Clinoril",
        "oxaprozin", "Daypro",
        "mefenamic acid", "Ponstel",
        "flurbiprofen", "Ansaid",
        "fenoprofen", "Nalfon",
        "tolmetin", "Tolectin"
        ])
                
    }

    medclass_patterns = {key: re.compile(pattern, re.IGNORECASE) for key, pattern in medclasses.items()}

    def classify_medication(med_name):
        for medclass, pattern in medclass_patterns.items():
            if pattern.search(med_name):
                return medclass
        return None
            
    med_df['medclass'] = med_df['med names (single)'].map(classify_medication)

    med_records = [
        Medication(enterpriseid = row['enterpriseid'],
                   name = row['med names (single)'],
                   medclass = row['medclass'])
        for _, row in med_df.iterrows()
    ]

    db.session.query(Medication).delete()
    db.session.bulk_save_objects(med_records)
    db.session.commit()

    set_table_import_time(Medication.__tablename__)

    flash(f"Successfully imported {len(med_records)} records.", category='success')





def format_and_import_A1C_data(file_path: str) -> None:
    header_line = get_header_line(file_path)

    a1c_df = pd.read_csv(file_path, header=header_line)

    # Check if required columns exist
    required_columns = ['enterpriseid', 'labdate', 'labvalue']

    validate_header_df(a1c_df, required_columns)

    # Remove rows with null values
    a1c_df.dropna(subset=required_columns, inplace=True)


    def format_a1c(row):
        if isinstance(row, (int, float)):
            return float(row)
        elif isinstance(row, str):
            m_obj = re.match(r'\d+.\d(?=\s?%)',row.strip())
            return float(m_obj.group(0)) if m_obj else None
        else:
            return None

    # Apply the function to create the 'on_insulin' column
    a1c_df['labvalue'] = a1c_df['labvalue'].apply(format_a1c)

        
    a1c_df['labdate'] = a1c_df['labdate'].apply(lambda row: pd.to_datetime(row, errors='coerce').date())

    a1c_df = a1c_df.dropna()

    a1c_records = [
        A1C(enterpriseid = row['enterpriseid'],
                   labdate = row['labdate'],
                   labvalue = row['labvalue'])
        for _, row in a1c_df.iterrows()
    ]

    db.session.query(A1C).delete()
    db.session.bulk_save_objects(a1c_records)
    db.session.commit()

    set_table_import_time(A1C.__tablename__)

    flash(f"Successfully imported {len(a1c_records)} records.", category='success')





def format_and_import_BP_data(file_path: str) -> None:
    # Identify the correct header line
    header_line = get_header_line(file_path) 

    # Convert CSV to BP
    bp_df = pd.read_csv(file_path, header=header_line)

        # Check if required columns exist
    required_columns = ['enterpriseid', 'Enc BP', 'enc BP date']

    validate_header_df(bp_df, required_columns)

    # Remove rows with null values
    bp_df.dropna(subset=required_columns, inplace=True)

    # Compile a regex object for detecting numbers preceding a "/"
    sysbp_pattern = re.compile(r'\d+(?=\/\d+)', re.IGNORECASE)

    # Complile a regex object for pulling out numbers following a "/"
    diabp_pattern = re.compile(r'(?<=\d\/)\d+', re.IGNORECASE)

    # Map a function that returns the regex results of systolic blood pressure if a match is found
    bp_df['sysbp'] = bp_df['Enc BP'].map(lambda row: sysbp_pattern.search(row).group(0) if sysbp_pattern.search(row) else None)

    # Do the same for diastolic blood pressure
    bp_df["diabp"] = bp_df['Enc BP'].map(lambda row: diabp_pattern.search(row).group(0) if diabp_pattern.search(row) else None)

    # Convert BP to the date only from a datetime object    
    bp_df['enc BP date'] = bp_df['enc BP date'].apply(lambda row: pd.to_datetime(row, errors='coerce').date())

    # Create a list of BP model objects to be uploaded to the database
    bp_records = [
        BP(enterpriseid = row['enterpriseid'],
                   bpdate = row['enc BP date'],
                   sysbp = row['sysbp'],
                   diabp = row['diabp'])
        for _, row in bp_df.iterrows()
    ]

    db.session.query(BP).delete()  # Clear out existing entries 
    db.session.bulk_save_objects(bp_records) # Save all new records
    db.session.commit() # Commit to database

    set_table_import_time(BP.__tablename__)

    flash(f"Successfully imported {len(bp_records)} records.", category='success')



def format_and_import_RAF_data(file_path: str) -> None:
    """Process RAF data from a CSV file and update the database."""
    # Identify the correct header line
    header_line = get_header_line(file_path)

    # Load CSV data into a DataFrame
    raf_df = pd.read_csv(file_path, header=header_line)

        # Check if required columns exist
    required_columns = ['enterpriseid', 'HCC RAF score']

    validate_header_df(raf_df, required_columns)

    # Remove rows with null values
    raf_df.dropna(subset=required_columns, inplace=True)

    # Map rows to `PatientComplexity` objects
    raf_records = [
        RAFScore(
            enterpriseid=row['enterpriseid'],
            raf_score=row['HCC RAF score']  # Ensure this matches your CSV column name
        )
        for _, row in raf_df.iterrows()
    ]

    # Clear existing entries and add new records
    db.session.query(RAFScore).delete()
    db.session.bulk_save_objects(raf_records)

    # Commit changes to the database
    db.session.commit()

    set_table_import_time(RAFScore.__tablename__)

    flash(f"Successfully imported {len(raf_records)} records.", category='success')



def format_and_import_encounter_data(file_path: str) -> None:

    header_line = get_header_line(file_path)

    enc_df = pd.read_csv(file_path, header=header_line)

    # Check if required columns exist
    required_columns = ['cln enc id', 'enterpriseid', 'prvdrid', 'cln enc date', 'appttype']

    validate_header_df(enc_df, required_columns)

    # Remove rows with null values
    enc_df.dropna(subset=required_columns, inplace=True)


    enc_df['cln enc date'] = enc_df['cln enc date'].apply(lambda row: pd.to_datetime(row, errors='coerce').date())

    enc_records = [
        Encounter(
            encounterid = row['cln enc id'],
            enterpriseid = row['enterpriseid'],
            providerid = row['prvdrid'],
            enc_date = row['cln enc date'],
            appt_type = row['appttype'],
        )
        for _, row in enc_df.iterrows()
    ]

    
    # Clear existing entries and add new records
    db.session.query(Encounter).delete()
    db.session.bulk_save_objects(enc_records)

    # Commit changes to the database
    db.session.commit()

    set_table_import_time(Encounter.__tablename__)

    flash(f"Successfully imported {len(enc_records)} records.", category='success')




def format_and_import_enc_dx_data(file_path: str) -> None:

    header_line = get_header_line(file_path)

    encdx_df = pd.read_csv(file_path, header=header_line)

    # Check if required columns exist
    required_columns = ['cln enc id', 'icd10encounterdiagcode']

    validate_header_df(encdx_df, required_columns)

    # Remove rows with null values
    encdx_df.dropna(subset=required_columns, inplace=True)
    
        
    dxgroups = {
        'Diabetes':'|'.join(['E08','E09','E10','E11','E13'])
    }

    dxgroup_patterns = {key: re.compile(pattern, re.IGNORECASE) for key, pattern in dxgroups.items()}

    def classify_dx(dxcode):
        for dxgroup, pattern in dxgroup_patterns.items():
            if pattern.search(dxcode):
                return dxgroup
            return None
        
    encdx_df['dxgroup'] = encdx_df['icd10encounterdiagcode'].map(classify_dx)

    encdx_records = [
        EncounterDx(
            encounterid = row['cln enc id'],
            ICD_code = row['icd10encounterdiagcode'],
            dxgroup = row['dxgroup']

        )
        for _, row in encdx_df.iterrows()
    ]

    
    # Clear existing entries and add new records
    db.session.query(EncounterDx).delete()
    db.session.bulk_save_objects(encdx_records)

    # Commit changes to the database
    db.session.commit()

    set_table_import_time(EncounterDx.__tablename__)

    flash(f"Successfully imported {len(encdx_records)} records.", category='success')




def format_and_import_enc_proc_data(file_path: str) -> None:

    header_line = get_header_line(file_path)

    enc_df = pd.read_csv(file_path, header=header_line)

    # Check if required columns exist
    required_columns = ['cln enc id', 'enc srv proccode']

    validate_header_df(enc_df, required_columns)

    # Remove rows with null values
    enc_df.dropna(subset=required_columns, inplace=True)

    enc_records = [
        EncounterProc(
            encounterid = row['cln enc id'],
            proc_code = row['enc srv proccode']
        )
        for _, row in enc_df.iterrows()
    ]

    
    # Clear existing entries and add new records
    db.session.query(EncounterProc).delete()
    db.session.bulk_save_objects(enc_records)

    # Commit changes to the database
    db.session.commit()

    set_table_import_time(EncounterProc.__tablename__)

    flash(f"Successfully imported {len(enc_records)} records.", category='success')




def format_and_import_provider_data(file_path: str) -> None:

    header_line = get_header_line(file_path)

    prov_df = pd.read_csv(file_path, header=header_line)

    # Check if required columns exist
    required_columns = ['prvdrid', 'prvdr', 'prvdrfrstnme', 'prvdrlstnme', 'prvdrtype']

    validate_header_df(prov_df, required_columns)

    # Remove rows with null values
    prov_df.dropna(subset=required_columns, inplace=True)
    

    prov_records = [
        Provider(
            providerid = row['prvdrid'],
            provider = row['prvdr'],
            prov_fname = row['prvdrfrstnme'],
            prov_lname = row['prvdrlstnme'],
            prov_type = row['prvdrtype']
        )
        for _, row in prov_df.iterrows()
    ]

    
    # Clear existing entries and add new records
    db.session.query(Provider).delete()
    db.session.bulk_save_objects(prov_records)

    # Commit changes to the database
    db.session.commit()

    set_table_import_time(Provider.__tablename__)

    flash(f"Successfully imported {len(prov_records)} records.", category='success')