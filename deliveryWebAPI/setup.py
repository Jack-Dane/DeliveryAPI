
from setuptools import setup, find_packages


setup(
    name="deliveryAPI",
    version="0.0.1",
    author="Jack Dane",
    author_email="jackdane@jackdane.co.uk",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "requests",
        "uvicorn"
    ]
)
