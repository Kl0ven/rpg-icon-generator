import setuptools

requirements = [
    "drawSvg==1.7.0",
    "Shapely==1.7.1"
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rpg_icon_generator",
    version="0.3.0",
    author="Jean-loup Monnier",
    author_email="jloup.m@gmail.com",
    description="This package generate RPG items images procedurallye",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Kl0ven/rpg-icon-generator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=requirements
)
