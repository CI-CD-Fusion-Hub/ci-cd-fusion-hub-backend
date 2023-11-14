from pydantic import Field
from pydantic_settings import BaseSettings

from typing import List, Dict, Any


class Settings(BaseSettings):
    app_name: str = Field(..., env="app_name")
    app_version: str = Field(..., env="app_version")
    app_secret_key: str = Field(..., env="app_secret_key")
    app_access_tokens: List[str] = Field(..., env="app_access_tokens")
    app_auth_header_name: str = Field(..., env="app_auth_header_name")
    app_root_path: str = Field(..., env="app_root_path")
    app_metrics_path: str = Field(..., env="app_metrics_path")
    app_metrics_excluded_paths: List[str] = Field(..., env="app_metrics_excluded_paths")
    app_host: str = Field(..., env="app_host")
    app_port: int = Field(..., env="app_port")
    app_session_lifetime: int = Field(..., env="app_session_lifetime")
    app_disable_auth: bool = Field(..., env="app_disable_auth")
    app_pipelines_sync_interval: int = Field(..., env="app_pipelines_sync_interval")
    app_env: str = Field(..., env="app_env")
    app_ssl_key: str = Field(..., env="app_ssl_key")
    app_ssl_cert: str = Field(..., env="app_ssl_cert")
    app_admin_email: str = Field(..., env="app_admin_email")
    app_admin_pass: str = Field(..., env="app_admin_pass")

    db_host: str = Field(..., env="db_host")
    db_user: str = Field(..., env="db_user")
    db_password: str = Field(..., env="db_password")
    db_name: str = Field(..., env="db_name")

    @property
    def app(self) -> Dict[str, str]:
        return {
            "name": self.app_name,
            "version": self.app_version,
            "secret_key": self.app_secret_key,
            "access_tokens": self.app_access_tokens,
            "auth_header_name": self.app_auth_header_name,
            "root_path": self.app_root_path,
            "metrics_path": self.app_metrics_path,
            "metrics_excluded_paths": self.app_metrics_excluded_paths,
            "host": self.app_host,
            "port": int(self.app_port),
            "session_lifetime": self.app_session_lifetime,
            "disable_auth": self.app_disable_auth,
            "pipelines_sync_interval": int(self.app_pipelines_sync_interval),
            "env": self.app_env,
            "ssl_cert": self.app_ssl_cert,
            "ssl_key": self.app_ssl_key,
            "admin_email": self.app_admin_email,
            "admin_pass": self.app_admin_pass
        }

    @property
    def database(self) -> Dict[str, str]:
        return {
            "host": self.db_host,
            "user": self.db_user,
            "password": self.db_password,
            "name": self.db_name
        }

    class Config:
        env_file = ".env"


