"""empty message

Revision ID: c1eb9ba929bf
Revises: 4c72df62a166
Create Date: 2025-01-05 17:16:20.765663

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1eb9ba929bf'
down_revision = '4c72df62a166'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('encounter_dx', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dxgroup', sa.String(length=40), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('encounter_dx', schema=None) as batch_op:
        batch_op.drop_column('dxgroup')

    # ### end Alembic commands ###
