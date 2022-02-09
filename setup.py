import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CyberDB",
    version="0.1.4",
    author="Cyberbolt",
    author_email="dtconlyone@gmail.com",
    description="CyberDB is a lightweight main memory database of Python. It can use Python's Dictionaries, Lists for data storage,build an efficient communication through Socket TCP, and provide data persistence. Developers can customize their own data structures based on this module, which is often used in Gunicorn inter-process communication, distributed computing, machine learning deployment and other fields.",
    long_description=long_description,
    long_description_content_type="text/markdown",    
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'APScheduler>=3.8.1',
        'joblib>=1.1.0'
    ]    
)