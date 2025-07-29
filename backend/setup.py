from setuptools import setup, find_packages

setup(
    name="seatsync-backend",
    version="1.0.0",
    description="AI-Powered Sports Ticket Portfolio Management Platform",
    author="SeatSync Team",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "sqlalchemy>=2.0.23",
        "psycopg2-binary>=2.9.9",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-dotenv>=1.0.0",
        "pandas>=2.1.3",
        "numpy>=1.25.2",
        "scikit-learn>=1.3.2",
        "xgboost>=2.0.2",
        "httpx>=0.25.2",
        "redis>=5.0.1",
        "pydantic>=2.5.0",
    ],
    python_requires=">=3.11",
) 