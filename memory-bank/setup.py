from setuptools import setup, find_packages

setup(
    name="memory_bank",
    version="0.1.0",
    description="Sistema de armazenamento e recuperação de memórias para o SynapScale Backend",
    author="SynapScale Team",
    author_email="contato@synapscale.com",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.110.0",
        "sqlalchemy>=2.0.0",
        "pydantic>=2.0.0",
        "sentence-transformers>=2.2.2",
        "faiss-cpu>=1.7.4",
        "numpy>=1.24.0",
        "psycopg2-binary>=2.9.5",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
