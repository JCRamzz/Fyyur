"""changed relationships between artists and venues

Revision ID: 7a28c474398d
Revises: 57d963e294f6
Create Date: 2021-02-23 04:29:20.745812

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a28c474398d'
down_revision = '57d963e294f6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('Artist_venue_id_fkey', 'Artist', type_='foreignkey')
    op.drop_column('Artist', 'venue_id')
    op.add_column('shows', sa.Column('venues_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'shows', 'Venue', ['venues_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'shows', type_='foreignkey')
    op.drop_column('shows', 'venues_id')
    op.add_column('Artist', sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('Artist_venue_id_fkey', 'Artist', 'Venue', ['venue_id'], ['id'])
    # ### end Alembic commands ###
