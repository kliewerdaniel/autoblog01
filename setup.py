"""
Setup script for the Agentic Blog Post Generation System.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read requirements
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read README
readme_path = Path('README.md')
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ""

setup(
    name="agentic-blog-generator",
    version="0.1.0",
    description="Agentic workflow system for generating high-quality, SEO-optimized blog posts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Daniel Kliewer",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'agent=agent.cli:cli',
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    keywords="ai, llm, blog, generation, seo, ollama, rag",
)
