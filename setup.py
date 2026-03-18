from setuptools import setup, find_packages

setup(
    name='ics-calendar-skill',
    version='0.1.0',
    description='ICS Calendar Subscription Skill for OpenClaw',
    author='aki894',
    author_email='aki894@qq.com',
    packages=find_packages(),
    py_modules=['ics_calendar', 'cli'],
    entry_points={
        'console_scripts': [
            'ics=cli:cli',
        ],
    },
    install_requires=[
        'requests',
        'click',
        'icalendar',
        'rich',
    ],
    python_requires='>=3.9',
)
