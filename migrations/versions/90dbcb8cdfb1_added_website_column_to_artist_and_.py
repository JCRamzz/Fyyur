"""added website column  to artist and venue tables

Revision ID: 90dbcb8cdfb1
Revises: 5a9ae1e547fc
Create Date: 2021-03-01 03:49:45.098037

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90dbcb8cdfb1'
down_revision = '5a9ae1e547fc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('website', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'website')
    op.drop_column('Artist', 'website')
    # ### end Alembic commands ###
