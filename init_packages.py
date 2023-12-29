import subprocess

packages = [
    # http
    "aiohttp",
    "sqlalchemy",
    "SQLAlchemy-serializer",
    "fastapi",
    "hypercorn",
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

skynet_log_version = "0.0.2"

subprocess.run("pip install --upgrade pip", shell=True)
for package in packages:
    print(f"installing {package}")
    subprocess.run(f"pip install {package}", shell=True)
