from setuptools import setup

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.8"

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="hookee",
    version=__version__,
    packages=["hookee",
              "hookee.plugins"],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    install_requires=[
        "future",
        "pluginbase",
        "confuse",
        "python-dotenv",
        "flask",
        "pyngrok>=4.1.10",
    ],
    entry_points="""
        [console_scripts]
        hookee=hookee.cli:hookee
    """,
    include_package_data=True,
    description="Command line webhooks, on demand.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alex Laird",
    author_email="contact@alexlaird.com",
    url="https://github.com/alexdlaird/hookee",
    download_url="https://github.com/alexdlaird/hookee/archive/{}.tar.gz".format(__version__),
    project_urls={
        "Changelog": "https://github.com/alexdlaird/hookee/blob/master/CHANGELOG.md",
        "Sponsor": "https://www.paypal.me/alexdlaird"
    },
    keywords=["python", "webhook", "ngrok", "flask"],
    license="MIT",
    classifiers=[
        "Environment :: Console",
        "Environment :: Web Environment",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD :: FreeBSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
