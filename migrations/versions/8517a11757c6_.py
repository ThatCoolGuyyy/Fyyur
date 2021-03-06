"""empty message

Revision ID: 8517a11757c6
Revises: 4f61e1998c83
Create Date: 2022-05-25 13:35:14.769115

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8517a11757c6'
down_revision = '4f61e1998c83'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('show')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('show',
    sa.Column('show_id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('venue_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('artist_name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('artist_image_link', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('start_time', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], name='show_artist_id_fkey'),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], name='show_venue_id_fkey'),
    sa.PrimaryKeyConstraint('show_id', name='show_pkey')
    )
    # ### end Alembic commands ###
