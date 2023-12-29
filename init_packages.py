import subprocess

packages = [
    # http
    "aiohttp",
    "fastapi",
    "hypercorn",
    # mysql
    "sqlalchemy",
    "SQLAlchemy-serializer",
    "pymysql",
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
for package in packages:
    print(f"----------------------installing {package}----------------------")
    subprocess.run(f"pip install {package}", shell=True)
