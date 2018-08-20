import os
import flake8.main.cli


def test_style():
    try:
        flake8.main.cli.main([os.path.join(os.path.dirname(__file__), '..')])
    except SystemExit, e:
        assert e.code is False


if __name__ == '__main__':
    flake8.main.cli.main()
