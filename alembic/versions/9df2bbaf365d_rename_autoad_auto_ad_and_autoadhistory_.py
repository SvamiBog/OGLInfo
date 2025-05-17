"""Rename autoad → auto_ad and autoadhistory → auto_ad_history

Revision ID: 9df2bbaf365d
Revises: 817b885a26f0
Create Date: 2025-05-02 17:34:04.382499

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9df2bbaf365d'
down_revision: Union[str, None] = '817b885a26f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.rename_table('autoad', 'auto_ad')
    op.rename_table('autoadhistory', 'auto_ad_history')


def downgrade():
    op.rename_table('auto_ad', 'autoad')
    op.rename_table('auto_ad_history', 'autoadhistory')
