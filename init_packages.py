import subprocess

packages = [
    # http
    "httpx",
    "fastapi",
    "pydantic",
    # mysql
    "sqlmodel",
    "psycopg2-binary",
    "alembic",
    # 基础包
    "colorlog",
    "pydantic",
    # 代码格式
    "pre-commit",
    "isort",
    "black",
    "mypy",
    "autoflake",
]

subprocess.run("pip install --upgrade pip", shell=True)
print(f'----------------------installing {"uvicorn[standard]"}----------------------')
subprocess.run('pip install "uvicorn[standard]" ', shell=True)
for package in packages:
    print(f"----------------------installing {package}----------------------")
    subprocess.run(f"pip install {package}", shell=True)
