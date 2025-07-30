"""Add host_id to bookings

Revision ID: 9ee36b40fea4
Revises: c7b48ea44ea7
Create Date: 2025-07-28 14:40:53.697740
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ee36b40fea4'
down_revision = 'c7b48ea44ea7'
branch_labels = None
depends_on = None


def upgrade():
    # Check if the 'host_id' column already exists
    inspector = sa.inspect(op.get_bind())
    columns = [col['name'] for col in inspector.get_columns('bookings')]
    
    # If the 'host_id' column doesn't exist, add it
    if 'host_id' not in columns:
        with op.batch_alter_table('bookings', schema=None) as batch_op:
            batch_op.add_column(sa.Column('host_id', sa.String(length=36), nullable=True))  # host_id column added as nullable

    # Update the host_id column with data from the places table
    op.execute("""
        UPDATE bookings
        SET host_id = (
            SELECT host_id FROM places WHERE places.id = bookings.place_id
        )
    """)

    # Now, make the host_id column non-nullable
    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.alter_column('host_id', nullable=False)
    
    # Add the foreign key constraint to host_id with a manually written SQL query
    op.execute("""
        ALTER TABLE bookings
        ADD CONSTRAINT fk_bookings_host_id
        FOREIGN KEY (host_id) REFERENCES hosts(id) ON DELETE CASCADE
    """)


def downgrade():
    # Directly drop the foreign key constraint using the SQL statement
    op.execute("""
        ALTER TABLE bookings
        DROP CONSTRAINT fk_bookings_host_id
    """)
    
    # Drop the host_id column
    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.drop_column('host_id')
