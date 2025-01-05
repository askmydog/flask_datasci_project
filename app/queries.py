from app import app, db
from sqlalchemy import select, func, case, or_, desc
from sqlalchemy.orm import aliased
from sqlalchemy.sql import over
from .models import *
import datetime as dt

def diabetics_query():
    # subquery where latest date that an A1C is obtained
    latest_date_subq = (
        select(
            A1C.enterpriseid,
            func.max(A1C.labdate).label('latest_date')
        )
        .group_by(A1C.enterpriseid)
        .subquery()
    )

    # Create new subquery that returns the labvalue associated with the latest A1C date
    latest_a1c_subq = (
        select(
            A1C.enterpriseid,
            latest_date_subq.c.latest_date,
            A1C.labvalue
        )
        .join(latest_date_subq,
              (A1C.enterpriseid == latest_date_subq.c.enterpriseid)
              & (A1C.labdate == latest_date_subq.c.latest_date)
        )
        .subquery()
    )

    insulin_count = (
        select(
            Medication.enterpriseid,
            func.count(Medication.medclass).label('insulin_count')
        )
        .where(Medication.medclass=='Insulin')
        .group_by(Medication.enterpriseid)
        .subquery()
    )

    glp1_count_subq = (
        select(
            Medication.enterpriseid,
            func.count(Medication.medclass).label("glp1_count")
        )
        .where(Medication.medclass == "GLP1")
        .group_by(Medication.enterpriseid)
        .subquery()
    )


    stmt = (sa.select(
        Patient.enterpriseid,
        Patient.age,
        Patient.sex,
        Patient.prim_prov,
        func.strftime('%m/%d/%Y', latest_a1c_subq.c.latest_date),
        latest_a1c_subq.c.labvalue,
        case(
            (insulin_count.c.insulin_count > 0, "True"),
            else_= "False"
        ).label('on_insulin'),
        case(
            (glp1_count_subq.c.glp1_count > 0, "True"),
            else_= "False"
        ).label('on_glp1')

        )
        .where(Patient.status == "a")
        .join(latest_a1c_subq,
              (Patient.enterpriseid == latest_a1c_subq.c.enterpriseid)
        )
        .join(insulin_count,
              (Patient.enterpriseid == insulin_count.c.enterpriseid),
              isouter = True
        )
        .join(glp1_count_subq,
              Patient.enterpriseid == glp1_count_subq.c.enterpriseid,
              isouter= True)
        .where(latest_a1c_subq.c.labvalue >= 8)
        .order_by(latest_a1c_subq.c.labvalue)
    )

    result = db.session.execute(statement=stmt)

    # print(result.fetchmany(10))
    return result

