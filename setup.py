from setuptools import setup, find_packages

setup(
    name="disscli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "diss=disscli.main:main",
        ]
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A CLI tool for sending Discord messages via webhooks.",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)