from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "postgresql://your_user:your_password@localhost/otomoto_data"

engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session
