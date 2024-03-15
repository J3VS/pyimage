from setuptools import find_packages, setup

setup(
    name="pyimage",
    version="1.0.0",
    description="python image scraping tools",
    license="MIT",
    author="jonathanviccary",
    url="https://github.com/J3VS/pyimage",
    packages=find_packages(),
    keywords="pyimage",
    install_requires=[
        "pillow==9.4.0",
        "pytesseract==0.3.10",
        "opencv-python==4.8.1.78",
        "tesseract==0.1.3"
    ],
    zip_safe=True,
)
