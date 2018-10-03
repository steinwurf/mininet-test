import os
import glob


def test_run(sshdirectory):

    wheels = glob.glob("dist/*.whl")

    if len(wheels) != 1:
        raise RuntimeError(
            "Unexpected number of wheels found {}".format(wheels))

    wheel_path = wheels[0]
    wheel_filename = os.path.basename(wheel_path)

    # Install the mininet_test pip package
    sshdirectory.put_file(wheel_path)
    sshdirectory.run('python -m pip install {}'.format(wheel_filename))

    # Run the mininet script
    sshdirectory.put_file('test/data/simple_ping.py')
    sshdirectory.run('sudo python simple_ping.py')
