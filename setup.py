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
    "flask",
    "Flask[async]" "sqlalchemy",
    "SQLAlchemy-serializer",
    "pydantic",
    "inflection",
    "colorlog",
]

setuptools.setup(
    name="pyautogen",
    version=__version__,
    author="AutoGen",
    author_email="auto-gen@outlook.com",
    description="Enabling Next-Gen LLM Applications via Multi-Agent Conversation Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/microsoft/autogen",
    packages=setuptools.find_packages(include=["autogen*"], exclude=["test"]),
    # package_data={
    #     "autogen.default": ["*/*.json"],
    # },
    # include_package_data=True,
    install_requires=install_requires,
    extras_require={
        "test": [
            "chromadb",
            "lancedb",
            "coverage>=5.3",
            "datasets",
            "ipykernel",
            "nbconvert",
            "nbformat",
            "pre-commit",
            "pydantic==1.10.9",
            "pytest-asyncio",
            "pytest>=6.1.1",
            "sympy",
            "tiktoken",
            "wolframalpha",
            "qdrant_client[fastembed]",
        ],
        "blendsearch": ["flaml[blendsearch]"],
        "mathchat": ["sympy", "pydantic==1.10.9", "wolframalpha"],
        "retrievechat": [
            "chromadb",
            "tiktoken",
            "sentence_transformers",
            "pypdf",
            "ipython",
        ],
        "teachable": ["chromadb"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)
