"""Insert data into users table

Revision ID: 4dc13ed861d5
Revises: f37ddfabed22
Create Date: 2023-09-25 00:05:17.421222

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4dc13ed861d5'
down_revision: Union[str, None] = 'f37ddfabed22'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
