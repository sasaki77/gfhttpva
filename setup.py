from setuptools import find_packages, setup

with open('README.md') as f:
        readme = f.read()

with open('LICENSE') as f:
        license = f.read()

setup(
    name='gfhttpva',
    version='0.0.1',
    url='https://github.com/sasaki77/gfhttpva',
    license=license,
    maintainer='Shinya Sasaki',
    maintainer_email='shinya.sasaki@kek.jp',
    description='grafana http / pvAccess API gateway',
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'numpy',
        'pytz',
    ],
)
