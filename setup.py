from setuptools import setup

requires = [
    "flake8 > 3.0.0",
]

setup(
    name="flake8-stricter-codestyle",
    license="MIT",
    version="0.0.1",
    description="flake8 extension that makes some optional PEP8 guidance mandatory",
    author="Kai Willaden",
    author_email="kai.willadsen@gmail.com",
    py_modules=["flake8_stricter_codestyle"],
    url="https://github.com/kaiw/flake8-stricter-codestyle",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=requires,
    entry_points={
        "flake8.extension": [
            "flake8_stricter_codestyle.backslash_continuation = flake8_stricter_codestyle:backslash_continuation",
            "flake8_stricter_codestyle.continued_indentation = flake8_stricter_codestyle:continued_indentation",
        ],
    },
    classifiers=[
        "Framework :: Flake8",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
)
