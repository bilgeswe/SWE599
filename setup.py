from setuptools import setup, find_packages

setup(
    name="sumo-to-opendrive",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "lxml>=4.9.0",
    ],
    extras_require={
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to convert SUMO networks to OpenDRIVE format",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
) 