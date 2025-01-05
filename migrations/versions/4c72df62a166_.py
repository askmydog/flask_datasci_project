"""empty message

Revision ID: 4c72df62a166
Revises: 
Create Date: 2025-01-04 21:31:17.589665

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c72df62a166'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('provider',
    sa.Column('providerid', sa.Integer(), nullable=False),
    sa.Column('provider', sa.String(length=40), nullable=False),
    sa.Column('prov_fname', sa.String(length=40), nullable=False),
    sa.Column('prov_lname', sa.String(length=40), nullable=False),
    sa.Column('prov_type', sa.String(length=60), nullable=False),
    sa.PrimaryKeyConstraint('providerid'),
    sa.UniqueConstraint('providerid')
    )
    op.create_table('table_metadata',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('table_name', sa.String(length=40), nullable=False),
    sa.Column('time_imported', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('table_metadata', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_table_metadata_table_name'), ['table_name'], unique=False)

    op.create_table('patient',
    sa.Column('enterpriseid', sa.Integer(), nullable=False),
    sa.Column('age', sa.Integer(), nullable=False),
    sa.Column('sex', sa.String(length=4), nullable=False),
    sa.Column('prim_prov', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=1), nullable=False),
    sa.Column('deceased', sa.String(length=1), nullable=True),
    sa.Column('prim_insurance_name', sa.String(length=60), nullable=True),
    sa.Column('prim_insurance_type', sa.String(length=40), nullable=True),
    sa.Column('sec_insurance_name', sa.String(length=60), nullable=True),
    sa.Column('sec_insurance_type', sa.String(length=40), nullable=True),
    sa.ForeignKeyConstraint(['prim_prov'], ['provider.providerid'], ),
    sa.PrimaryKeyConstraint('enterpriseid'),
    sa.UniqueConstraint('enterpriseid')
    )
    op.create_table('a1_c',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('enterpriseid', sa.Integer(), nullable=False),
    sa.Column('labdate', sa.Date(), nullable=False),
    sa.Column('labvalue', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['enterpriseid'], ['patient.enterpriseid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('a1_c', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_a1_c_enterpriseid'), ['enterpriseid'], unique=False)

    op.create_table('bp',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('enterpriseid', sa.Integer(), nullable=False),
    sa.Column('bpdate', sa.Date(), nullable=False),
    sa.Column('sysbp', sa.Integer(), nullable=True),
    sa.Column('diabp', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['enterpriseid'], ['patient.enterpriseid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('bp', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_bp_enterpriseid'), ['enterpriseid'], unique=False)

    op.create_table('encounter',
    sa.Column('encounterid', sa.Integer(), nullable=False),
    sa.Column('enterpriseid', sa.Integer(), nullable=False),
    sa.Column('providerid', sa.Integer(), nullable=False),
    sa.Column('enc_date', sa.Date(), nullable=False),
    sa.Column('appt_type', sa.String(length=20), nullable=False),
    sa.ForeignKeyConstraint(['enterpriseid'], ['patient.enterpriseid'], ),
    sa.ForeignKeyConstraint(['providerid'], ['provider.providerid'], ),
    sa.PrimaryKeyConstraint('encounterid')
    )
    with op.batch_alter_table('encounter', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_encounter_enterpriseid'), ['enterpriseid'], unique=False)
        batch_op.create_index(batch_op.f('ix_encounter_providerid'), ['providerid'], unique=False)

    op.create_table('medication',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('enterpriseid', sa.Integer(), nullable=False),
    sa.Column('name', sa.Integer(), nullable=False),
    sa.Column('medclass', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['enterpriseid'], ['patient.enterpriseid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('medication', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_medication_enterpriseid'), ['enterpriseid'], unique=False)

    op.create_table('raf_score',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('enterpriseid', sa.Integer(), nullable=False),
    sa.Column('raf_score', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['enterpriseid'], ['patient.enterpriseid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('raf_score', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_raf_score_enterpriseid'), ['enterpriseid'], unique=False)

    op.create_table('encounter_dx',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('encounterid', sa.Integer(), nullable=False),
    sa.Column('ICD_code', sa.String(length=10), nullable=False),
    sa.ForeignKeyConstraint(['encounterid'], ['encounter.encounterid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('encounter_proc',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('encounterid', sa.Integer(), nullable=False),
    sa.Column('proc_code', sa.String(length=10), nullable=False),
    sa.ForeignKeyConstraint(['encounterid'], ['encounter.encounterid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('encounter_proc')
    op.drop_table('encounter_dx')
    with op.batch_alter_table('raf_score', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_raf_score_enterpriseid'))

    op.drop_table('raf_score')
    with op.batch_alter_table('medication', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_medication_enterpriseid'))

    op.drop_table('medication')
    with op.batch_alter_table('encounter', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_encounter_providerid'))
        batch_op.drop_index(batch_op.f('ix_encounter_enterpriseid'))

    op.drop_table('encounter')
    with op.batch_alter_table('bp', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_bp_enterpriseid'))

    op.drop_table('bp')
    with op.batch_alter_table('a1_c', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_a1_c_enterpriseid'))

    op.drop_table('a1_c')
    op.drop_table('patient')
    with op.batch_alter_table('table_metadata', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_table_metadata_table_name'))

    op.drop_table('table_metadata')
    op.drop_table('provider')
    # ### end Alembic commands ###