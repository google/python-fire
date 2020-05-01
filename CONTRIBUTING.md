# How to contribute

We'd love to accept your patches and contributions to this project. There are
just a few small guidelines you need to follow.

Once you have read them fork the project, make changes in your repository, then
open a pull request once your changes are ready.

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

All submissions, including submissions by project members, require review. We
use GitHub pull requests for this purpose. Consult [GitHub Help] for more
information on using pull requests.

[GitHub Help]: https://help.github.com/articles/about-pull-requests/

## Code style

In general, python-fire follows the guidelines in the
[Google Python Style Guide].
In addition, the project follows a convention of:
- An 80 character line length.
- An indentation of 2 spaces in most cases, and 4 for line continuation.
- PascalCase for function and method names.
- No type hints, as described in [PEP 484], to maintain compatibility with
Python versions < 3.5.
- Single quotes around strings, three double quotes around docstrings.

[Google Python Style Guide]: http://google.github.io/styleguide/pyguide.html
[PEP 484]: https://www.python.org/dev/peps/pep-0484

## Testing
python-fire uses Travis CI to run tests on pull requests, however you can run
tests yourself to reduce the chance of issues early on.
To do this, install pytest, mock, termcolor, and hypothesis, then run the tests
by opening a bash terminal in the root of the repository and run `pytest`.

## Linting
Some code style issues may be addressed as part of merging your pull request,
but if you would like to you can also lint your code beforehand. To do this,
open a bash terminal in the root of the repository and run `pylint fire`.
