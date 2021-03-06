"""
custom_components.temperature_control
~~~~~~~~~~~~~~~~~~~~~~~~~

thermostat_control:
  home:                     required: use to specify the friendly name of the
                                      control entity
    schedule:               required:
      - '07:00': 21.5
      - '07:15': 22.5
      - '07:30': 23.5
      - '09:00': 29.5
      - '15:15': 31.5
      - '15:30': 32.5
      - '23:00': 01.5
      - '23:15': 02.5
      - '23:45': 04.5
    thermostat: kitchen     optional: only required if more then one thermostat
                                      exists
    max_temp: 26            optional: set the failsafe temperature the
                                      thermostat will not exceed
    min_temp: 15            optional: set the failsafe temperature the
                                      thermostat will not fall below
    proximity:              optional: add to enable proximity based control
      distance_offset: 0.1  optional: set the value to which will be applied to
                                      the schedule temperature based on the
                                      proximity of the nearest tracked device
                                      (in degrees per km)
      zone:                 optional: required if more than one proximitiy
                                      entity exists
      away_distance: 50     optional: the distance after which the thermostat
                                      will be put into away mode
"""

import logging
import datetime as dt
from homeassistant.helpers.event import track_state_change
from homeassistant.helpers.event import track_time_change
from homeassistant.helpers.event import track_point_in_time
from homeassistant.helpers.entity import Entity
import homeassistant.util.dt as dt_util

DEPENDENCIES = ['thermostat', 'proximity']

# domain for the component
DOMAIN = 'thermostat_control'

# default control values
DEFAULT_OFFSET = 0
DEFAULT_AWAY = 999999
DEFAULT_MAX_TEMP = 25
DEFAULT_MIN_TEMP = 15

# entity attributes
ATTR_SCHEDULE_START = 'active_from'
ATTR_SCHEDULE_NEXT = 'next_change'
ATTR_SCHEDULE_TEMP = 'schedule_temp'
ATTR_SET_TEMP = 'set_temp'
ATTR_NAME = 'friendly_name'
ATTR_OFFSET_TEMP = 'offset_temp'
ATTR_MANUAL_OVERRIDE = 'manual_override'
ATTR_MANUAL_OVERRIDE_END = 'manual_override_end'
ATTR_AWAY = 'away_mode'

# Shortcut for the logger
_LOGGER = logging.getLogger(__name__)


