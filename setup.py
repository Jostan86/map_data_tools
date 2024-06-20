from setuptools import setup, find_packages

setup(
    name="map_data_tools",
    version="0.1.0",
    description="Some tools for working with the orchard map data for the particle filter localization system and related projects.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Jostan Brown",
    author_email="your.email@example.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # List your project dependencies here
    ],
    python_requires='>=3.6',
)