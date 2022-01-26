import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CyberDB",
    version="0.1.0",
    author="Cyberbolt",
    author_email="dtconlyone@gmail.com",
    description="CyberDB is a main memory database of Python. You can use Dictionaries, Lists as data storage and it supports data persistence. Inter-process communication through Socket TCP has extremely high performance. In addition, you can customize your own data structure based on this module to support Gunicorn inter-process communication, distributed computing, model deployment of machine learning, etc.",
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