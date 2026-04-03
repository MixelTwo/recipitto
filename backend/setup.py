from setuptools import find_packages, setup

with open("requirements.txt", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="recipitto-backend",
    version="1.0.0",
    description="Backend for Recipitto recipe management application",
    author="Recipitto Team",
    author_email="team@recipitto.example.com",
    url="https://github.com/MixelTwo/recipitto",
    packages=find_packages(include=["blueprints", "data", "utils", "alembic"]),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "recipitto=main:main",
        ],
    },
)
