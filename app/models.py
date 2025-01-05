from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from datetime import date, datetime



class TableMetadata(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    table_name: so.Mapped[str] = so.mapped_column(sa.String(40), index=True)
    time_imported: so.Mapped[datetime] = so.mapped_column(sa.DateTime())

    def __repr__(self):
        return f'({self.id}) {self.table_name}, {self.time_imported}'
    


class Provider(db.Model):
    providerid: so.Mapped[int] = so.mapped_column(unique=True, primary_key=True)
    provider: so.Mapped[str] = so.mapped_column(sa.String(40))
    prov_fname: so.Mapped[str] = so.mapped_column(sa.String(40))
    prov_lname: so.Mapped[str] = so.mapped_column(sa.String(40))
    prov_type: so.Mapped[str] = so.mapped_column(sa.String(60))

    def __repr__(self):
        return f'({self.providerid}) {self.provider}'



class Patient(db.Model):
    enterpriseid: so.Mapped[int] = so.mapped_column(sa.Integer(), unique=True, primary_key=True)
    age: so.Mapped[int] = so.mapped_column(sa.Integer())
    sex: so.Mapped[str] = so.mapped_column(sa.String(4))
    prim_prov: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Provider.providerid))
    status: so.Mapped[str] = so.mapped_column(sa.String(1))
    deceased: so.Mapped[Optional[str]] = so.mapped_column(sa.String(1))
    prim_insurance_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(60))
    prim_insurance_type: so.Mapped[Optional[str]] = so.mapped_column(sa.String(40))
    sec_insurance_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(60))
    sec_insurance_type: so.Mapped[Optional[str]] = so.mapped_column(sa.String(40))

    def __repr__(self):
        return f'id={self.enterpriseid}, {self.age} {self.sex}, {self.prim_prov}'
    


class Encounter(db.Model):
    encounterid: so.Mapped[int] = so.mapped_column(primary_key=True)
    enterpriseid: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Patient.enterpriseid), index=True)
    providerid: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Provider.providerid), index=True)
    enc_date: so.Mapped[date] = so.mapped_column(sa.Date())
    appt_type: so.Mapped[str] = so.mapped_column(sa.String(20))

    def __repr__(self):
        return f'({self.encounterid}), {self.enterpriseid}, {self.providerid}, {self.enc_date}'



class EncounterDx(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    encounterid: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Encounter.encounterid))
    ICD_code: so.Mapped[str] = so.mapped_column(sa.String(10))
    dxgroup: so.Mapped[Optional[str]] = so.mapped_column(sa.String(40), nullable=True)

    def __repr__(self):
        return f'({self.id}) {self.encounterid}, {self.ICD_code}'



class EncounterProc(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    encounterid: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Encounter.encounterid))
    proc_code: so.Mapped[str] = so.mapped_column(sa.String(10))

    def __repr__(self):
        return f'({self.id}) {self.encounterid}, {self.proc_code}'



class A1C(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    enterpriseid: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Patient.enterpriseid), index=True)
    labdate: so.Mapped[date] = so.mapped_column(sa.Date())
    labvalue: so.Mapped[float] = so.mapped_column(sa.Float())

    def __repr__(self):
        return f'id={self.id}, {self.enterpriseid}, {self.labdate}, {self.labvalue}'
    


class BP(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    enterpriseid: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Patient.enterpriseid), index=True)
    bpdate: so.Mapped[date] = so.mapped_column(sa.Date())
    sysbp: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer())
    diabp: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer())

    def __repr__(self):
        return f'({self.id}) {self.enterpriseid}, {self.bpdate}, {self.sysbp}/{self.diabp}'



class Medication(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    enterpriseid: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Patient.enterpriseid), index=True)
    name: so.Mapped[int] = so.mapped_column(sa.Integer())
    medclass: so.Mapped[Optional[str]] = so.mapped_column(sa.String())

    def __repr__(self):
        return f'({self.id}) {self.enterpriseid}, {self.name}, {self.medclass}'
    


class RAFScore(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    enterpriseid: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Patient.enterpriseid), index=True)
    raf_score: so.Mapped[float] = so.mapped_column(sa.Float())

    def __repr__(self):
        return f'({self.id}) {self.enterpriseid}, RAF={self.raf_score}'
    




# class EncounterDx(db.Model):
#     id: so.Mapped[int] = so.mapped_column(primary_key=True)
#     enterpriseid: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Patient.enterpriseid), index=True)
#     prov: so.Mapped[str] = so.mapped_column(sa.String(40), index=True)
#     enc_date: so.Mapped[date] = so.mapped_column(sa.Date())
#     dx: so.Mapped[str] = so.mapped_column(sa.String(10), index=True)
#     dxgroup: so.Mapped[Optional[str]] = so.mapped_column(sa.String(10), index=True)
    
#     def __repr__(self):
#         return f'({self.id}) {self.enterpriseid}, {self.enc_prov}, {self.enc_date}, {self.enc_dx}'
    
# class EncounterProc(db.Model):
#     id: so.Mapped[int] = so.mapped_column(primary_key=True)
#     enterpriseid: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Patient.enterpriseid), index=True)
