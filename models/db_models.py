from sqlalchemy.orm import relationship

from utils.database import Base

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    created_ts = Column(TIMESTAMP, default=func.now())
    status = Column(String)
    access_level = Column(String)

    roles = relationship("AccessRoleMembers", back_populates="user")

    def as_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'created_ts': self.created_ts.isoformat() if self.created_ts else None,
            'status': self.status,
            'access_level': self.access_level
        }


class AccessRoles(Base):
    __tablename__ = "access_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    description = Column(String)
    created_ts = Column(TIMESTAMP, default=func.now())

    users = relationship("AccessRoleMembers", back_populates="role", cascade="all, delete")
    pipelines = relationship("AccessRolePipelines", back_populates="access_role", cascade="all, delete")

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_ts': self.created_ts.isoformat() if self.created_ts else None
        }


class AccessRoleMembers(Base):
    __tablename__ = "access_role_members"

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(Integer, ForeignKey('access_roles.id'), primary_key=True)
    created_ts = Column(TIMESTAMP, default=func.now())

    user = relationship("Users", back_populates="roles")
    role = relationship("AccessRoles", back_populates="users")

    def as_dict(self):
        return {
            'user_id': self.user_id,
            'role_id': self.role_id,
            'created_ts': self.created_ts.isoformat() if self.created_ts else None
        }


class Pipelines(Base):
    __tablename__ = "pipelines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    application_id = Column(Integer, ForeignKey('applications.id'))
    project_id = Column(String)
    created_ts = Column(TIMESTAMP, default=func.now())

    application = relationship("Applications", back_populates="pipelines", lazy="joined")
    access_roles = relationship("AccessRolePipelines", back_populates="pipeline")

    __table_args__ = (UniqueConstraint('name', 'application_id', name='unique_name_application_id'),)

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'application': self.application.as_dict() if self.application else None,
            'project_id': self.project_id,
            'created_ts': self.created_ts.isoformat() if self.created_ts else None
        }


class AccessRolePipelines(Base):
    __tablename__ = 'access_role_pipelines'

    pipeline_id = Column(Integer, ForeignKey('pipelines.id'), primary_key=True)
    access_role_id = Column(Integer, ForeignKey('access_roles.id', ondelete='CASCADE'), primary_key=True)
    created_ts = Column(TIMESTAMP, default=func.now())

    pipeline = relationship("Pipelines", back_populates="access_roles")
    access_role = relationship("AccessRoles", back_populates="pipelines")

    def as_dict(self):
        return {
            'pipeline_id': self.pipeline_id,
            'access_role_id': self.access_role_id,
            'created_ts': self.created_ts.isoformat() if self.created_ts else None
        }


class Applications(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    auth_user = Column(String)
    auth_pass = Column(String)
    base_url = Column(String)
    type = Column(String)
    regex_pattern = Column(String)
    status = Column(String)
    created_ts = Column(TIMESTAMP, default=func.now())

    pipelines = relationship("Pipelines", back_populates="application")

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'auth_user': self.auth_user,
            'auth_pass': self.auth_pass,
            'base_url': self.base_url,
            'type': self.type,
            'regex_pattern': self.regex_pattern,
            'status': self.status,
            'created_ts': self.created_ts.isoformat() if self.created_ts else None
        }


