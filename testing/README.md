# Unit tests

**WARNING: Risk of flashing lights as GUI windows are rapidly created and destroyed**

Run the tests by running:

```
python3 test.py
```

The unit tests validate the basic functionality of the tool.

# Test environment

A set of testing `Views` have been set up to allow for quick and easy testing of different aspects of the tool. To start the test environment, run:

```
python3 main.py test
```

The test environment uses the `Views` found in the `testing/saved_views` directory and activates the scripts found in `testing/scripts` on top of the those found in `scripts`.