def setup(hass, config):
    # pylint: disable=too-many-locals,too-many-return-statements,
    # pylint: disable=too-many-statements,too-many-branches
    """ get the zones and offsets from configuration.yaml"""

    thermostat_controls = []

    # no config found
    if config.get(DOMAIN) is None:
        return False

    for control_location, control_config in config[DOMAIN].items():
        # ============== Thermostat checking ==============
        thermostat_entity = "not set"

        # HA does not have a thermostat
        if len(hass.states.entity_ids('thermostat')) == 0:
            _LOGGER.error('HA does not have any thermostats')
            continue

        # a single thermostat has been found so default to it
        if len(hass.states.entity_ids('thermostat')) == 1:
            thermostat_entity = hass.states.entity_ids('thermostat')[0]
            _LOGGER.error('defaulting to thermostat: %s', thermostat_entity)

        # get the thermostat if it's in the config
        if 'thermostat' in control_config:
            thermostat_entity = ('thermostat.' + control_config['thermostat'])

            # check thermostat exists
            if thermostat_entity not in hass.states.entity_ids('thermostat'):
                _LOGGER.error('thermostat_entity not found')
                continue

        # skip processing if we don't have a thermostat
        if thermostat_entity == "not set":
            continue

        _LOGGER.error('thermostat_entity confirmed: %s', thermostat_entity)

        # ============== Schedule checking ==============
        # Config does not include schedule
        if 'schedule' not in control_config:
            _LOGGER.error('no schedule in config')
            continue

        # get maximum set temperature
        max_temp = control_config.get('max_temp', DEFAULT_MAX_TEMP)
        _LOGGER.error('max_temp set to: %s', max_temp)

        # get minimum set temperature
        min_temp = control_config.get('min_temp', DEFAULT_MIN_TEMP)
        _LOGGER.error('min_temp set to: %s', min_temp)

        # check the timers
        schedule_error = 0
        control_schedule = {}

        for each_time in control_config.get('schedule'):
            each_temp = control_config['schedule'][each_time]

            # incorrectly formatted schedule time, mark as an error
            test_time = dt_util.parse_time(each_time)
            if test_time is None:
                schedule_error = 1
                _LOGGER.error('schedule error: incorrectly formatted time: %s',
                              each_time)
                continue

            # schedule temp exceeds max temp, mark as an error
            if each_temp > max_temp:
                schedule_error = 1
                _LOGGER.error('schedule error: temp exceeds max_temp: %s',
                              each_temp)
                continue

            # schedule temp is lower than min temp, mark as an error
            if each_temp < min_temp:
                schedule_error = 1
                _LOGGER.error('schedule error: temp is lower than min_temp:'
                              '%s', each_temp)
                continue

            control_schedule[each_time] = each_temp
            _LOGGER.error('time: %s temp: %s', each_time, each_temp)

        # skip processing if config does not have a properly formatted time
        if schedule_error == 1:
            continue

        _LOGGER.error('schedule read successfully')

        # ============== Proximity checking ==============
        proximity_zone = "not set"
        dist_offset = DEFAULT_OFFSET
        away_distance = DEFAULT_AWAY
        # do we need to add proximity control
        if 'proximity' in control_config:
            # HA does not have a proximity_zone
            if len(hass.states.entity_ids('proximity')) == 0:
                _LOGGER.error('Error in setup: No proximity_zone entities ' +
                              'exist')
                continue

            # Single Prozimity Zone found
            if len(hass.states.entity_ids('proximity')) == 1:
                proximity_zone = hass.states.entity_ids('proximity')[0]
                _LOGGER.error('defaulting to proximity zone: %s',
                              proximity_zone)

            # get the proximity zone if it's in the config
            if 'zone' in control_config['proximity']:
                proximity_zone = ('proximity.' +
                                  control_config['proximity']['zone'])

                _LOGGER.error('proximity_zone in config: %s', proximity_zone)

            # if proximity_zone is "not set" there is a problem in the config
            if proximity_zone == "not set":
                _LOGGER.error('Error in Config: No Proximity zone found')
                continue

            # check proximity zone we are going to use exists
            if proximity_zone not in hass.states.entity_ids('proximity'):
                _LOGGER.error('Error in Config: Specified proximity zone ' +
                              'does not exist')
                continue
            _LOGGER.error('proximity_zone entity confirmed: %s',
                          proximity_zone)

            # get the distance offset
            if 'distance_offset' in control_config['proximity']:
                dist_offset = control_config['proximity']['distance_offset']
                _LOGGER.error('dist_offset: %s', dist_offset)

            # get the away distance
            if 'away_distance' in control_config['proximity']:
                away_distance = control_config['proximity']['away_distance']
                _LOGGER.error('away_distance: %s', away_distance)

            # config contains neither distance offset nor away distance
            # proximity control is useless
            if dist_offset == DEFAULT_OFFSET and away_distance == DEFAULT_AWAY:
                proximity_zone = "not set"

        # ============== Create the thermostat control entities ==============
        # set the entity ID
        entity_id = DOMAIN + '.' + control_location
        _LOGGER.error('entity_id: %s', entity_id)

        # set the friendly name for the created entity
        friendly_name = control_location

        # we have all the information required, now create the entity
        thermostat_control = Thermostatcontrol(hass, thermostat_entity,
                                               dist_offset, away_distance,
                                               control_schedule,
                                               friendly_name, proximity_zone,
                                               max_temp, min_temp)

        thermostat_control.entity_id = entity_id
        thermostat_control.update_ha_state()
        thermostat_controls.append(thermostat_control)
        thermostat_control.check_initial_state()

        # setup the schedule triggers
        for each_time in control_schedule:
            each_time = dt_util.parse_time(each_time)
            track_time_change(hass, thermostat_control.check_time_change,
                              hour=each_time.hour,
                              minute=each_time.minute,
                              second=each_time.second)
        _LOGGER.error('added time triggers: %s triggers',
                      len(control_schedule))

        # setup the thermostat trigger
        track_state_change(hass, thermostat_control.thermostat_entity,
                           thermostat_control.check_thermostat_change)
        _LOGGER.error('added thermostat trigger: %s', thermostat_entity)

        # setup the proximity trigger if required
        if not proximity_zone == "not set":
            track_state_change(hass, thermostat_control.proximity_zone,
                               thermostat_control.check_proximity_change)
            _LOGGER.error('added proximity trigger: %s', proximity_zone)

    if not thermostat_controls:
        _LOGGER.error('No controls defined')
        return False

    # Tell the bootstrapper that the component was successfully initialized
    return True


