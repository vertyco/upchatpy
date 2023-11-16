import re
from pathlib import Path

from setuptools import find_packages, setup

version_raw = (Path(__file__).parent / "upgrade_chat" / "version.py").read_text()
version = re.compile(r'__version__\s=\s"(\d+\.\d+.\d)').search(version_raw).group(1)
keywords = [
    "Upgrade.Chat",
    "chat",
    "bot",
    "discord",
    "upgradechat",
    "donations",
    "subscriptions",
    "monetization",
    "payment",
    "api",
    "wrapper",
    "client",
]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="upchatpy",
    version=version,
    url="https://github.com/vertyco/upgrade-chat",
    author="vertyco",
    author_email="alex.c.goble@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    description="A type hinted async Python wrapper for the Upgrade.Chat API",
    packages=find_packages(),
    keywords=keywords,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Pydantic :: 1",
        "Framework :: Pydantic :: 2",
        "Framework :: Pytest",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Typing :: Typed",
        "Natural Language :: English",
    ],
    install_requires=["aiohttp", "pydantic"],
    python_requires=">=3.9",
)
