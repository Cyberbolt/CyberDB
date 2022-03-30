import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CyberDB",
    version="0.4.4",
    author="Cyberbolt",
    author_email="dtconlyone@gmail.com",
    description="CyberDB is a lightweight Python in-memory database. It is designed to use Python's built-in data structures Dictionaries, Lists for data storage, efficient communication through Socket TCP, and provide data persistence. This module is often used in Gunicorn inter-process communication, distributed computing and other fields.",
    long_description=long_description,
    long_description_content_type="text/markdown",    
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'APScheduler>=3.9.1',
        'obj-encrypt==0.3.0'
    ]    
)