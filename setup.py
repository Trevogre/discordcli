from setuptools import setup, find_packages

setup(
    name="disscli",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
    ],
    tests_require=[
        "pytest>=6.0.0",
    ],
    entry_points={
        'console_scripts': [
            'diss=disscli.main:main',
        ],
    },
    author="Trevor Green",
    author_email="your.email@example.com",
    description="A Discord CLI tool for sending messages via webhooks",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)