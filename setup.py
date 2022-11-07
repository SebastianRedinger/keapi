from setuptools import setup, find_packages
from pathlib import Path

VERSION = "1.0.0.beta2"

install_requires = ['websocket-client==1.4.1']
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="keapi-robotics",
    version=VERSION,
    description="A API to communicate with a KEBA PLC via WebSockets",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Sebastian Redinger",
    author_email="sebastian.redinger@fsbondtec.at",
    license="MIT",
    python_requires='>=3.8',
    extras_require={
        "docs": ["Sphinx >= 5.2", "sphinx_rtd_theme >= 1.0"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Scientific/Engineering",
        "Intended Audience :: Developers",
    ],
    keywords='keapi',
    install_requires=install_requires,
    packages=find_packages(),
)
