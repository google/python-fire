import os
import sys

# Use local Fire without installing.
sys.path.insert(0, os.path.dirname(__file__))

# Fire depends on termcolor for pretty output; to keep this repro standalone
# in minimal environments, provide a tiny stub.
try:
    import termcolor  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    import types

    termcolor = types.SimpleNamespace(colored=lambda s, *args, **kwargs: s)
    sys.modules["termcolor"] = termcolor

import fire


class Foo:
    def bar(self):
        return "bar"

    def do_stuff(self, arg1):
        return f"stuff {arg1}"


def main() -> None:
    # Enable completion output.
    # In Fire, `-- --completion` is passed after the Fire arguments separator.
    # We'll call Fire in a way that simulates CLI invocation.
    #
    # The bug report says that completion output includes a `--self` flag, which should
    # never be suggested to the user.
    argv = [
        "prog",
        "--",
        "--completion",
    ]

    # Fire uses sys.argv.
    old_argv = sys.argv
    try:
        sys.argv = argv
        # Fire writes completion script to stdout. Capture by redirecting.
        from io import StringIO
        import contextlib

        buf = StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                fire.Fire(Foo)
            except SystemExit as e:
                # Fire may exit after printing completion.
                if e.code not in (0, None):
                    raise

        out = buf.getvalue()
    finally:
        sys.argv = old_argv

    assert "--self" not in out, (
        "Completion output must not include the implicit 'self' parameter as a flag.\n"
        f"Output was:\n{out[:2000]}"
    )


if __name__ == "__main__":
    main()
