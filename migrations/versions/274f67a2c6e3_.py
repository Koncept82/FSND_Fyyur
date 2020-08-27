"""empty message

Revision ID: 274f67a2c6e3
Revises: c07f0fcef486
Create Date: 2020-08-27 12:17:59.267096

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '274f67a2c6e3'
down_revision = 'c07f0fcef486'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'genres')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('genres', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
