from setuptools import find_packages, setup

with open('README.md') as f:
        readme = f.read()

with open('LICENSE') as f:
        license = f.read()

setup(
    name='gfhttpva',
    version='0.2.0',
    url='https://github.com/sasaki77/gfhttpva',
    license=license,
    maintainer='Shinya Sasaki',
    maintainer_email='shinya.sasaki@kek.jp',
    description='grafana http / pvAccess API gateway',
    long_description=readme,
    packages=find_packages(exclude=('tests')),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-cors',
        'numpy',
        'pandas',
        'pytz',
        'pvapy',
    ],
)
