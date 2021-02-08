import re
import setuptools


with open("discord/ext/ipc/__init__.py") as stream:
    version = re.search(
        r"^__version__\s*=\s*[\'\"]([^\'\"]*)[\'\"]", stream.read(), re.MULTILINE
    ).group(1)

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Internet",
    "Topic :: Software Development",
    "Topic :: Software Development :: Libraries",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

project_urls = {
    "Issue Tracker": "https://github.com/Ext-Creators/discord-ext-ipc/issues",
    "Source": "https://github.com/Ext-Creators/discord-ext-ipc",
}

setuptools.setup(
    author="Ext-Creators",
    classifiers=classifiers,
    description="A discord.py extension for inter-process communication.",
    install_requires=["discord.py"],
    license="Apache Software License",
    name="discord-ext-ipc",
    packages=["discord.ext.ipc"],
    project_urls=project_urls,
    python_requires=">=3.5.3",
    url="https://github.com/Ext-Creators/discord-ext-ipc",
    version=version,
)
