from setuptools import setup

__author__ = "Alex Laird"
__copyright__ = "Copyright 2022, Alex Laird"
__version__ = "2.0.7"

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="hookee",
    version=__version__,
    packages=["hookee",
              "hookee.plugins"],
    python_requires=">=3.5",
    install_requires=[
        "pluginbase",
        "confuse",
        "flask>=1.1.0,<2.0.0",
        "MarkupSafe>=0.23,<2.1.0",
        "click",
        "pyngrok>=5.2.1",
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
        "Changelog": "https://github.com/alexdlaird/hookee/blob/main/CHANGELOG.md",
        "Sponsor": "https://www.paypal.me/alexdlaird"
    },
    keywords=["python", "webhook", "ngrok", "flask"],
    license="MIT",
    classifiers=[
        "Environment :: Console",
        "Environment :: Web Environment",
        "Development Status :: 5 - Production/Stable",
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
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
