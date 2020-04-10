from datetime import datetime

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="PyNyaaTa",
    version=datetime.now().strftime("%Y%m%d%H%M"),
    author="Xéfir Destiny",
    author_email="xefir@crystalyx.net",
    description="𝛑 😼 た, Xéfir's personal animes torrent search engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.crystalyx.net/Xefir/PyNyaaTa",
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.5",
)
