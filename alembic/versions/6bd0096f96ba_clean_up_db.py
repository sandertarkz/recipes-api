"""Clean up db

Revision ID: 6bd0096f96ba
Revises: f37df9a60c66
Create Date: 2025-01-22 15:22:42.434047

"""
from typing import Sequence, Union
import sqlmodel
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6bd0096f96ba'
down_revision: Union[str, None] = 'f37df9a60c66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # Drop the dependent table first
    op.drop_table('sites_companies_links')
    
    # Drop other tables
    op.drop_index('ix_companies_account_id', table_name='companies')
    op.drop_table('companies')
    op.drop_table('accounts')
    op.drop_table('sites')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sites_companies_links',
    sa.Column('site_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('company_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], name='sites_companies_links_company_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['site_id'], ['sites.id'], name='sites_companies_links_site_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('site_id', 'company_id', name='sites_companies_links_pkey')
    )
    op.create_table('sites',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='sites_pkey')
    )
    op.create_table('accounts',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('accounts_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='accounts_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('companies',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('account_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name='companies_account_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='companies_pkey')
    )
    op.create_index('ix_companies_account_id', 'companies', ['account_id'], unique=False)
    # ### end Alembic commands ###
