cd d:\git\home-assistant
d:\python\scripts\flake8 --exclude www_static homeassistant/components/thermostat_control.py > d:\testflake8.txt
d:\python\scripts\flake8 --exclude www_static tests/components/test_thermostat_control.py > d:\testflake8_testfile.txt
d:\python\scripts\pylint homeassistant/components/thermostat_control.py > d:\testpylint.txt
d:\python\scripts\pylint tests/components/test_thermostat_control.py > d:\testpylint_testfile.txt
d:\python\scripts\py.test tests/components/test_thermostat_control.py --cov --cov-report term-missing > d:\testcoverage.txt
exit