def hypertensives_query():
    sysbp_thres = 140
    diabp_thres = 90


    # Step 1: Aggregate data by date to get the minimum sysbp and diabp for each date
    aggregated_bp_subq = (
        select(
            BP.enterpriseid,
            BP.bpdate,
            func.min(BP.sysbp).label('min_sysbp'),
            func.min(BP.diabp).label('min_diabp')
        )
        .group_by(BP.enterpriseid, BP.bpdate)  # Group by enterprise and date
        .subquery()
    )

    # Step 2: Assign row numbers after aggregation
    row_number_subq = (
        select(
            aggregated_bp_subq.c.enterpriseid,
            aggregated_bp_subq.c.bpdate,
            aggregated_bp_subq.c.min_sysbp.label('sysbp'),
            aggregated_bp_subq.c.min_diabp.label('diabp'),
            func.row_number()
            .over(
                partition_by=aggregated_bp_subq.c.enterpriseid,
                order_by=aggregated_bp_subq.c.bpdate
            )
            .label('row_number'),
        )
        .subquery()
    )

    # Step 3: Flag rows above the threshold
    group_identifier_subquery = (
        select(
            row_number_subq.c.enterpriseid,
            row_number_subq.c.bpdate,
            row_number_subq.c.row_number,
            row_number_subq.c.sysbp,
            row_number_subq.c.diabp,
            case(
                (or_(
                    row_number_subq.c.sysbp > 140,
                    row_number_subq.c.diabp > 90
                ), 1),
                else_=0
            ).label('above_threshold_flag'),
        )
        .subquery()
    )

    # Step 4: Assign group IDs for consecutive rows
    gap_group_subq = (
        select(
            group_identifier_subquery.c.enterpriseid,
            group_identifier_subquery.c.bpdate,
            group_identifier_subquery.c.sysbp,
            group_identifier_subquery.c.diabp,
            group_identifier_subquery.c.row_number,
            (group_identifier_subquery.c.row_number
            - func.sum(group_identifier_subquery.c.above_threshold_flag)
            .over(
                partition_by=group_identifier_subquery.c.enterpriseid,
                order_by=group_identifier_subquery.c.row_number
            )
            ).label("group_id"),
        )
        .where(group_identifier_subquery.c.above_threshold_flag == 1)
        .subquery()
    )

    # Step 5: Find the most recent record for each group
    latest_record_subq = (
        select(
            gap_group_subq.c.enterpriseid,
            gap_group_subq.c.group_id,
            func.max(gap_group_subq.c.bpdate).label("latest_bpdate"),
        )
        .group_by(gap_group_subq.c.enterpriseid, gap_group_subq.c.group_id)
        .subquery()
    )

    # Step 6: Count consecutive rows in each group
    group_count_subq = (
        select(
            gap_group_subq.c.enterpriseid,
            gap_group_subq.c.group_id,
            func.count().label("consecutive_count"),
        )
        .group_by(gap_group_subq.c.enterpriseid, gap_group_subq.c.group_id)
        .subquery()
    )

    # Step 7: Combine filters for groups with 3+ rows where the last record is the most recent
    final_query = (
        select(
            Patient.enterpriseid,
            Patient.age,
            Patient.sex,
            Patient.prim_prov,
            func.strftime('%m/%d/%Y', gap_group_subq.c.bpdate),
            gap_group_subq.c.sysbp,
            gap_group_subq.c.diabp,
        )
        .where(Patient.status == 'a')
        .join(
            group_count_subq,
            (gap_group_subq.c.enterpriseid == group_count_subq.c.enterpriseid)
            & (gap_group_subq.c.group_id == group_count_subq.c.group_id),
        )
        .join(
            latest_record_subq,
            (gap_group_subq.c.enterpriseid == latest_record_subq.c.enterpriseid)
            & (gap_group_subq.c.group_id == latest_record_subq.c.group_id),
        )
        .join(
            Patient,
            gap_group_subq.c.enterpriseid == Patient.enterpriseid
        )
        .where(group_count_subq.c.consecutive_count >= 3)  # At least 3 consecutive rows
        .where(gap_group_subq.c.bpdate == latest_record_subq.c.latest_bpdate)  # Latest record condition
        .order_by(gap_group_subq.c.sysbp, gap_group_subq.c.diabp)
    )

    result = db.session.execute(final_query)

    result.fetchmany(10)

    return result

def patient_complexity_query():
    """Query to calculate average patient complexity metrics grouped by primary provider."""

    # Subquery: Calculate medication count per enterprise ID
    med_count_subq = (
        select(
            Medication.enterpriseid,
            func.count(Medication.name).label('med_count')
        )
        .group_by(Medication.enterpriseid)
        .subquery()
    )

    diabetic_count_subq = (
        select(
            Encounter.enterpriseid,
            func.count(EncounterDx.dxgroup).label('diabetic_count')
        )
        .where(EncounterDx.dxgroup == "Diabetes")
        .group_by(Encounter.enterpriseid)
        .join(Encounter, 
              Encounter.encounterid == EncounterDx.encounterid)
        .subquery()
    )

    # Subquery: Combine patient data, medication count, and RAF score
    p_complex_q = (
        select(
            Patient.enterpriseid,
            Patient.age,
            Patient.prim_prov,
            Patient.sex,
            med_count_subq.c.med_count,
            case((diabetic_count_subq.c.diabetic_count>0,1),
                 else_=0).label("is_diabetic"),
            RAFScore.raf_score,
        )
        .where(Patient.status == 'a')
        .join(med_count_subq, Patient.enterpriseid == med_count_subq.c.enterpriseid)
        .join(RAFScore, Patient.enterpriseid == RAFScore.enterpriseid)
        .join(diabetic_count_subq, Patient.enterpriseid == diabetic_count_subq.c.enterpriseid, isouter=True)
        .subquery()
    )

    # Final query: Calculate averages grouped by primary provider
    final_query = (
        select(
            p_complex_q.c.prim_prov,
            func.count(p_complex_q.c.enterpriseid).label('patient_count'),
            func.avg(p_complex_q.c.age).label('avg_age'),
            func.avg(p_complex_q.c.med_count).label('avg_med_count'),
            func.avg(p_complex_q.c.raf_score).label('avg_raf_score'),
            (func.sum(p_complex_q.c.is_diabetic) / func.count(p_complex_q.c.enterpriseid)).label("perc_diabetic")
        )
        .group_by(p_complex_q.c.prim_prov)
    )

    # Execute the final query
    result = db.session.execute(final_query)

    # Fetch all results and return them
    return result

def medicare_diabetes_query():
    pass