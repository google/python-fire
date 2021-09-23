# How to contribute

We'd love to accept your patches and contributions to this project. There are
just a few small guidelines you need to follow.

First, read these guidelines.
Before you begin making changes, state your intent to do so in an Issue.
Then, fork the project. Make changes in your copy of the repository.
Then open a pull request once your changes are ready.
If this is your first contribution, sign the Contributor License Agreement.
A discussion about your change will follow, and if accepted your contribution
will be incorporated into the Python Fire codebase.

## Contributor License Agreement

Contributions to this project must be accompanied by a Contributor License
Agreement. You (or your employer) retain the copyright to your contribution,
this simply gives us permission to use and redistribute your contributions as
part of the project. Head over to <https://cla.developers.google.com/> to see
your current agreements on file or to sign a new one.

You generally only need to submit a CLA once, so if you've already submitted one
(even if it was for a different project), you probably don't need to do it
again.

## Code reviews

All submissions, including submissions by project members, require review.
For changes introduced by non-Googlers, we use GitHub pull requests for this
purpose. Consult [GitHub Help] for more information on using pull requests.

[GitHub Help]: https://help.github.com/articles/about-pull-requests/

## Code style

In general, Python Fire follows the guidelines in the
[Google Python Style Guide].

In addition, the project follows a convention of:
- Maximum line length: 80 characters
- Indentation: 2 spaces (4 for line continuation)
- PascalCase for function and method names.
- No type hints, as described in [PEP 484], to maintain compatibility with
Python versions < 3.5.
- Single quotes around strings, three double quotes around docstrings.

[Google Python Style Guide]: http://google.github.io/styleguide/pyguide.html
[PEP 484]: https://www.python.org/dev/peps/pep-0484

## Testing

Python Fire uses [Github Actions](https://github.com/google/python-fire/actions) to run tests on each pull request. You can run
these tests yourself as well. To do this, first install the test dependencies
listed in setup.py (e.g. pytest, mock, termcolor, and hypothesis).
Then run the tests by running `pytest` in the root directory of the repository.

## Linting

Please run lint on your pull requests to make accepting the requests easier.
To do this, run `pylint fire` in the root directory of the repository.
Note that even if lint is passing, additional style changes to your submission
may be made during merging.