class Thermostatcontrol(Entity):
    # pylint: disable=too-many-branches,too-many-statements,too-many-locals
    # pylint: disable=too-many-instance-attributes
    """ Represents a Proximity in Home Assistant"""
    def __init__(self, hass, thermostat_entity, dist_offset, away_distance,
                 control_schedule, friendly_name, proximity_zone, max_temp,
                 min_temp):
        # pylint: disable=too-many-arguments
        self.hass = hass
        self.control_schedule = control_schedule
        self.thermostat_entity = thermostat_entity
        self.dist_offset = dist_offset
        self.away_distance = away_distance
        self.friendly_name = friendly_name
        self.proximity_zone = proximity_zone
        self.max_temp = max_temp
        self.min_temp = min_temp
        # set the default values
        self.schedule_start = 'not set'
        self.schedule_next = 'not set'
        self.schedule_temp = 'not set'
        self.set_temp = 'not set'
        self.offset_temp = 0
        self.manual_override = 'not set'
        self.manual_override_end = 'not set'
        self.change_triggered_by_ha = 0

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
            ATTR_MANUAL_OVERRIDE_END: self.manual_override_end
        }

    def check_proximity_change(self, entity, old_state, new_state):
        # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        """ Function to handle a change in proximity """
        # *********? what happens if no away distance has been calculated?
        _LOGGER.error('start: proximity change triggered')

        # proximity is not set
        if new_state.state == 'not set':
            _LOGGER.error('ignore: proximity state is not set')
            return

        # proximity has not changed
        if old_state.state == new_state.state:
            _LOGGER.error('ignore: no change in proximity state')
            return

        # proximity is greater than distance to away - turn on away mode
        if int(new_state.state) > int(self.away_distance):
            # ==== CONTROL ====
            self.change_triggered_by_ha = 1
            self.hass.services.call('thermostat', 'set_away_mode',
                                     {'entity_id': self.thermostat_entity,
                                     'away_mode': 'on'})
            self.update_ha_state()
            _LOGGER.error('end: set away_mode on: distance: %s',
                         new_state.state)
            return

        # if thermostat is away, turn it on
        thermostat_state = self.hass.states.get(self.thermostat_entity)
        away_mode = thermostat_state.attributes['away_mode']
        if away_mode == 'on':
            # ==== CONTROL ====
            self.change_triggered_by_ha = 1
            self.hass.services.call('thermostat', 'set_away_mode',
                                    {'entity_id': self.thermostat_entity,
                                    'away_mode': 'off'})
            _LOGGER.error('set away_mode off: distance: %s', new_state.state)

        # set the temperature based on the direction of travel
        # if new_state.attributes['dir_of_travel'] == 'towards':
        #    self.offset_temp = (round(int(new_state.state) *
        #                        self.dist_offset, 1) * 1)
        # if new_state.attributes['dir_of_travel'] == 'away_from':
        #    self.offset_temp = (round(int(new_state.state) *
        #                        self.dist_offset, 1) * -1)
        # if new_state.attributes['dir_of_travel'] == 'arrived':
        #    self.offset_temp = 0
        # if new_state.attributes['dir_of_travel'] == 'not set':
        #    self.offset_temp = self.offset_temp
        # if new_state.attributes['dir_of_travel'] == 'unknown':
        #    self.offset_temp = self.offset_temp
        # if new_state.attributes['dir_of_travel'] == 'stationary':
        #    self.offset_temp = self.offset_temp

        # set the offset temperature
        self.offset_temp = (round(int(new_state.state) *
                            self.dist_offset, 1) * -1)                               
        self.set_temp = float(self.schedule_temp) + float(self.offset_temp)

        # ==== CONTROL ====
        self.change_triggered_by_ha = 1
        self.hass.services.call('thermostat', 'set_temperature',
                                {'entity_id': self.thermostat_entity,
                                'temperature': self.set_temp})
        self.update_ha_state()

        _LOGGER.error('end: set_temp: %s distance: %s direction: %s'
                      ' offset: %s', self.set_temp, new_state.state,
                      new_state.attributes['dir_of_travel'], self.offset_temp)

    def check_time_change(self, trigger_time):
        # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        """ Function to handle a sheduled temperature change """

        now_time = (str(trigger_time.hour).zfill(2) + ':' +
                    str(trigger_time.minute).zfill(2))

        _LOGGER.error('start: schedule change triggered: now_time %s',
                      now_time)

        self.schedule_temp = self.control_schedule[now_time]
        self.schedule_start = now_time

        # get the next schedule change time
        schedule_next = 'not set'
        now_date = trigger_time.date()
        now_datetime = dt_util.as_utc(trigger_time)
        count_previous = -10000000
        _LOGGER.error('searching for next schedule change')
        for each_entry in self.control_schedule:
            each_time = dt.datetime.strptime(each_entry, "%H:%M").time()
            each_datetime = dt.datetime.combine(now_date, each_time)
            each_datetime = dt_util.as_utc(each_datetime)
            time_diff = (now_datetime - each_datetime).total_seconds()
            if time_diff > count_previous and time_diff < 0:
                count_previous = time_diff
                schedule_next = each_entry

        # if next is not found, reset the time to 00:01 & try again
        if schedule_next == 'not set':
            _LOGGER.error('2nd search for next schedule change')
            now_time = dt.datetime.strptime('00:01', "%H:%M").time()
            now_datetime = dt.datetime.combine(now_date, now_time)
            now_datetime = dt_util.as_utc(now_datetime)
            count_previous = -10000000
            for each_entry in self.control_schedule:
                each_time = dt.datetime.strptime(each_entry, "%H:%M").time()
                each_datetime = dt.datetime.combine(now_date, each_time)
                each_datetime = dt_util.as_utc(each_datetime)
                time_diff = (now_datetime - each_datetime).total_seconds()
                if time_diff > count_previous and time_diff < 0:
                    count_previous = time_diff
                    schedule_next = each_entry

        _LOGGER.error('time: closest next:%s', schedule_next)

        self.schedule_next = schedule_next

        # stop if manual override is on
        if self.manual_override == "on":
            _LOGGER.error('ignore: manual override is on')
            self.update_ha_state()
            return

        # stop if the thermostat is in away mode
        thermostat_state = self.hass.states.get(self.thermostat_entity)
        away_mode = thermostat_state.attributes['away_mode']
        if away_mode == 'on':
            _LOGGER.error('ignore: away_mode is on')
            self.update_ha_state()
            return

        # set the thermostat temperature
        self.set_temp = float(self.schedule_temp) + float(self.offset_temp)
        # ==== CONTROL ====
        self.change_triggered_by_ha = 1
        self.hass.services.call('thermostat', 'set_temperature',
                                {'entity_id': self.thermostat_entity,
                                'temperature': self.set_temp})
        self.update_ha_state()

        _LOGGER.error('end: set_temp: %s', self.schedule_temp)

    def check_thermostat_change(self, entity, old_state, new_state):
        # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        """ Function to handle a manual thermostat change """

        _LOGGER.error('start: thermostat change triggered')

        # skip thermostat changes triggered by thermostat_control
        if self.change_triggered_by_ha == 1:
            self.change_triggered_by_ha = 0
            self.update_ha_state()
            _LOGGER.error('ignore: change triggered by HA')
            return

        # state not changed
        if new_state.attributes['away_mode'] == 'on':
            _LOGGER.error('ignore: away mode is on')
            return

        # state not changed
        if old_state.state == new_state.state:
            _LOGGER.error('ignore: no change in thermostat value')
            return

        # state is not set at startup
        if new_state.state == 'not set':
            _LOGGER.error('ignore: thermostat state not set')
            return

        # setup the thermostat trigger to reset back after duration
        reset_time = dt_util.utcnow() + dt.timedelta(hours=1)
        track_point_in_time(self.hass, self.reset_override,
                            reset_time)
        _LOGGER.error('override trigger added: %s', reset_time)

        # manual thermostat change overrides all settings
        reset_time = (str(reset_time.hour).zfill(2) + ':' +
                      str(reset_time.minute).zfill(2))

        self.manual_override = 'on'
        self.manual_override_end = reset_time
        self.set_temp = new_state.state
        self.update_ha_state()

        # thermostat change not required as manually set
        _LOGGER.error('end: thermostat change complete reset: %s set_temp: %s',
                      reset_time, new_state.state)

    def reset_override(self, trigger_time):
        # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        """ Function to reset a manual thermostat change """

        _LOGGER.error('start: reset manual override triggered')

        # reset the manual override information
        self.manual_override = 'off'
        self.manual_override_end = 'not set'

        # if the thermostat is in away mode??
        # ===================================
        # ===================================
        # ===================================

        # update the temperature
        self.set_temp = float(self.schedule_temp) + float(self.offset_temp)
        self.update_ha_state()
        self.hass.services.call('thermostat', 'set_temperature',
                                {'entity_id': self.thermostat_entity,
                                'temperature': self.set_temp})

        _LOGGER.error('end: override reset: set_temp: %s', self.set_temp)

    def check_initial_state(self):
        # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        """ Function to populate entity on startup """

        _LOGGER.error('start: initialise entity triggered')
        schedule_next = 'not set'
        schedule_previous = 'not set'

        # calculate the previous and next schedule changes
        now_date = dt_util.utcnow().date()
        now_datetime = dt_util.utcnow()
        count_previous = -10000000
        count_next = 10000000
        for each_entry in self.control_schedule:
            each_time = dt.datetime.strptime(each_entry, "%H:%M").time()
            each_datetime = dt.datetime.combine(now_date, each_time)
            each_datetime = dt_util.as_utc(each_datetime)
            time_diff = (now_datetime - each_datetime).total_seconds()
            if time_diff < count_next and time_diff > 0:
                count_next = time_diff
                schedule_previous = each_entry
            if time_diff > count_previous and time_diff < 0:
                count_previous = time_diff
                schedule_next = each_entry

        # if previous is not found, reset the time to 23:59 & try again
        if schedule_previous == 'not set':
            _LOGGER.error('2nd search for previous schedule change')
            now_time = dt.datetime.strptime('23:59', "%H:%M").time()
            now_datetime = dt.datetime.combine(now_date, now_time)
            now_datetime = dt_util.as_utc(now_datetime)
            count_next = 10000000
            for each_entry in self.control_schedule:
                each_time = dt.datetime.strptime(each_entry, "%H:%M").time()
                each_datetime = dt.datetime.combine(now_date, each_time)
                each_datetime = dt_util.as_utc(each_datetime)
                time_diff = (now_datetime - each_datetime).total_seconds()
                if time_diff < count_next and time_diff > 0:
                    count_next = time_diff
                    schedule_previous = each_entry

        # if next is not found, reset the time to 00:01 & try again
        if schedule_next == 'not set':
            _LOGGER.error('2nd search for next schedule change')
            now_time = dt.datetime.strptime('00:01', "%H:%M").time()
            now_datetime = dt.datetime.combine(now_date, now_time)
            now_datetime = dt_util.as_utc(now_datetime)
            count_previous = -10000000
            for each_entry in self.control_schedule:
                each_time = dt.datetime.strptime(each_entry, "%H:%M").time()
                each_datetime = dt.datetime.combine(now_date, each_time)
                each_datetime = dt_util.as_utc(each_datetime)
                time_diff = (now_datetime - each_datetime).total_seconds()
                if time_diff > count_previous and time_diff < 0:
                    count_previous = time_diff
                    schedule_next = each_entry

        _LOGGER.error('closest: previous %s next: %s', schedule_previous,
                      schedule_next)

        # set the initial state of the entitiy attributes
        self.set_temp = self.control_schedule[schedule_previous]
        self.schedule_start = schedule_previous
        self.schedule_next = schedule_next
        self.schedule_temp = self.control_schedule[schedule_previous]
        self.offset_temp = 0
        self.manual_override = 'off'
        self.manual_override_end = 'not set'

        # set the thermostat temperature
        self.change_triggered_by_ha = 1
        self.hass.services.call('thermostat', 'set_temperature',
                                {'entity_id': self.thermostat_entity,
                                'temperature': self.set_temp})
        self.update_ha_state()

        _LOGGER.error('end: initialise set_temp: %s', self.set_temp)