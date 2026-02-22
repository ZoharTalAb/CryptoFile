from infrastructure.db.session import engine, Base
from infrastructure.db import models

Base.metadata.create_all(bind=engine)
