"""
custom_components.temperature_control
~~~~~~~~~~~~~~~~~~~~~~~~~

thermostat_control:
  home:
    proximity_zone: home
    thermostat: kitchen
    schedule:
      - '07:00': 21.5
      - '07:15': 22.5
      - '07:30': 23.5
      - '09:00': 29.5
      - '15:15': 31.5
      - '15:30': 32.5
      - '23:00': 01.5
      - '23:15': 02.5
      - '23:45': 04.5
    max_temp: 26
    dist_offset: 0.1
    away_distance: 50
"""

import logging
from homeassistant.helpers.event import track_state_change
from homeassistant.helpers.event import track_time_change
from homeassistant.helpers.event import track_point_in_time
from homeassistant.helpers.entity import Entity
from homeassistant.components import zone
from homeassistant.const import CONF_NAME
import homeassistant.util.dt as dt_util
from datetime import timedelta
import time

DEPENDENCIES = ['thermostat', 'proximity']

# domain for the component
DOMAIN = 'thermostat_control'

# default control values
DEFAULT_OFFSET = 0
DEFAULT_AWAY = 50

# default zone
DEFAULT_PROX_ZONE = 'not_set'

# entity attributes
ATTR_SCHEDULE_START = 'active_from'
ATTR_SCHEDULE_NEXT = 'next_change'
ATTR_SCHEDULE_TEMP = 'schedule_temp'
ATTR_SET_TEMP = 'set_temp'
ATTR_NAME = 'friendly_name'
ATTR_OFFSET_TEMP = 'offset_temp'
ATTR_MANUAL_OVERRIDE = 'manual_override'
ATTR_MANUAL_OVERRIDE_END = 'manual_override_end'
ATTR_AWAY = 'Away_mode'

# Shortcut for the logger
_LOGGER = logging.getLogger(__name__)

def setup(hass, config):  # pylint: disable=too-many-locals,too-many-statements
    """ get the zones and offsets from configuration.yaml"""

    thermostat_controls = []

    if config.get(DOMAIN) is None:
        return False

    for control_location, control_config in config[DOMAIN].items():
        if 'thermostat' not in control_config:
            _LOGGER.error('no thermostat in config')
            return False

        if 'schedule' not in control_config:
            _LOGGER.error('no time schedule in config')
            return False

        thermostat_entity = 'thermostat.' + control_config.get('thermostat')
        if thermostat_entity not in hass.states.entity_ids('thermostat'):
            _LOGGER.error('thermostat_entity not found')
            return

        state = hass.states.get(thermostat_entity)
        thermostat_friendly_name = (state.name).lower()
        _LOGGER.error('thermostat_friendly_name: %s', thermostat_friendly_name)

        dist_offset = control_config.get('dist_offset', DEFAULT_OFFSET)
        _LOGGER.error('dist_offset: %s', dist_offset)

        away_distance = control_config.get('away_distance', DEFAULT_AWAY)
        _LOGGER.error('away_distance: %s', away_distance)

        proximity_zone = 'proximity.' + control_config.get('proximity_zone',
                                                           DEFAULT_PROX_ZONE)
        if proximity_zone not in hass.states.entity_ids('proximity'):
            _LOGGER.error('proximity_entity not found')
            return
        _LOGGER.error('proximity_zone: %s', proximity_zone)

        entity_id = DOMAIN + '.' + control_location
        _LOGGER.error('entity_id: %s', entity_id)

        friendly_name = control_location
        _LOGGER.error('name: %s', friendly_name)

        control_schedule = {}
        for each_entry in control_config['schedule']:
            for each_time in each_entry:
                control_schedule[each_time] = each_entry.get(each_time)

        # set the default values
        schedule_start = 'not set'
        schedule_next = 'not set'
        schedule_temp = 'not set'
        away_mode = 'not set'
        set_temp = 'not set'
        offset_temp = 0
        manual_override = 'not set'
        manual_override_end = 'not set'

        thermostat_control = Thermostat_control(hass, thermostat_entity,
                                                dist_offset, away_distance,
                                                control_schedule,
                                                schedule_start, schedule_temp,
                                                set_temp, friendly_name,
                                                offset_temp, manual_override,
                                                manual_override_end,
                                                schedule_next, away_mode,
                                                proximity_zone)
        thermostat_control.entity_id = entity_id
        thermostat_control.update_ha_state()
        thermostat_controls.append(thermostat_control)
        thermostat_control.check_initial_state()

        # setup the proximity trigger
        if not proximity_zone == 'not_set':
            track_state_change(hass, thermostat_control.proximity_zone,
                               thermostat_control.check_proximity_change)
            _LOGGER.error('proximity trigger added: %s', proximity_zone)

        # setup the schedule triggers
        for each_time in control_schedule:
            each_time = dt_util.parse_time_str(each_time)
            if each_time is None:
                _LOGGER.error('error reading time schedule: %s',
                    control_location)
                continue
            track_time_change(hass, thermostat_control.check_time_change,
                              hour=each_time.hour,
                              minute=each_time.minute,
							  second=each_time.second)
            _LOGGER.error('time trigger added: time:%s hour:%s minute:%s',
                          each_time, each_time.hour, each_time.minute)

        # setup the thermostat trigger
        track_state_change(hass, thermostat_control.thermostat_entity,
                           thermostat_control.check_thermostat_change)
        _LOGGER.error('thermostat trigger added: %s', thermostat_entity)

    if not thermostat_controls:
        _LOGGER.error('No controls defined')
        return False

    # Tells the bootstrapper that the component was successfully initialized
    return True

