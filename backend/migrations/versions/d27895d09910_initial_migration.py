"""Initial migration

Revision ID: d27895d09910
Revises: 
Create Date: 2025-12-24 09:14:34.037639

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd27895d09910'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('actors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('birth_date', sa.Date(), nullable=False),
    sa.Column('gender', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('movies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=120), nullable=False),
    sa.Column('release_date', sa.Date(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    op.drop_table('movies')
    op.drop_table('actors')
    # ### end Alembic commands ###
