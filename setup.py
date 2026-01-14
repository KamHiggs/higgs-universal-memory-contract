"""
Higgs Universal Memory Contract - Setup
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="higgs-universal-memory-contract",
    version="0.9.0",
    author="Kamden & Solara Higgs",
    description="Universal Memory Contract (UMC) - Session-scoped episodic memory protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KamHiggs/higgs-universal-memory-contract",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "pydantic>=2.5.3",
        "psycopg2-binary>=2.9.9",
        "sqlalchemy>=2.0.25",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-asyncio>=0.23.3",
            "httpx>=0.26.0",
            "black>=23.12.1",
            "ruff>=0.1.11",
        ],
    },
    entry_points={
        "console_scripts": [
            "umc-server=middleware.umc_memory_server:main",
        ],
    },
)
