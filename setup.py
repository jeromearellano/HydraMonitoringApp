from setuptools import setup, find_packages

# Read the README file for long description (optional, but recommended)
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="HydraMonitoringApp",  # The name of your project
    version="1.0.0",  # Version of your project
    author="jerome.a.arellano",  # Replace with your name
    author_email="jerome.a.arellano@accenture.com",  # Replace with your email
    description="A web app to monitor Hydra alarms and notify users when alarms turn red.",  # A short description of your project
    long_description=long_description,  # Load README for the long description
    long_description_content_type="text/markdown",  # The format of the long description (Markdown)
    url="https://github.com/jeromearellano/HydraMonitoringApp.git",  # Replace with actual repository URL
    packages=find_packages(),  # Automatically find and include project packages
    install_requires=[  # List of dependencies to be installed via pip
        "gradio",
        "requests",
        "urllib3",
        "pyttsx3"
    ],
    include_package_data=True,  # Include additional files from MANIFEST.in
    classifiers=[  # Classifiers help categorize your project on PyPI (optional)
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Replace with your license
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Minimum Python version required
)
