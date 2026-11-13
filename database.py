import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Archivo SQLite local que guardará los mensajes pendientes de aprobación
DATABASE_URL = "sqlite+aiosqlite:///./otrabogota.db"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


# Dependencia de FastAPI para inyectar la sesión en las rutas
async def get_db():
  async with AsyncSessionLocal() as session:
    yield session