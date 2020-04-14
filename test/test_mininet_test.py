import os
import glob


def test_run(vagrant):

    machine = vagrant.from_box(
        box="steinwurf/mininet", name="mininet-testmonitor", reset=True)

    with machine.ssh() as ssh:

        wheels = glob.glob("dist/*.whl")

        if len(wheels) != 1:
                raise RuntimeError(
                "Unexpected number of wheels found {}".format(wheels))

        wheel_path = wheels[0]
        wheel_filename = os.path.basename(wheel_path)

        # Install the mininet_test pip package
        ssh.put_file(wheel_path)
        ssh.run('python -m pip install {}'.format(wheel_filename))

        # Run the mininet script
        ssh.put_file('test/data/simple_ping.py')
        ssh.run('sudo python simple_ping.py')
