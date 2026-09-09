import setuptools
from pathlib import Path

with Path(__file__).with_name("README.md").open(encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sjvisualizer",
    version="0.0.15",
    author="Sjoerd Tilmans",
    author_email="info@sjdataviz.com",
    description="Package to animate your data",
    long_description=long_description,
    url="https://www.sjdataviz.com/",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(include=["sjvisualizer", "sjvisualizer.*"]),
    install_requires=["numpy>=1.23.2", "pandas>=2.0", "screeninfo>=0.7", "Pillow>=9.1", "openpyxl>=3.1", "opencv-python>=4.8"],
    package_data={
        'sjvisualizer': ['assets/*', "world.json", 'maps/*.json', 'maps/README.md'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
