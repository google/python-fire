# Installation

Install this library in an [virtualenv](https://virtualenv.pypa.io/en/latest/) using pip. virtualenv is a tool to create isolated Python environments. The basic problem it addresses is one of dependencies and versions, and indirectly permissions.

With virtualenv, it's possible to install this library without needing system install permissions, and without clashing with the installed system dependencies.

### Mac/Linux

```

pip install virtualenv

virtualenv <your-env>

source <your-env>/bin/activate

<your-env>/bin/pip install google-api-python-client

```

### Windows

```

pip install virtualenv

virtualenv <your-env>

<your-env>\Scripts\activate

<your-env>\Scripts\pip.exe install google-api-python-client

```


To install Python Fire with pip, run: `pip install fire`

To install Python Fire with conda, run: `conda install fire -c conda-forge`

To install Python Fire from source, first clone the repository and then run:
`python setup.py install`
