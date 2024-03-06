from sqlalchemy import Table, Column, Integer, String, MetaData

metadata = MetaData()

exercises = Table(
    "exercises",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("Exercise", String, nullable=False),
    Column("Timer", Integer, nullable=False),
    Column("Repetitions", Integer, nullable=False),

)