class Thermostat_control(Entity):
    # pylint: disable=too-many-instance-attributes
    # Represents a Proximity in Home Assistant.
    def __init__(self, hass, thermostat_entity, dist_offset, away_distance,
                 control_schedule, schedule_start, schedule_temp, set_temp,
                 friendly_name, offset_temp, manual_override,
                 manual_override_end, schedule_next, away_mode,
                 proximity_zone):
        # pylint: disable=too-many-arguments
        self.hass = hass
        self.control_schedule = control_schedule
        self.thermostat_entity = thermostat_entity
        self.dist_offset = dist_offset
        self.away_distance = away_distance
        self.friendly_name = friendly_name
        self.offset_temp = offset_temp
        self.schedule_start = schedule_start
        self.schedule_next = schedule_next
        self.schedule_temp = schedule_temp
        self.manual_override = manual_override
        self.manual_override_end = manual_override_end
        self.away_mode = away_mode
        self.set_temp = set_temp
        self.proximity_zone = proximity_zone

    @property
    def state(self):
        return self.set_temp

    @property
    def unit_of_measurement(self):
        # Unit of measurement of this entity
        return "°C"

    @property
    def state_attributes(self):
        return {
            ATTR_SCHEDULE_START: self.schedule_start,
            ATTR_SCHEDULE_NEXT: self.schedule_next,
            ATTR_SCHEDULE_TEMP: self.schedule_temp,
            ATTR_OFFSET_TEMP: self.offset_temp,
            ATTR_SET_TEMP: self.set_temp,
            ATTR_NAME: self.friendly_name,
            ATTR_MANUAL_OVERRIDE: self.manual_override,
            ATTR_MANUAL_OVERRIDE_END: self.manual_override_end,
            ATTR_AWAY: self.away_mode
        }

    def check_proximity_change(self, entity, old_state, new_state):
        # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        """ Function to handle a change in proximity """
        
        # proximity is not set
        if new_state.state == 'not set':
            return

        # proximity has not changed
        if old_state.state == new_state.state:
            self.update_ha_state()
            return

        # manual override is set
        if self.manual_override == 'on':
            self.update_ha_state()
            return

        self.offset_temp = round(int(new_state.state) * self.dist_offset, 1) * -1

        # proximity is greater than distance to away
        if int(new_state.state) > int(self.away_distance):
            self.away_mode = 'on'
            self.update_ha_state()
            # =========SET THERMOSTAT TO AWAY
            # =========SET THERMOSTAT TEMP
            _LOGGER.info('proximity set_thermostat_away: distance:%s offset:%s'
                         , new_state.state, self.offset_temp)
            return

        # proximity is 0 therefore offset is 0
        if int(new_state.state) == 0:
            self.offset_temp = 0
            self.away_mode = 'off'
            self.set_temp = float(self.schedule_temp) + float(self.offset_temp)
            self.update_ha_state()
            # ========SET THERMOSTAT TO HOME
            # ========SET THERMOSTAT TEMP
            _LOGGER.info('proximity set_thermostat_temp: distance:%s offset:%s'
                         , new_state.state, self.offset_temp)
            return

        # set the temperature
        self.set_temp = float(self.schedule_temp) + float(self.offset_temp)
        self.update_ha_state()
        # ========SET THERMOSTAT TEMP

        _LOGGER.info('proximity set_thermostat_temp: distance:%s direction:%s'
                     'offset:%s', new_state.state,
                     new_state.attributes['dir_of_travel'], self.offset_temp)

        _LOGGER.info('proximity change complete')

    def check_time_change(self, trigger_time):
        # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        """ Function to handle a sheduled temperature change """

        now_time = (str(trigger_time.hour).zfill(2) + ':'
                           + str(trigger_time.minute).zfill(2))

        if now_time not in self.control_schedule:
            _LOGGER.info('time: trigger not found in schedule:%s',
                         each_entry)
            _LOGGER.info('schedule change: no action: time not found in schedule')
            return

        self.schedule_temp = self.control_schedule[now_time]
        self.schedule_start = now_time

        # get the next schedule change time
        count_previous = -10000000
        count_next = 10000000
        now_time = time.mktime(time.strptime(now_time, "%H:%M"))        
        for each_entry in self.control_schedule:
            compare_time = time.mktime(time.strptime(each_entry, "%H:%M"))
            time_diff = now_time - compare_time
            #_LOGGER.info('time_diff: %s', time_diff)

            if time_diff > count_previous and time_diff < 0:
                count_previous = time_diff
                schedule_next = each_entry
                #_LOGGER.info('time: previous:%s', schedule_next)
        _LOGGER.info('time: closest next:%s', schedule_next)

        self.schedule_next = schedule_next

        if self.manual_override == "on":
            self.update_ha_state()
            return

        if self.away_mode == "on":
            self.update_ha_state()
            return

        self.set_temp = float(self.schedule_temp) + float(self.offset_temp)
        self.update_ha_state()

        # ========SET THERMOSTAT TEMP
        _LOGGER.info('schedule set_thermostat_temp: schedule time:%s temp:%s',
                     self.schedule_start, self.schedule_temp)

        _LOGGER.info('schedule change complete')

    def check_thermostat_change(self, entity, old_state, new_state):
        # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        """ Function to handle a manual thermostat change """

        # state not changed
        if new_state.attributes['away_mode'] == 'on':
            self.away_mode = 'away'
            self.update_ha_state()
            _LOGGER.info('thermostat change: no action: awaymode on')
            return

        # state not changed
        if old_state.state == new_state.state:
            _LOGGER.info('thermostat change: no action: no change')
            return

        # state is not set at startup
        if new_state.state == 'not set':
            _LOGGER.info('thermostat change: no action: state not set')
            return

        # state change triggered by thermostat_control proximity
        if float(new_state.state) == (float(self.schedule_temp) +
                                      float(self.offset_temp)):
            _LOGGER.info('thermostat change: no action: change triggered by thermostat_control')
            return

        # state change triggered by thermostat_control schedule
        if new_state.state == self.schedule_temp:
            _LOGGER.info('thermostat change: no action: change triggered by thermostat_control')
            return

        # setup the thermostat trigger to reset back after duration
        reset_time = dt_util.now() + timedelta(hours=1)
        track_point_in_time(self.hass, self.reset_override,
                            reset_time)
        _LOGGER.error('override trigger added: %s', reset_time)

        # manual thermostat change overrides all settings
        reset_time = str(reset_time.hour) + ':' + str(reset_time.minute)
        #trigger_time = (str(dt_util.now().hour).zfill(2) + ':'
        #                + str(dt_util.now().minute).zfill(2))
        self.manual_override_end = reset_time

        self.manual_override = 'on'
        self.away_mode = 'off'
        self.set_temp = new_state.state
        self.update_ha_state()
        
        # thermostat change not required as manually set
        _LOGGER.info('thermostat change complete')

    def reset_override(self, trigger_time):
        # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        """ Function to reset a manual thermostat change """

        # set the schedule temperature and other variables
        self.manual_override = 'off'
        self.manual_override_end = 'not set'
        self.set_temp = float(self.schedule_temp) + float(self.offset_temp)
        self.update_ha_state()

        # ========SET THERMOSTAT TEMP
        _LOGGER.info('time set_thermostat_temp: override reset: temp:%s',
                     self.set_temp)

        _LOGGER.info('override reset complete')

    def check_initial_state(self):
        # get the closest time
        now_time = str(dt_util.now().hour) + ':' + str(dt_util.now().minute)
        now_time = time.mktime(time.strptime(now_time, "%H:%M"))

        count_previous = -10000000
        count_next = 10000000
        for each_entry in self.control_schedule:
            compare_time = time.mktime(time.strptime(each_entry, "%H:%M"))
            time_diff = now_time - compare_time
            #_LOGGER.info('time_diff: %s', time_diff)

            if time_diff < count_next and time_diff > 0:
                count_next = time_diff
                schedule_previous = each_entry
                #_LOGGER.info('time: next:%s', schedule_previous)
            if time_diff > count_previous and time_diff < 0:
                count_previous = time_diff
                schedule_next = each_entry
                #_LOGGER.info('time: previous:%s', schedule_next)
        _LOGGER.info('time: closest next:%s', schedule_next)
        _LOGGER.info('time: closest previous:%s', schedule_previous)

        self.schedule_start = schedule_previous
        self.schedule_next = schedule_next
        self.schedule_temp = self.control_schedule[schedule_previous]
        self.offset_temp = 0
        self.manual_override = 'off'
        self.manual_override_end = 'not set'
        self.away_mode = 'off'
        self.set_temp = float(self.schedule_temp)
        self.update_ha_state()
