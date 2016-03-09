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
            })
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
                
    def teardown_method(self, method):
        """ Stop down stuff we started. """
        self.hass.stop()
        
    def test_thermostat_control(self):
        assert thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1':{
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

        state = self.hass.states.get('thermostat_control.test1')
        assert state.state != 'not set'
        assert state.attributes.get('next_change') != 'not set'
        assert state.attributes.get('away_mode') != 'not set'       
        assert state.attributes.get('manual_override_end') == 'not set'
        assert state.attributes.get('offset_temp') == 0
        assert state.attributes.get('unit_of_measurement') == '°C'
        assert state.attributes.get('active_from') != 'not set'
        assert state.attributes.get('manual_override') != 'not set'
        assert state.attributes.get('schedule_temp') != 'not set'
        assert state.attributes.get('friendly_name') == 'test1'
        assert state.attributes.get('set_temp') != 'not set'

    def test_no_config(self):
        assert not thermostat_control.setup(self.hass, {
        })
        
    def test_no_schedule_in_config(self):
        assert not thermostat_control.setup(self.hass, {
            'thermostat_control': {
                'test1':{
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
