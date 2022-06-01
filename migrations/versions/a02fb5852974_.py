"""empty message

Revision ID: a02fb5852974
Revises: 59011ea2eaaf
Create Date: 2022-05-26 12:48:44.657417

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a02fb5852974'
down_revision = '59011ea2eaaf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Show', 'venue_name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Show', 'venue_name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###