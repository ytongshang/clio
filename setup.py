import os
from typing import Dict

import setuptools

here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r", encoding="UTF-8") as fh:
    long_description = fh.read()

# Get the code version
version: Dict[str, str] = {}
with open(os.path.join(here, "clio/version.py")) as fp:
    exec(fp.read(), version)
__version__ = version["__version__"]

install_requires = [
    # http
    "httpx",
    "fastapi",
    "uvicorn[standard]",
    # base
    "colorlog",
    "pydantic",
    "aiofiles",
    # db
    "prisma",
    "psycopg2-binary",
]

setuptools.setup(
    name="clio",
    version=__version__,
    author="rancune",
    author_email="ytongshang@gmail.com",
    description="A python web framework based on flask and prisma",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ytongshang/clio",
    packages=setuptools.find_packages(
        include=["clio*"], exclude=["example*", "app.py", "init_packages.py"]
    ),
    # package_data={
    #     "autogen.default": ["*/*.json"],
    # },
    # include_package_data=True,
    install_requires=install_requires,
    extras_require={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)
