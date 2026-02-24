# backend/init_db.py
from database import engine, Base
import models

# Isso diz ao SQLAlchemy para ler as classes e criar o arquivo .db fisicamente
Base.metadata.create_all(bind=engine)
print("Banco de dados criado com sucesso!")