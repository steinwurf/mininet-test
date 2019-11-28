import os
import glob


def test_run(testdirectory):

    print(testdirectory.path())

    testdirectory.copy_file(filename="test/data/simple_ping.py")

    # Make sudo use our venv path (https://unix.stackexchange.com/a/83194)
    sudo_path = 'PATH={}'.format(os.getenv("PATH"))

    testdirectory.run('sudo {} python simple_ping.py'.format(sudo_path))
