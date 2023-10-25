from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os


load_dotenv()

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('CONTAINER_NAME')}/{os.getenv('POSTGRES_DATABASE')}", echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()
