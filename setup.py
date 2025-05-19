from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="yacraf_calculator",
    version="1.0.1",
    description="A calculator for a YACRAF instance",
    packages=find_packages("yacraf_calculator"),  # Automatically find all Python packages inside `src`
    install_requires=["numpy"],  # Dependencies
    long_description=(Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown"
)