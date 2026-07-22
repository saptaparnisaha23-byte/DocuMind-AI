from app.auth.database import Base
from app.auth.database import engine

from app.auth.models import User

Base.metadata.create_all(bind=engine)

print("Database created successfully!")