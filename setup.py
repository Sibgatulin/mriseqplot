from setuptools import setup, find_packages


def readme():
    with open("README.md") as f:
        f.read()


setup(
    name="mriseqplot",
    version="0.1",
    description="A module to generate MRI sequence diagrams with matplotlib",
    long_description=readme(),
    url="https://github.com/Sibgatulin/mriseqplot",
    author="Renat Sibgatulin",
    author_email="renat.sibgatulin@gmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=["numpy", "matplotlib"],
    extras_require={"dev": ["pre-commit"],},
)
