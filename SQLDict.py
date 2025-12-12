import random
import string
import hashlib
from time import time
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

URL = "sqlite:///./SQLDict.db"
engine = create_engine(URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    idn = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

db = SessionLocal()

def create_user(db, username, email):
    db_user = User(username=username, email=email)
    db_user.idn = int.from_bytes(hashlib.sha256(db_user.email.encode()).digest()[:8], signed=True)
    db.add(db_user)
    #db.commit()
    #db.refresh(db_user)
    return db_user

def random_user(db):
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choices(characters, k=20))
    return create_user(db, random_string, random_string)

for i in range(0, db.query(User).count(), 100_000):
    for o in db.query(User).offset(i).limit(100_000):
        db.delete(o)
    db.commit()

for i in range(1_000_000):
    c = random_user(db)
    if i % 10_000 == 0:
        print(i)
    if i % 100_000 == 0:
        db.commit()

email = "tonylovesdarkred@gmail.com"
idn = int.from_bytes(hashlib.sha256(email.encode()).digest()[:8], signed=True)
Tony = create_user(db, "PoeticDeath", email)
db.commit()

start = time()
db.query(User).filter(User.idn == idn).first()
print("Dict:", time() - start)
start = time()
db.query(User).filter(User.email == email).first()
print("List:", time() - start)
