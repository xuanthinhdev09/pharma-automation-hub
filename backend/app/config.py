"""Cấu hình ứng dụng — đọc từ biến môi trường, có giá trị mặc định cho demo."""
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pharma.db")
SECRET_KEY = os.getenv("SECRET_KEY", "demo-secret-key-change-me-in-production-0123456789abcdef")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")

# Các vai trò cố định theo đặc tả RBAC (v2 mục 2.1)
ROLES = ["EMPLOYEE", "MANAGER", "ACCOUNTANT", "DIRECTOR", "IT_ADMIN"]
