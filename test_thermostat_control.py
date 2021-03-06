"""
tests.components.proximity_zones
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests proximity_zones component.
"""
# import the dependencies
import unittest
from homeassistant.components import thermostat_control
import homeassistant.util.dt as dt_util
from tests.common import get_test_home_assistant, fire_time_changed


class TestThermostatControl(unittest.TestCase):
    """ Test the Thermostat_ccontrol component. """

    def setup_method(self, method):
        self.hass = get_test_home_assistant()

    def teardown_method(self, method):
        # function which removes things it's called between tests?
        self.hass.stop()

    # no config found
    def test_no_config(self):
        # get the state of the thermostat_control component
        state = self.hass.states.get('thermostat_control.test1')
        assert state is None

    # ============== Thermostat checking ==============
    # HA does not have a thermostat
    def test_no_thermostat(self):
        # mimic properly formatted config.yaml entry
        assert not thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1': {
                    'schedule': {
                        '07:00': 21.5,
                        '10:15': 24.5,
                        '15:45': 23.5,
                        '16:45': 20.5
                    },
                    'max_temp': 26,
                    'min_temp': 15,
                    'proximity': {
                        'distance_offset': 0.1,
                        'away_distance': 50,
                        'zone': 'home'
                    }
                }
            }
        })

        # component should exit gracefully
        # state = self.hass.states.get('thermostat_control.test1')
        # assert state is None

    # multiple thermostats exist - we need one from the config file
    def test_multiple_thermostats_no_thermostat_in_config(self):
        # setup a thermostat as this will be needed
        self.hass.states.set(
            'thermostat.test1', '23.5',
            {
                'away_mode': 'off',
                'current_operation': 'idle',
                'current_temperature': 19,
                'fan': 'off',
                'friendly_name': 'test1',
                'humidity': 38,
                'max_temp': 35,
                'min_temp': 16,
                'mode': 'heat',
                'target_humidity': 35,
                'target_temp_high': 16,
                'target_temp_low': 16,
                'temperature': 23.5,
                'unit_of_measurement': '°C'
            })
        self.hass.states.set(
            'thermostat.test2', '25.5',
            {
                'away_mode': 'off',
                'current_operation': 'idle',
                'current_temperature': 19,
                'fan': 'off',
                'friendly_name': 'test1',
                'humidity': 38,
                'max_temp': 35,
                'min_temp': 16,
                'mode': 'heat',
                'target_humidity': 35,
                'target_temp_high': 16,
                'target_temp_low': 16,
                'temperature': 23.5,
                'unit_of_measurement': '°C'
            })

        # no thermostat specified in config entry
        assert not thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1': {
                    'schedule': {
                        '07:00': 21.5,
                        '10:15': 24.5,
                        '15:45': 23.5,
                        '16:45': 20.5
                    },
                    'max_temp': 26,
                    'min_temp': 15,
                    'proximity': {
                        'distance_offset': 0.1,
                        'away_distance': 50,
                        'zone': 'home'
                    }
                }
            }
        })

    # check thermostat we are going to use exists
    def test_thermostat_exists(self):
        # setup a thermostat as component will fail without it
        self.hass.states.set(
            'thermostat.test1', '25.5',
            {
                'away_mode': 'off',
                'current_operation': 'idle',
                'current_temperature': 19,
                'fan': 'off',
                'friendly_name': 'test1',
                'humidity': 38,
                'max_temp': 35,
                'min_temp': 16,
                'mode': 'heat',
                'target_humidity': 35,
                'target_temp_high': 16,
                'target_temp_low': 16,
                'temperature': 23.5,
                'unit_of_measurement': '°C'
            })

        # thermostat does not exist
        assert not thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1': {
                    'schedule': {
                        '07:00': 21.5,
                        '10:15': 24.5,
                        '15:45': 23.5,
                        '16:45': 20.5
                    },
                    'max_temp': 26,
                    'min_temp': 15,
                    'thermostat': 'does_not_exist',
                    'proximity': {
                        'distance_offset': 0.1,
                        'away_distance': 50,
                        'zone': 'home'
                    }
                }
            }
        })

    # ============== Schedule checking ==============
    # Config does not include schedule
    def test_no_schedule_in_config(self):
        # setup a thermostat as component will fail without it
        self.hass.states.set(
            'thermostat.test1', '25.5',
            {
                'away_mode': 'off',
                'current_operation': 'idle',
                'current_temperature': 19,
                'fan': 'off',
                'friendly_name': 'test1',
                'humidity': 38,
                'max_temp': 35,
                'min_temp': 16,
                'mode': 'heat',
                'target_humidity': 35,
                'target_temp_high': 16,
                'target_temp_low': 16,
                'temperature': 23.5,
                'unit_of_measurement': '°C'
            })

        # no schedule specified in config entry
        assert not thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1': {
                    'max_temp': 26,
                    'min_temp': 15,
                    'proximity': {
                        'distance_offset': 0.1,
                        'away_distance': 50,
                        'zone': 'home'
                    }
                }
            }
        })

    # check schedule has properly formatted times
    def test_incorrect_time_in_schedule(self):
        # setup a thermostat as component will fail without it
        self.hass.states.set(
            'thermostat.test1', '25.5',
            {
                'away_mode': 'off',
                'current_operation': 'idle',
                'current_temperature': 19,
                'fan': 'off',
                'friendly_name': 'test1',
                'humidity': 38,
                'max_temp': 35,
                'min_temp': 16,
                'mode': 'heat',
                'target_humidity': 35,
                'target_temp_high': 16,
                'target_temp_low': 16,
                'temperature': 23.5,
                'unit_of_measurement': '°C'
            })

        # schedule includes error time
        assert not thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1': {
                    'schedule': {
                        '07:00': 21.5,
                        '10:15': 24.5,
                        '15:45': 23.5,
                        '26:45': 20.5
                    },
                    'max_temp': 26,
                    'min_temp': 15,
                    'proximity': {
                        'distance_offset': 0.1,
                        'away_distance': 50,
                        'zone': 'home'
                    }
                }
            }
        })

    # check schedule temperature does not exceed maximum temperature
    def test_schedule_temp_exceeds_max_temp(self):
        # setup a thermostat as component will fail without it
        self.hass.states.set(
            'thermostat.test1', '25.5',
            {
                'away_mode': 'off',
                'current_operation': 'idle',
                'current_temperature': 19,
                'fan': 'off',
                'friendly_name': 'test1',
                'humidity': 38,
                'max_temp': 35,
                'min_temp': 16,
                'mode': 'heat',
                'target_humidity': 35,
                'target_temp_high': 16,
                'target_temp_low': 16,
                'temperature': 23.5,
                'unit_of_measurement': '°C'
            })

        # schedule temp is above max temp
        assert not thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1': {
                    'schedule': {
                        '07:00': 31.5,
                        '10:15': 24.5,
                        '15:45': 23.5,
                        '16:45': 20.5
                    },
                    'max_temp': 26,
                    'min_temp': 15,
                    'proximity': {
                        'distance_offset': 0.1,
                        'away_distance': 50,
                        'zone': 'home'
                    }
                }
            }
        })

    # check schedule temperature does not exceed maximum temperature
    def test_schedule_temp_lower_than_min_temp(self):
        # setup a thermostat as component will fail without it
        self.hass.states.set(
            'thermostat.test1', '25.5',
            {
                'away_mode': 'off',
                'current_operation': 'idle',
                'current_temperature': 19,
                'fan': 'off',
                'friendly_name': 'test1',
                'humidity': 38,
                'max_temp': 35,
                'min_temp': 16,
                'mode': 'heat',
                'target_humidity': 35,
                'target_temp_high': 16,
                'target_temp_low': 16,
                'temperature': 23.5,
                'unit_of_measurement': '°C'
            })

        # schedule temp is less than minimum temp
        assert not thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1': {
                    'schedule': {
                        '07:00': 21.5,
                        '10:15': 24.5,
                        '15:45': 23.5,
                        '16:45': 10.5
                    },
                    'max_temp': 26,
                    'min_temp': 15,
                    'proximity': {
                        'distance_offset': 0.1,
                        'away_distance': 50,
                        'zone': 'home'
                    }
                }
            }
        })

    # ============== Proximity checking ==============
    # proximity control is expected but no proximity_zone exists
    def test_no_proximity_zone_no_config(self):
        # setup a thermostat as component will fail without it
        self.hass.states.set(
            'thermostat.test1', '25.5',
            {
                'away_mode': 'off',
                'current_operation': 'idle',
                'current_temperature': 19,
                'fan': 'off',
                'friendly_name': 'test1',
                'humidity': 38,
                'max_temp': 35,
                'min_temp': 16,
                'mode': 'heat',
                'target_humidity': 35,
                'target_temp_high': 16,
                'target_temp_low': 16,
                'temperature': 23.5,
                'unit_of_measurement': '°C'
            })

        # zone not specified
        assert not thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1': {
                    'schedule': {
                        '07:00': 21.5,
                        '10:15': 24.5,
                        '15:45': 23.5,
                        '16:45': 20.5
                    },
                    'max_temp': 26,
                    'min_temp': 15,
                    'proximity': {
                        'distance_offset': 0.1
                    }
                }
            }
        })

    # proximity control is expected but no proximity_zone exists
    def test_no_proximity_zone_zone_in_config(self):
        # setup a thermostat as component will fail without it
        self.hass.states.set(
            'thermostat.test1', '25.5',
            {
                'away_mode': 'off',
                'current_operation': 'idle',
                'current_temperature': 19,
                'fan': 'off',
                'friendly_name': 'test1',
                'humidity': 38,
                'max_temp': 35,
                'min_temp': 16,
                'mode': 'heat',
                'target_humidity': 35,
                'target_temp_high': 16,
                'target_temp_low': 16,
                'temperature': 23.5,
                'unit_of_measurement': '°C'
            })

        # zone not specified
        assert not thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1': {
                    'schedule': {
                        '07:00': 21.5,
                        '10:15': 24.5,
                        '15:45': 23.5,
                        '16:45': 20.5
                    },
                    'max_temp': 26,
                    'min_temp': 15,
                    'proximity': {
                        'distance_offset': 0.1,
                        'zone': 'test1'
                    }
                }
            }
        })

    # multiple thermostats exist - we need one from the config file
    # check thermostat we are going to use exists

    # multiple zones exist - config file does not include one
    def test_proximity_multiple_zones_no_zone_in_config(self):
        # setup a thermostat as component will fail without it
        self.hass.states.set(
            'thermostat.test1', '25.5',
            {
                'away_mode': 'off',
                'current_operation': 'idle',
                'current_temperature': 19,
                'fan': 'off',
                'friendly_name': 'test1',
                'humidity': 38,
                'max_temp': 35,
                'min_temp': 16,
                'mode': 'heat',
                'target_humidity': 35,
                'target_temp_high': 16,
                'target_temp_low': 16,
                'temperature': 23.5,
                'unit_of_measurement': '°C'
            })

        # setup proximity zone as these will be needed
        self.hass.states.set(
            'proximity.test1', '60',
            {
                'dir_of_travel': 'unknown',
                'friendly_name': 'test1',
                'nearest': 'Nick',
                'unit_of_measurement': 'km'
            })

        # setup proximity zone as these will be needed
        self.hass.states.set(
            'proximity.test2', '60',
            {
                'dir_of_travel': 'unknown',
                'friendly_name': 'test2',
                'nearest': 'Nick',
                'unit_of_measurement': 'km'
            })

        # no proximity zone in config entry
        assert not thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1': {
                    'schedule': {
                        '07:00': 21.5,
                        '10:15': 24.5,
                        '15:45': 23.5,
                        '16:45': 20.5
                    },
                    'max_temp': 26,
                    'min_temp': 15,
                    'proximity': {
                        'distance_offset': 0.1,
                        'away_distance': 50
                    }
                }
            }
        })

    # we need either distance offset or away distance in the config
    def test_proximity_distance_offset_nor_away_distance_in_config(self):
        # setup a thermostat as component will fail without it
        self.hass.states.set(
            'thermostat.test1', '25.5',
            {
                'away_mode': 'off',
                'current_operation': 'idle',
                'current_temperature': 19,
                'fan': 'off',
                'friendly_name': 'test1',
                'humidity': 38,
                'max_temp': 35,
                'min_temp': 16,
                'mode': 'heat',
                'target_humidity': 35,
                'target_temp_high': 16,
                'target_temp_low': 16,
                'temperature': 23.5,
                'unit_of_measurement': '°C'
            })

        # setup proximity zones as these will be needed
        self.hass.states.set(
            'proximity.test1', '60',
            {
                'dir_of_travel': 'unknown',
                'friendly_name': 'test1',
                'nearest': 'Nick',
                'unit_of_measurement': 'km'
            })

        # neither distance offset nor away distance in config entry
        assert not thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1': {
                    'schedule': {
                        '07:00': 21.5,
                        '10:15': 24.5,
                        '15:45': 23.5,
                        '16:45': 20.5
                    },
                    'max_temp': 26,
                    'min_temp': 15,
                    'proximity': {
                        'zone': 'home'
                    }
                }
            }
        })

    # check proximity zone we are going to use exists
    def test_proximity_zone_exists(self):
        # setup a thermostat as component will fail without it
        self.hass.states.set(
            'thermostat.test1', '25.5',
            {
                'away_mode': 'off',
                'current_operation': 'idle',
                'current_temperature': 19,
                'fan': 'off',
                'friendly_name': 'test1',
                'humidity': 38,
                'max_temp': 35,
                'min_temp': 16,
                'mode': 'heat',
                'target_humidity': 35,
                'target_temp_high': 16,
                'target_temp_low': 16,
                'temperature': 23.5,
                'unit_of_measurement': '°C'
            })

        # setup a proximity zone as this will be needed
        self.hass.states.set(
            'proximity.test1', '60',
            {
                'dir_of_travel': 'unknown',
                'friendly_name': 'test1',
                'nearest': 'Nick',
                'unit_of_measurement': 'km'
            })

        # proximity zone does not exist
        assert not thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1': {
                    'schedule': {
                        '07:00': 21.5,
                        '10:15': 24.5,
                        '15:45': 23.5,
                        '16:45': 20.5
                    },
                    'max_temp': 26,
                    'min_temp': 15,
                    'proximity': {
                        'distance_offset': 0.1,
                        'away_distance': 50,
                        'zone': 'does_not_exist'
                    }
                }
            }
        })

    # ==============================================
    def test_thermostat_control_success(self):
        # setup a thermostat
        self.hass.states.set(
            'thermostat.test1', '25.5',
            {
                'away_mode': 'off',
                'current_operation': 'idle',
                'current_temperature': 19,
                'fan': 'off',
                'friendly_name': 'test1',
                'humidity': 38,
                'max_temp': 35,
                'min_temp': 16,
                'mode': 'heat',
                'target_humidity': 35,
                'target_temp_high': 16,
                'target_temp_low': 16,
                'temperature': 23.5,
                'unit_of_measurement': '°C'
            })

        # setup a proximity zone
        self.hass.states.set(
            'proximity.test1', '0',
            {
                'dir_of_travel': 'unknown',
                'friendly_name': 'test1',
                'nearest': 'Nick',
                'unit_of_measurement': 'km'
            })

        # mimic properly formatted config.yaml entry
        assert thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1': {
                    'schedule': {
                        '07:00': 21.5,
                        '10:15': 24.5,
                        '15:45': 23.5,
                        '16:45': 20.5
                    },
                    'max_temp': 26,
                    'min_temp': 15,
                    'proximity': {
                        'distance_offset': 0.1,
                        'away_distance': 50,
                        'zone': 'test1'
                    }
                }
            }
        })

        # get the state of the created entity
        state = self.hass.states.get('thermostat_control.test1')

        # test the expected values of the entity
        self.assertEqual('20.5', state.state)
        self.assertEqual(20.5, state.attributes.get('set_temp'))
        self.assertEqual('16:45', state.attributes.get('active_from'))
        self.assertEqual('07:00', state.attributes.get('next_change'))
        self.assertEqual(20.5, state.attributes.get('schedule_temp'))
        self.assertEqual(0, state.attributes.get('offset_temp'))
        self.assertEqual('off', state.attributes.get('manual_override'))
        self.assertEqual('not set',
                         state.attributes.get('manual_override_end'))
        self.assertEqual('°C', state.attributes.get('unit_of_measurement'))
        self.assertEqual('test1', state.attributes.get('friendly_name'))

    def test_thermostat_control_schedule_change(self):
        # setup a thermostat
        self.hass.states.set(
            'thermostat.test1', '25.5',
            {
                'away_mode': 'off',
                'current_operation': 'idle',
                'current_temperature': 19,
                'fan': 'off',
                'friendly_name': 'test1',
                'humidity': 38,
                'max_temp': 35,
                'min_temp': 16,
                'mode': 'heat',
                'target_humidity': 35,
                'target_temp_high': 16,
                'target_temp_low': 16,
                'temperature': 23.5,
                'unit_of_measurement': '°C'
            })

        # setup a proximity zone
        self.hass.states.set(
            'proximity.test1', '0',
            {
                'dir_of_travel': 'unknown',
                'friendly_name': 'test1',
                'nearest': 'Nick',
                'unit_of_measurement': 'km'
            })

        # mimic properly formatted config.yaml entry
        assert thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1': {
                    'schedule': {
                        '07:00': 21.5,
                        '10:15': 24.5,
                        '15:45': 23.5,
                        '16:45': 20.5
                    },
                    'max_temp': 26,
                    'min_temp': 15,
                    'proximity': {
                        'distance_offset': 0.1,
                        'away_distance': 50,
                        'zone': 'test1'
                    }
                }
            }
        })

        # ========= Time Change 1 =========
        # set the time of HA
        fire_time_changed(self.hass,
                          dt_util.utcnow().replace(hour=7, minute=0, second=0))
        self.hass.pool.block_till_done()

        # get the state of the created entity
        state = self.hass.states.get('thermostat_control.test1')

        # test the expected values of the thermostat_control entity
        self.assertEqual('21.5', state.state)
        self.assertEqual(21.5, state.attributes.get('set_temp'))
        self.assertEqual('07:00', state.attributes.get('active_from'))
        self.assertEqual('10:15', state.attributes.get('next_change'))
        self.assertEqual(21.5, state.attributes.get('schedule_temp'))
        self.assertEqual(0, state.attributes.get('offset_temp'))
        self.assertEqual('off', state.attributes.get('manual_override'))
        self.assertEqual('not set',
                         state.attributes.get('manual_override_end'))

        # test the value of the thermostat
        state = self.hass.states.get('thermostat.test1')

        # test the expected values of the thermostat entity
        self.assertEqual('21.5', state.state)

        # ========= Time Change 2 =========
        # set the time of HA
        fire_time_changed(self.hass,
                          dt_util.utcnow().replace(hour=10, minute=15,
                          second=0))
        self.hass.pool.block_till_done()

        # get the state of the created entity
        state = self.hass.states.get('thermostat_control.test1')

        # test the expected values of the thermostat_control entity
        self.assertEqual('24.5', state.state)
        self.assertEqual(24.5, state.attributes.get('set_temp'))
        self.assertEqual('10:15', state.attributes.get('active_from'))
        self.assertEqual('15:45', state.attributes.get('next_change'))
        self.assertEqual(24.5, state.attributes.get('schedule_temp'))

        # test the value of the thermostat
        state = self.hass.states.get('thermostat.test1')

        # test the expected values of the thermostat entity
        self.assertEqual('24.5', state.state)

        # ========= Time Change 3 =========
        # set the time of HA
        fire_time_changed(self.hass,
                          dt_util.utcnow().replace(hour=15, minute=45,
                          second=0))
        self.hass.pool.block_till_done()

        # get the state of the created entity
        state = self.hass.states.get('thermostat_control.test1')

        # test the expected values of the thermostat_control entity
        self.assertEqual('23.5', state.state)
        self.assertEqual(23.5, state.attributes.get('set_temp'))
        self.assertEqual('15:45', state.attributes.get('active_from'))
        self.assertEqual('16:45', state.attributes.get('next_change'))
        self.assertEqual(23.5, state.attributes.get('schedule_temp'))

        # test the value of the thermostat
        state = self.hass.states.get('thermostat.test1')

        # test the expected values of the thermostat entity
        self.assertEqual('23.5', state.state)

        # ========= Time Change 4 =========
        # set the time of HA
        fire_time_changed(self.hass,
                          dt_util.utcnow().replace(hour=16, minute=45,
                          second=0))
        self.hass.pool.block_till_done()

        # get the state of the created entity
        state = self.hass.states.get('thermostat_control.test1')

        # test the expected values of the thermostat_control entity
        self.assertEqual('20.5', state.state)
        self.assertEqual(20.5, state.attributes.get('set_temp'))
        self.assertEqual('16:45', state.attributes.get('active_from'))
        self.assertEqual('07:00', state.attributes.get('next_change'))
        self.assertEqual(20.5, state.attributes.get('schedule_temp'))

        # test the value of the thermostat
        state = self.hass.states.get('thermostat.test1')

        # test the expected values of the thermostat entity
        self.assertEqual('20.5', state.state)