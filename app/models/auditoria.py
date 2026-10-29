
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AuditoriaChamado(Base):
    __tablename__ = "auditoria_chamados"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    chamado_id: Mapped[int] = mapped_column(
        ForeignKey("chamados.id"),
        nullable=False,
        index=True
    )

    acao: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    valor_anterior: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    valor_novo: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    origem: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    motivo: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
