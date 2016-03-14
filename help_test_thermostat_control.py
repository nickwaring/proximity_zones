"""
tests.components.proximity_zones
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests proximity_zones component.
"""
# import the dependencies
import homeassistant.core as ha
import os
from homeassistant.components import thermostat_control
import homeassistant.util.dt as dt_util
from tests.common import get_test_home_assistant
from datetime import timedelta
import time

class TestThermostatControl:
    """ Test the Thermostat_ccontrol component. """

    def setup_method(self, method):
        self.hass = get_test_home_assistant()

				# setup the test proximity component & give it some initial values
        self.hass.states.set(
            'proximity.test1', '60',
            {
                'dir_of_travel': 'unknown',
                'friendly_name': 'test1',
                'nearest': 'Nick',
                'unit_of_measurement': 'km'
            })
				# setup the test thermostat & give it some initial values
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
        # function which removes things it's called between tests?
        """ indeed, the setup_method is called before each test """
        """ this method is called after each test, it will stop the HA """
        """ from the test so you can start with a blank version each time """
        self.hass.stop()
    
  	# test that the compnoent creates successfully
    def test_thermostat_control(self):
				# mimic properly formatted config.yaml entry  
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

				# get the state of the created component  
        state = self.hass.states.get('thermostat_control.test1')
        
				# test the value of each of the created component  attributes
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

  	# tests what happens if there is no config.yaml entry
    def test_no_config(self):
				# mimic no config.yaml  
        assert not thermostat_control.setup(self.hass, {
        })
				
				# where are the tests in the current version?
				# component should exit gracefully
        """ wrong, the setup will fail, see line 77, it will return False """
        
        
  	# tests what happens if the schedule component is missing
    def test_no_schedule_in_config(self):
				# mimic no schedule entry in config.yaml  
        assert not thermostat_control.setup(self.hass, {
				# assert not?
        """ 'assert A' will check if A is true """
        """ 'assert not A' will check if A is false """
        """ basically, we know that the setup will return False if there is """
        """ no schedule in the config, so we know this setup must fail, """
        """ that's why we use 'assert not' here """
            'thermostat_control': {
                'test1':{
                    'max_temp': 26,
                    'dist_offset': 0.1,
                    'away_distance': 50
                }               
            }
        })
        
				# where are the tests in the current version?
				# component should exit gracefully
        state = self.hass.states.get('thermostat_control.test1')
        assert state == None
        """ we ask HA for the state of the thermostat_control """
        """ that state will be none, because the thermostat_control doesn't """
        """ exist even though the setup didn't fail """
				
    def test_no_max_temp_in_config(self):
				# mimic no max temp entry in config.yaml  
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
     
				# where are the tests in the current version?
				# component should be created successfully
				assert state.state != 'some value'
        assert state.attributes.get('some_attribute') != 'expected_state'
        
    def test_no_dist_offset_in_config(self):
        # mimic no distance offset entry in config.yaml  
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
    
				# where are the tests in the current version?
				# component should be created successfully but dist_offset should be 0 and proximity zone should be 'not_set'
				assert state.state != 'some value'
        assert state.attributes.get('dist_offest') == '0'				
        assert state.attributes.get('proximity_zone') == 'not set'

    def test_no_away_distance_in_config(self):
 			  # mimic no away distance entry in config.yaml  
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

				# where are the tests in the current version?
				# component should be created successfully but away distance should be 999999
				assert state.state != 'some value'
        assert state.attributes.get('dist_offset') == '999999'
		
		# test what happens if there are multiple thermostats
	  def test_multiple_thermostats_one_selected(self):
				# create addtional thermostat
        self.hass.states.set(
            'thermostat.test2', '23.5',
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

        # setup appropriate config.yaml entry
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
										'thermostat': test2
                    'dist_offset': 0.1,
                }
            }
        })        
						 
				# get the state of the created component  
        state = self.hass.states.get('thermostat_control.test1')
        
				# test the value of the created component attributes
				
				# delete the newly created thermostat?
				
		# test what happens if there are multiple thermostats
	  def test_multiple_thermostats_none_selected(self):
				# create addtional thermostat
        self.hass.states.set(
            'thermostat.test2', '23.5',
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

        # setup appropriate config.yaml entry
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
				
				# where are the tests?
				# component should exit gracefully

  			# delete the newly created thermostat?

		# test what happens if there are multiple proximity zones
	  def test_multiple_proximity_zones_one_selected(self):
				# create addtional proximity zone
        self.hass.states.set(
            'proximity.test2', '10',
            {
                'dir_of_travel': 'unknown',
                'friendly_name': 'test2',
                'nearest': 'Nick',
                'unit_of_measurement': 'km'
            })

        # setup appropriate config.yaml entry
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
										'proximity': test1
                    'dist_offset': 0.1,
                }
            }
        })        
						 
				# get the state of the created component  
        state = self.hass.states.get('thermostat_control.test1')
        
				# test the value of the created component attributes
				
				# delete the newly created proximity?
				
		# test what happens if there are multiple proximity zones
	  def test_multiple_proximity_zones_none_selected(self):
				# create addtional proximity zone
        self.hass.states.set(
            'proximity.test2', '10',
            {
                'dir_of_travel': 'unknown',
                'friendly_name': 'test2',
                'nearest': 'Nick',
                'unit_of_measurement': 'km'
            })

        # setup appropriate config.yaml entry
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
						 
				# where are the tests?
				# component should exit gracefully

				# delete the newly created proximity?
				
		# test what happens when the thermostat temp changes
	  def test_manual_thermostat_change(self):
				# mimic properly formatted config.yaml entry  
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

				# get the state of the created component  
        state = self.hass.states.get('thermostat_control.test1')

				# how to get the thermostat trigger to fire? set a new thermostat temperature?

				# get the new state of the thermostat component  
        state = self.hass.states.get('thermostat_control.test1')
        
				# test the value of the created component attributes
				
		# test what happens when ta schedule trigger fires
	  def test_schedule_time_trigger(self):
				# mimic properly formatted config.yaml entry  
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

				# get the state of the created component  
        state = self.hass.states.get('thermostat_control.test1')

				# how to get the time trigger to fire? override the time?

				# get the new state of the thermostat component  
        state = self.hass.states.get('thermostat_control.test1')
        
				# test the value of the created component attributes
				
