from setuptools import setup, find_packages

setup(
    name='gpt_scraper',
    version='0.1.0',
    description='GPT-Scraper is an autonomous, LLM-based agent that generates code to extract structured information from web pages.',
    author='Sergei Belousov aka BeS',
    author_email='sergei.o.belousov@gmail.com',
    url='https://github.com/bes-dev/gpt-scraper.git',
    packages=find_packages(exclude=[".git", ".gitignore"]),
    install_requires=[
        'openai',
        'pydantic',
        'selenium',
    ],
    entry_points={
        'console_scripts': [
            'gpt-scraper = gpt_scraper.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
