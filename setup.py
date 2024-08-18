import re
from pathlib import Path

from setuptools import find_packages, setup

version_raw = (Path(__file__).parent / "upchatpy" / "version.py").read_text()
version = re.compile(r'__version__\s=\s"(\d+\.\d+.\d)').search(version_raw).group(1)

setup(
    name="upchatpy",
    version=version,
    url="https://github.com/vertyco/upchatpy",
    author="vertyco",
    author_email="alex.c.goble@gmail.com",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    description="A type hinted async Python wrapper for the Upgrade.Chat API",
    packages=find_packages(),
    keywords=[
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
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Pydantic :: 1",
        "Framework :: Pydantic :: 2",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    install_requires=["aiohttp", "pydantic"],
    python_requires=">=3.8",
)
