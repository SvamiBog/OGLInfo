"""Rename autoad → auto_ad and autoadhistory → auto_ad_history

Revision ID: 817b885a26f0
Revises: 3a5621d9e77d
Create Date: 2025-05-02 17:28:19.503420

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '817b885a26f0'
down_revision: Union[str, None] = '3a5621d9e77d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('autoad', 'auto_ad')
    op.rename_table('autoadhistory', 'auto_ad_history')


def downgrade() -> None:
    op.rename_table('auto_ad', 'autoad')
    op.rename_table('auto_ad_history', 'autoadhistory')