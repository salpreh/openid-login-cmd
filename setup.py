from setuptools import setup, find_packages


version = '0.1.0'

# Load doc
# with open('README.md') as f:
#     readme = f.read()

# Dependecies
requires = [
    'certifi==2021.5.30',
    'charset-normalizer==2.0.4',
    'click==8.0.1',
    'clinlog==1.0.0',
    'colorama==0.4.4',
    'idna==3.2',
    'PyYAML==5.4.1',
    'requests==2.26.0',
    'urllib3==1.26.6'
]
setup(
    name='openid_login_cmd',
    version=version,
    description='CLI app to get tokens from openid server',
    # long_description=readme,
    long_description_content_type='text/markdown',
    author='salpreh',
    author_email='salva.perez46@gmail.com',
    url='https://github.com/salpreh/openid-login-cmd',
    install_requires=requires,
    license='MIT License',
    packages=find_packages(exclude=('test', 'assets', 'venv', 'doc')),
    entry_points={
        'console_scripts': [
            'oidc-login=openid_login_cmd.cli:main'
        ]
    }
)