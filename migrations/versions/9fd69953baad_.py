"""empty message

Revision ID: 9fd69953baad
Revises: aae7ba5c3400
Create Date: 2022-06-03 10:17:54.898420

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9fd69953baad'
down_revision = 'aae7ba5c3400'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('venues')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('venues',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('city', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('state', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('address', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('phone', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('image_link', sa.VARCHAR(length=500), autoincrement=False, nullable=True),
    sa.Column('facebook_link', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('genres', postgresql.BYTEA(), autoincrement=False, nullable=True),
    sa.Column('seeking_talent', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('seeking_description', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('website', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='venues_pkey')
    )
    # ### end Alembic commands ###