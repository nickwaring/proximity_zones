"""
tests.components.proximity_zones
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests proximity_zones component.
"""

import homeassistant.core as ha
import os
from homeassistant.components import thermostat_control
#from homeassistant.components import zone
#import homeassistant.components.device_tracker as device_tracker
import homeassistant.util.dt as dt_util
#from datetime import datetime, timedelta
from tests.common import get_test_home_assistant
from datetime import timedelta
import time

class TestThermostatControl:
    """ Test the Thermostat_ccontrol component. """

    def setup_method(self, method):
        self.hass = get_test_home_assistant()

        self.hass.states.set(
            'proximity.test1', '60',
            {
                'dir_of_travel': 'unknown',
                'friendly_name': 'test1',
                'nearest': 'Nick',
                'unit_of_measurement': 'km'
            },
            'thermostat.test1', '23.5',
-            {
-                'away_mode': 'off',
-                'current_operation': 'idle',
-                'current_temperature': 19,
-                'fan': 'off',
-                'friendly_name': 'test1',
-                'humidity': 38,
-                'max_temp': 35,
-                'min_temp': 16,
-                'mode': 'heat',
-                'target_humidity': 35,
-                'target_temp_high': 16,
-                'target_temp_low': 16,
-                'temperature': 23.5,
-                'unit_of_measurement': '°C'
             })
                
    def teardown_method(self, method):
        """ Stop down stuff we started. """
        self.hass.stop()
        
    def test_thermostat_control(self):
        assert thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1':{
                    'proximity_zone': 'test1',
                    'thermostat': 'test1',
                    'schedule': {
                        '07:00': 21.5,
                        '10:15': 34.5,
                        '15:45': 33.5,
                        '16:45': 40.5
                    },
                    'max_temp': 26,
                    'dist_offset': 0.1,
                    'away_distance': 50
                }
                'test2':{
                    'proximity_zone': 'test2',
                    'thermostat': 'test2',
                    'schedule': {
                        '09:00': 21.5,
                        '12:15': 14.5,
                        '17:45': 23.5,
                        '18:45': 20.5
                    },
                    'max_temp': 24,
                    'dist_offset': 0.5,
                    'away_distance': 30
                }                
            }
        })

        state = self.hass.states.get('thermostat_control.test1')
        assert state.state != 'not set'
        assert state.attributes.get('next_change') != 'not set'
        assert state.attributes.get('away_mode') != 'not set'       
        assert state.attributes.get('manual_override_end') != 'not set'
        assert state.attributes.get('offset_temp') != 'not set'
        assert state.attributes.get('unit_of_measurement') != 'not set'
        assert state.attributes.get('active_from') != 'not set'
        assert state.attributes.get('manual_override') != 'not set'
        assert state.attributes.get('schedule_temp') != 'not set'
        assert state.attributes.get('friendly_name') != 'not set'
        assert state.attributes.get('set_temp') != 'not set'

    def test_no_config(self):
        assert not thermostat_control.setup(self.hass, {
        })
        
    def test_no_thermostat_in_config(self):
        assert not thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1':{
                    'proximity_zone': 'test1',
                    'schedule': {
                        '07:00': 21.5,
                        '10:15': 34.5,
                        '15:45': 33.5,
                        '16:45': 40.5
                    },
                    'max_temp': 26,
                    'dist_offset': 0.1,
                    'away_distance': 50
                }                
            }
        })
        
    def test_no_schedule_in_config(self):
        assert not thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1':{
                    'proximity_zone': 'test1',
                    'thermostat': 'test1',
                    'max_temp': 26,
                    'dist_offset': 0.1,
                    'away_distance': 50
                }               
            }
        })
        
    def test_no_proximity_zone_in_config(self):
        assert thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1':{
                    'thermostat': 'test1',
                    'schedule': {
                        '07:00': 21.5,
                        '10:15': 34.5,
                        '15:45': 33.5,
                        '16:45': 40.5
                    },
                    'max_temp': 26,
                    'dist_offset': 0.1,
                    'away_distance': 50
                }              
            }
        })
        
    def test_no_max_temp_in_config(self):
        assert thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1':{
                    'proximity_zone': 'test1',
                    'thermostat': 'test1',
                    'schedule': {
                        '07:00': 21.5,
                        '10:15': 34.5,
                        '15:45': 33.5,
                        '16:45': 40.5
                    },
                    'dist_offset': 0.1,
                    'away_distance': 50
                }               
            }
        })
     
    def test_no_dist_offset_in_config(self):
        assert thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1':{
                    'proximity_zone': 'test1',
                    'thermostat': 'test1',
                    'schedule': {
                        '07:00': 21.5,
                        '10:15': 34.5,
                        '15:45': 33.5,
                        '16:45': 40.5
                    },
                    'max_temp': 26,
                    'away_distance': 50
                }                
            }
        })
    
    def test_no_dist_offset_in_config(self):
        assert thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1':{
                    'proximity_zone': 'test1',
                    'thermostat': 'test1',
                    'schedule': {
                        '07:00': 21.5,
                        '10:15': 34.5,
                        '15:45': 33.5,
                        '16:45': 40.5
                    },
                    'max_temp': 26,
                    'away_distance': 50
                }
            }
        })

    def test_no_away_distance_in_config(self):
        assert thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1':{
                    'proximity_zone': 'test1',
                    'thermostat': 'test1',
                    'schedule': {
                        '07:00': 21.5,
                        '10:15': 34.5,
                        '15:45': 33.5,
                        '16:45': 40.5
                    },
                    'max_temp': 26,
                    'dist_offset': 0.1,
                }
            }
        })        
