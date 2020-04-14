Introduction
============

When using mininet for automated testing of network applications we would like
to monitor the status of those applications.

To acheive this we use a customized mininet Host which records all processes
launced with a test monitor object. The test monitor object then monitors those
processes and will signal when the last non daemon process exits.

Server / client example
-----------------------

In a server client scenario we would like the server to run as long as needed
and consider the test over once the client exits.

With the mininet test monitor we can specify the server as a daemon process
this means that we expect it to run indefinitely and the client is a normal
process that is expected to exit at some point.

In code this looks very similar to using the standard mininet `popen` calls::

    # Will open the two processes on both hosts and read the output

    server_app = server.popen('./server', daemon=True)
    client_app = client.popen('./client {}'.format(server.IP()))

If the server exits before the client we will be notified and if either
exits with an error we will also get an exception.