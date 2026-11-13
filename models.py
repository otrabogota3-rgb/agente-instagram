from database import Base
from sqlalchemy import Column, Integer, String, Text


class MensajePendienteDB(Base):
  __tablename__ = "mensajes_pendientes"

  id = Column(Integer, primary_key=True, index=True)
  instagram_message_id = Column(
      String, unique=True, index=True, nullable=False
  )
  sender_id = Column(String, nullable=False)
  user_message = Column(Text, nullable=False)
  draft_response = Column(Text, nullable=False)
  post_caption = Column(Text, nullable=True)
  status = Column(
      String, default="pending"
  )  # Valores: pending, approved, rejected