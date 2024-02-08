from setuptools import setup, find_packages

__author__ = "Alex Laird"
__copyright__ = "Copyright 2024, Alex Laird"
__version__ = "2.2.3"

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="hookee",
    version=__version__,
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pluginbase",
        "confuse",
        "flask>=1.1.0,<2.0.0",
        "click",
        "pyngrok>=7.1.0",
        "defusedxml",
        # Remove these pinned deps once hookee is updated to work with Flask 2.x
        "MarkupSafe>=0.23,<2.1.0",
        "Jinja2<3.0,>=2.10.1",
        "itsdangerous==2.0.1",
        "werkzeug==2.0.3"
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
    project_urls={
        "Changelog": "https://github.com/alexdlaird/hookee/blob/main/CHANGELOG.md",
        "Documentation": "https://hookee.readthedocs.io",
        "Sponsor": "https://github.com/sponsors/alexdlaird",
        "Source Code": "https://github.com/alexdlaird/hookee"
    },
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Testing",
    ]
)
