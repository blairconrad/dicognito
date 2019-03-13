import os
import flake8.main.cli


def test_style():
    try:
        base_dir = os.path.join(os.path.dirname(__file__), '..')
        config_file = os.path.join(base_dir, ".flake8")
        flake8.main.cli.main([base_dir, "--config=" + config_file])
    except SystemExit, e:
        assert e.code is False


if __name__ == "__main__":
    flake8.main.cli.main()
