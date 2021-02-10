from setuptools import find_packages, setup

setup(
    name="bohr",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points="""
        [console_scripts]
        bohr=bohr.framework.cli:bohr
    """,
)