#===========================================================        
    def test_device_tracker_test1_in_zone(self):
        assert proximity_zones.setup(self.hass, {
            'proximity_zones': {
                'home': {
                    'zone': 'home',
                    'ignored_zones': {
                        'work'
                    },
                    'devices': {
                        'test1'
                    },
                    'tolerance': 1
                },
                'work': {
                    'zone': 'work',
                    'ignored_zones': {
                        'home'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                }
            }
        })
        
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1',
                'latitude': 50,
                'longitude': 50
            })
        self.hass.pool.block_till_done()
        
        state = self.hass.states.get('device_tracker.test1')
        assert state.state == 'not_home'
        
        self.hass.states.set(
            'device_tracker.test1', 'home',
            {
                'friendly_name': 'test1',
                'latitude': 2.1,
                'longitude': 1.1
            })
        self.hass.pool.block_till_done()
        
        device_state = self.hass.states.get('device_tracker.test1')
        assert device_state.state == 'home'
        device_state_lat = device_state.attributes['latitude']
        assert device_state_lat == 2.1
        device_state_lon = device_state.attributes['longitude']
        assert device_state_lon == 1.1
        
        zone_state = self.hass.states.get('zone.home')
        assert zone_state.state == 'zoning'
        proximity_latitude = zone_state.attributes.get('latitude')
        assert proximity_latitude == 2.1
        proximity_longitude = zone_state.attributes.get('longitude')
        assert proximity_longitude == 1.1
        
        assert zone.in_zone(zone_state, device_state_lat, device_state_lon)
        
        state = self.hass.states.get('proximity_zones.home')
        assert state.state == '0'
        assert state.attributes.get('nearest') == 'test1'
        assert state.attributes.get('dir_of_travel') == 'arrived'
        
    def test_device_trackers_in_zone_at_start(self):
        self.hass.states.set(
            'device_tracker.test1', 'home',
            {
                'friendly_name': 'test1',
                'latitude': 2.1,
                'longitude': 1.1
            })
        self.hass.pool.block_till_done()
        self.hass.states.set(
            'device_tracker.test2', 'home',
            {
                'friendly_name': 'test2',
                'latitude': 2.1,
                'longitude': 1.1
            })
        self.hass.pool.block_till_done()
        assert proximity_zones.setup(self.hass, {
            'proximity_zones': {
                'home': {
                    'zone': 'home',
                    'ignored_zones': {
                        'work'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                },
                'work': {
                    'zone': 'work',
                    'ignored_zones': {
                        'home'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                }
            }
        })        
        
        state = self.hass.states.get('proximity_zones.home')
        assert state.state == '0'
        assert ((state.attributes.get('nearest') == 'test1, test2') or
                (state.attributes.get('nearest') == 'test2, test1'))
        assert state.attributes.get('dir_of_travel') == 'arrived'
        
    def test_device_trackers_in_zone(self):
        assert proximity_zones.setup(self.hass, {
            'proximity_zones': {
                'home': {
                    'zone': 'home',
                    'ignored_zones': {
                        'work'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                },
                'work': {
                    'zone': 'work',
                    'ignored_zones': {
                        'home'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                }
            }
        })        
        self.hass.states.set(
            'device_tracker.test1', 'home',
            {
                'friendly_name': 'test1',
                'latitude': 2.1,
                'longitude': 1.1
            })
        self.hass.pool.block_till_done()
        self.hass.states.set(
            'device_tracker.test2', 'home',
            {
                'friendly_name': 'test2',
                'latitude': 2.1,
                'longitude': 1.1
            })
        self.hass.pool.block_till_done()
        state = self.hass.states.get('proximity_zones.home')
        assert state.state == '0'
        assert ((state.attributes.get('nearest') == 'test1, test2') or
                (state.attributes.get('nearest') == 'test2, test1'))
        assert state.attributes.get('dir_of_travel') == 'arrived'
        
    def test_device_tracker_test1_away(self):
        assert proximity_zones.setup(self.hass, {
            'proximity_zones': {
                'home': {
                    'zone': 'home',
                    'ignored_zones': {
                        'work'
                    },
                    'devices': {
                        'test1'
                    },
                    'tolerance': 1
                },
                'work': {
                    'zone': 'work',
                    'ignored_zones': {
                        'home'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                }
            }
        })
        
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1',
                'latitude': 20.1,
                'longitude': 10.1
            })
        self.hass.pool.block_till_done()
        state = self.hass.states.get('proximity_zones.home')
        assert state.attributes.get('nearest') == 'test1'
        assert state.attributes.get('dir_of_travel') == 'towards'
        
    def test_device_tracker_test1_awayfurther(self):
        assert proximity_zones.setup(self.hass, {
            'proximity_zones': {
                'home': {
                    'zone': 'home',
                    'ignored_zones': {
                        'work'
                    },
                    'devices': {
                        'test1'
                    },
                    'tolerance': 1
                },
                'work': {
                    'zone': 'work',
                    'ignored_zones': {
                        'home'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                }
            }
        })
        
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1',
                'latitude': 20.1,
                'longitude': 10.1
            })
        self.hass.pool.block_till_done()
        state = self.hass.states.get('proximity_zones.home')
        assert state.attributes.get('nearest') == 'test1'
        assert state.attributes.get('dir_of_travel') == 'towards'
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1',
                'latitude': 40.1,
                'longitude': 20.1
            })
        self.hass.pool.block_till_done()
        state = self.hass.states.get('proximity_zones.home')
        assert state.attributes.get('nearest') == 'test1'
        assert state.attributes.get('dir_of_travel') == 'away_from'
        
    def test_device_tracker_test1_awaycloser(self):
        assert proximity_zones.setup(self.hass, {
            'proximity_zones': {
                'home': {
                    'zone': 'home',
                    'ignored_zones': {
                        'work'
                    },
                    'devices': {
                        'test1'
                    },
                    'tolerance': 1
                },
                'work': {
                    'zone': 'work',
                    'ignored_zones': {
                        'home'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                }
            }
        })
        
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1',
                'latitude': 40.1,
                'longitude': 20.1
            })
        self.hass.pool.block_till_done()
        state = self.hass.states.get('proximity_zones.home')
        assert state.attributes.get('nearest') == 'test1'
        assert state.attributes.get('dir_of_travel') == 'towards'
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1',
                'latitude': 20.1,
                'longitude': 10.1
            })
        self.hass.pool.block_till_done()
        state = self.hass.states.get('proximity_zones.home')
        assert state.attributes.get('nearest') == 'test1'
        assert state.attributes.get('dir_of_travel') == 'towards'
        
    def test_all_device_trackers_in_ignored_zone(self):
        assert proximity_zones.setup(self.hass, {
            'proximity_zones': {
                'home': {
                    'zone': 'home',
                    'ignored_zones': {
                        'work'
                    },
                    'devices': {
                        'test1'
                    },
                    'tolerance': 1
                },
                'work': {
                    'zone': 'work',
                    'ignored_zones': {
                        'home'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                }
            }
        })
        
        self.hass.states.set(
            'device_tracker.test1', 'work',
            {
                'friendly_name': 'test1',
                'latitude': 100,
                'longitude': 100
            })
        self.hass.pool.block_till_done()
        state = self.hass.states.get('proximity_zones.home')
        assert state.state == 'not set'
        assert state.attributes.get('nearest') == 'not set'
        assert state.attributes.get('dir_of_travel') == 'not set'
        
    def test_all_device_trackers_in_ignored_zone_at_start(self):
        self.hass.states.set(
            'device_tracker.test1', 'work',
            {
                'friendly_name': 'test1',
                'latitude': 100,
                'longitude': 100
            })
        self.hass.pool.block_till_done()
        
        assert proximity_zones.setup(self.hass, {
            'proximity_zones': {
                'home': {
                    'zone': 'home',
                    'ignored_zones': {
                        'work'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                },
                'work': {
                    'zone': 'work',
                    'ignored_zones': {
                        'home'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                }
            }
        })
        
        state = self.hass.states.get('proximity_zones.home')
        assert state.attributes.get('nearest') == 'test2'
        assert state.attributes.get('dir_of_travel') == 'unknown'
        
    def test_device_tracker_test1_no_coordinates(self):
        assert proximity_zones.setup(self.hass, {
            'proximity_zones': {
                'home': {
                    'zone': 'home',
                    'ignored_zones': {
                        'work'
                    },
                    'devices': {
                        'test1'
                    },
                    'tolerance': 1
                },
                'work': {
                    'zone': 'work',
                    'ignored_zones': {
                        'home'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                }
            }
        })
        
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1'
            })
        self.hass.pool.block_till_done()
        state = self.hass.states.get('proximity_zones.home')
        assert state.attributes.get('nearest') == 'not set'
        assert state.attributes.get('dir_of_travel') == 'not set'
        
    def test_device_tracker_test1_no_coordinates_at_start(self):
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1'
            })
        self.hass.pool.block_till_done()
        
        assert proximity_zones.setup(self.hass, {
            'proximity_zones': {
                'home': {
                    'zone': 'home',
                    'ignored_zones': {
                        'work'
                    },
                    'devices': {
                        'test1'
                    },
                    'tolerance': 1
                },
                'work': {
                    'zone': 'work',
                    'ignored_zones': {
                        'home'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                }
            }
        })
                
        state = self.hass.states.get('proximity_zones.home')
        assert state.attributes.get('nearest') == 'not set'
        assert state.attributes.get('dir_of_travel') == 'not set'
        
    def test_device_tracker_test1_awayfurther_than_test2_first_test1(self):
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1'
            })
        self.hass.pool.block_till_done()
        self.hass.states.set(
            'device_tracker.test2', 'not_home',
            {
                'friendly_name': 'test2'
            })
        self.hass.pool.block_till_done()
        assert proximity_zones.setup(self.hass, {
            'proximity_zones': {
                'home': {
                    'zone': 'home',
                    'ignored_zones': {
                        'work'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                },
                'work': {
                    'zone': 'work',
                    'ignored_zones': {
                        'home'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                }
            }
        })
        
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1',
                'latitude': 20.1,
                'longitude': 10.1
            })
        self.hass.pool.block_till_done()
        state = self.hass.states.get('proximity_zones.home')
        assert state.attributes.get('nearest') == 'test1'
        assert state.attributes.get('dir_of_travel') == 'unknown'
        self.hass.states.set(
            'device_tracker.test2', 'not_home',
            {
                'friendly_name': 'test2',
                'latitude': 40.1,
                'longitude': 20.1
            })
        self.hass.pool.block_till_done()
        state = self.hass.states.get('proximity_zones.home')
        assert state.attributes.get('nearest') == 'test1'
        assert state.attributes.get('dir_of_travel') == 'unknown'
        
    def test_device_tracker_test1_awayfurther_than_test2_first_test2(self):
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1'
            })
        self.hass.pool.block_till_done()
        self.hass.states.set(
            'device_tracker.test2', 'not_home',
            {
                'friendly_name': 'test2'
            })
        self.hass.pool.block_till_done()
        assert proximity_zones.setup(self.hass, {
            'proximity_zones': {
                'home': {
                    'zone': 'home',
                    'ignored_zones': {
                        'work'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                },
                'work': {
                    'zone': 'work',
                    'ignored_zones': {
                        'home'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                }
            }
        })
        
        self.hass.states.set(
            'device_tracker.test2', 'not_home',
            {
                'friendly_name': 'test2',
                'latitude': 40.1,
                'longitude': 20.1
            })
        self.hass.pool.block_till_done()
        state = self.hass.states.get('proximity_zones.home')
        assert state.attributes.get('nearest') == 'test2'
        assert state.attributes.get('dir_of_travel') == 'unknown'
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1',
                'latitude': 20.1,
                'longitude': 10.1
            })
        self.hass.pool.block_till_done()
        state = self.hass.states.get('proximity_zones.home')
        assert state.attributes.get('nearest') == 'test1'
        assert state.attributes.get('dir_of_travel') == 'unknown'
        
    def test_device_tracker_test1_awayfurther_test2_in_ignored_zone(self):
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1'
            })
        self.hass.pool.block_till_done()
        self.hass.states.set(
            'device_tracker.test2', 'work',
            {
                'friendly_name': 'test2',
                'latitude': 100,
                'longitude': 100
            })
        self.hass.pool.block_till_done()
        assert proximity_zones.setup(self.hass, {
            'proximity_zones': {
                'home': {
                    'zone': 'home',
                    'ignored_zones': {
                        'work'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                },
                'work': {
                    'zone': 'work',
                    'ignored_zones': {
                        'home'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                }
            }
        })
        
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1',
                'latitude': 20.1,
                'longitude': 10.1
            })
        self.hass.pool.block_till_done()
        state = self.hass.states.get('proximity_zones.home')
        assert state.attributes.get('nearest') == 'test1'
        assert state.attributes.get('dir_of_travel') == 'unknown'
        
    def test_device_tracker_test1_awayfurther_test2_first(self):
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1'
            })
        self.hass.pool.block_till_done()
        self.hass.states.set(
            'device_tracker.test2', 'not_home',
            {
                'friendly_name': 'test2'
            })
        self.hass.pool.block_till_done()
        assert proximity_zones.setup(self.hass, {
            'proximity_zones': {
                'home': {
                    'zone': 'home',
                    'ignored_zones': {
                        'work'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                },
                'work': {
                    'zone': 'work',
                    'ignored_zones': {
                        'home'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                }
            }
        })
        
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1',
                'latitude': 10.1,
                'longitude': 5.1
            })
        self.hass.pool.block_till_done()
        
        self.hass.states.set(
            'device_tracker.test2', 'not_home',
            {
                'friendly_name': 'test2',
                'latitude': 20.1,
                'longitude': 10.1
            })
        self.hass.pool.block_till_done()
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1',
                'latitude': 40.1,
                'longitude': 20.1
            })
        self.hass.pool.block_till_done()
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1',
                'latitude': 35.1,
                'longitude': 15.1
            })
        self.hass.pool.block_till_done()
        self.hass.states.set(
            'device_tracker.test1', 'work',
            {
                'friendly_name': 'test1',
                'latitude': 100,
                'longitude': 100
            })
        self.hass.pool.block_till_done()
        state = self.hass.states.get('proximity_zones.home')
        assert state.attributes.get('nearest') == 'test2'
        assert state.attributes.get('dir_of_travel') == 'unknown'
        
    def test_device_tracker_test1_awayfurther_a_bit(self):
        assert proximity_zones.setup(self.hass, {
            'proximity_zones': {
                'home': {
                    'zone': 'home',
                    'ignored_zones': {
                        'work'
                    },
                    'devices': {
                        'test1'
                    },
                    'tolerance': 1000
                },
                'work': {
                    'zone': 'work',
                    'ignored_zones': {
                        'home'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                }
            }
        })
        
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1',
                'latitude': 20.1000001,
                'longitude': 10.1000001
            })
        self.hass.pool.block_till_done()
        state = self.hass.states.get('proximity_zones.home')
        assert state.attributes.get('nearest') == 'test1'
        assert state.attributes.get('dir_of_travel') == 'towards'
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1',
                'latitude': 20.1000002,
                'longitude': 10.1000002
            })
        self.hass.pool.block_till_done()
        state = self.hass.states.get('proximity_zones.home')
        assert state.attributes.get('nearest') == 'test1'
        assert state.attributes.get('dir_of_travel') == 'stationary'
    
    def test_device_tracker_test1_nearest_after_test2_in_ignored_zone(self):
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1'
            })
        self.hass.pool.block_till_done()
        self.hass.states.set(
            'device_tracker.test2', 'not_home',
            {
                'friendly_name': 'test2'
            })
        self.hass.pool.block_till_done()
        assert proximity_zones.setup(self.hass, {
            'proximity_zones': {
                'home': {
                    'zone': 'home',
                    'ignored_zones': {
                        'work'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                },
                'work': {
                    'zone': 'work',
                    'ignored_zones': {
                        'home'
                    },
                    'devices': {
                        'test1',
                        'test2'
                    },
                    'tolerance': 1
                }
            }
        })
        
        self.hass.states.set(
            'device_tracker.test1', 'not_home',
            {
                'friendly_name': 'test1',
                'latitude': 20.1,
                'longitude': 10.1
            })
        self.hass.pool.block_till_done()
        state = self.hass.states.get('proximity_zones.home')
        assert state.attributes.get('nearest') == 'test1'
        assert state.attributes.get('dir_of_travel') == 'unknown'
        
        self.hass.states.set(
            'device_tracker.test2', 'not_home',
            {
                'friendly_name': 'test2',
                'latitude': 10.1,
                'longitude': 5.1
            })
        self.hass.pool.block_till_done()
        state = self.hass.states.get('proximity_zones.home')
        assert state.attributes.get('nearest') == 'test2'
        assert state.attributes.get('dir_of_travel') == 'unknown'
        
        self.hass.states.set(
            'device_tracker.test2', 'work',
            {
                'friendly_name': 'test2',
                'latitude': 100,
                'longitude': 100
            })
        self.hass.pool.block_till_done()
        state = self.hass.states.get('proximity_zones.home')
        assert state.attributes.get('nearest') == 'test1'
        assert state.attributes.get('dir_of_travel') == 'unknown'
