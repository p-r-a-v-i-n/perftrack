from setuptools import setup, find_packages

setup(
    name="perftrack",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "psutil",
    ],
    entry_points={
        "console_scripts": [
            "perftrack=perftrack.cli:main"
        ]
    }
)
