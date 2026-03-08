from sqlalchemy import (
    String,
    DateTime,
    Integer,
    ForeignKey,
    LargeBinary,
    Table,
    Column,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from typing import List

from infrastructure.db.session import Base


# --- association tables ---
trusted_relations = Table(
    "trusted_relations",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("trusted_user_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    files: Mapped[List["FileModel"]] = relationship("FileModel", back_populates="owner")

    owned_shares: Mapped[List["FileShareModel"]] = relationship(
        "FileShareModel",
        foreign_keys="FileShareModel.owner_id",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    received_shares: Mapped[List["FileShareModel"]] = relationship(
        "FileShareModel",
        foreign_keys="FileShareModel.target_user_id",
        back_populates="target_user",
        cascade="all, delete-orphan",
    )


class FileModel(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    owner: Mapped["UserModel"] = relationship("UserModel", back_populates="files")

    versions: Mapped[List["FileVersionModel"]] = relationship(
        "FileVersionModel",
        back_populates="file",
        cascade="all, delete-orphan",
    )

    shares: Mapped[List["FileShareModel"]] = relationship(
        "FileShareModel",
        back_populates="file",
        cascade="all, delete-orphan",
    )


class FileVersionModel(Base):
    __tablename__ = "file_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    file_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("files.id"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    file: Mapped["FileModel"] = relationship("FileModel", back_populates="versions")


class FileShareModel(Base):
    __tablename__ = "file_shares"
    __table_args__ = (
        UniqueConstraint(
            "file_id", "target_user_id", name="uq_file_shares_file_target"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    file_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("files.id"), nullable=False
    )
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    target_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    file: Mapped["FileModel"] = relationship("FileModel", back_populates="shares")

    owner: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[owner_id],
        back_populates="owned_shares",
    )

    target_user: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[target_user_id],
        back_populates="received_shares",
    )


class MessageModel(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    receiver_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    content_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )
    is_read: Mapped[int] = mapped_column(Integer, default=0)


class FileKeyModel(Base):
    __tablename__ = "file_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    file_id: Mapped[int] = mapped_column(Integer, ForeignKey("files.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    encrypted_key: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
