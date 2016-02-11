"""
custom_components.proximity_zones
~~~~~~~~~~~~~~~~~~~~~~~~~

proximity_zones:
- zone: home
    ignored_zones:
      - twork
      - elschool
    devices:
      - device_tracker.nwaring_nickmobile
      - device_tracker.eleanorsiphone
      - device_tracker.tsiphone
    tolerance: 1
- zone: work
    ignored_zones:
      - home
    devices:
      - device_tracker.nwaring_nickmobile
    tolerance: 10
"""

import logging
from homeassistant.helpers.event import track_state_change
from homeassistant.helpers.entity import Entity
from homeassistant.util.location import distance
from homeassistant.components import zone

DEPENDENCIES = ['zone', 'device_tracker']

# domain for the component
DOMAIN = 'proximity_zones'

# default tolerance
DEFAULT_TOLERANCE = 1

# default zone
DEFAULT_PROXIMITY_ZONE = 'home'

# entity attributes
ATTR_DIST_FROM = 'dist_to_zone'
ATTR_DIR_OF_TRAVEL = 'dir_of_travel'
ATTR_NEAREST = 'nearest'
ATTR_FRIENDLY_NAME = 'friendly_name'

# Shortcut for the logger
_LOGGER = logging.getLogger(__name__)

def setup(hass, config):  # pylint: disable=too-many-locals,too-many-statements
    """ get the zones and offsets from configuration.yaml"""
 
    # stop if no zones are specified
    if 'zone' not in config[DOMAIN]:
        _LOGGER.error('zones not found in config')
        return False

    # mater list to record zones, devices & ignore zones
    proximity_list = []
    
    # setup a master device list
    master_device_list = []
    
    # for each zone in the config file
    for zone in config[DOMAIN]['zone']:

        # setup empty lists to store config variables in
        devices[]
        ignored_zones[]
        tolerance[]
        
        # create the config lists (need to think about error checking)
        for variable in config[DOMAIN][zone]['devices']:
            devices.append(variable)
            master_device_list.append(variable)
        for variable config[DOMAIN][zone]['ignored_zones']:
            ignored_zones.append(variable)
        for variable config[DOMAIN][zone]['tolerance']:
            tolerance.append(variable)

        # create the master list of lists
        proximity_list.append([zone, devices, ignored_zones, tolerance])

        # for loop to iterate through the master list of list
        # use index values to make recall of values easier
        for zone_entry in range(len(proximity_list)):
            _LOGGER.debug('%s: getting proximity zone config',
                          device_list[zone_entry][0])
            proximity_zone = device_list[zone_entry][0]
            
            # the devices to be tracked
            for device in device_list[zone_entry][1]:
                print("device: " + device)
                _LOGGER.debug('%s: device added: %s',
                              device_list[zone_entry][0], device)

            # recall the ignore zones
            for ignore in device_list[zone_entry][2]:
                print("ignore: " + ignore)
                _LOGGER.debug('%s: ignore zone added: %s',
                              device_list[zone_entry][0], ignore)

            # recall the tolerance
            for tolerance in device_list[zone_entry][3]:
                print("tolerance: " + ignore)
                _LOGGER.debug('%s: tolerance added: %s',
                              device_list[zone_entry][0], tolerance)
        
            entity_id = DOMAIN + '.' + proximity_zone
            proximity_zone = 'zone.' + proximity_zone

            state = hass.states.get(proximity_zone)
            zone_friendly_name = (state.name).lower()

            # set the default values
            dist_to_zone = 'not set'
            dir_of_travel = 'not set'
            nearest = 'not set'

            proximity = Proximity(hass, zone_friendly_name, dist_to_zone,
                                  dir_of_travel, nearest, ignored_zones,
                                  proximity_devices, tolerance, proximity_zone)
            proximity.entity_id = entity_id

            proximity.update_ha_state()

    # main command to monitor proximity of devices
    track_state_change(hass, master_device_list,
                       proximity.check_proximity_state_change)

    # Tells the bootstrapper that the component was successfully initialized
    return True

#******************** UPDATES MADE UP TO HERE ***********************

class Proximity(Entity):  # pylint: disable=too-many-instance-attributes
    """ Represents a Proximity in Home Assistant. """
    def __init__(self, hass, zone_friendly_name, dist_to, dir_of_travel,
                 nearest, ignored_zones, proximity_devices, tolerance,
                 proximity_zone):
        # pylint: disable=too-many-arguments
        self.hass = hass
        self.friendly_name = zone_friendly_name
        self.dist_to = dist_to
        self.dir_of_travel = dir_of_travel
        self.nearest = nearest
        self.ignored_zones = ignored_zones
        self.proximity_devices = proximity_devices
        self.tolerance = tolerance
        self.proximity_zone = proximity_zone

    @property
    def state(self):
        return self.dist_to

    @property
    def unit_of_measurement(self):
        """ Unit of measurement of this entity """
        return "km"

    @property
    def state_attributes(self):
        return {
            ATTR_DIR_OF_TRAVEL: self.dir_of_travel,
            ATTR_NEAREST: self.nearest,
            ATTR_FRIENDLY_NAME: self.friendly_name
        }

    def check_proximity_state_change(self, entity, old_state, new_state):
        # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        """ Function to perform the proximity checking """
        entity_name = new_state.name
        devices_to_calculate = False
        devices_in_zone = ''

        zone_state = self.hass.states.get(self.proximity_zone)
        proximity_latitude = zone_state.attributes.get('latitude')
        proximity_longitude = zone_state.attributes.get('longitude')

        # check for devices in the monitored zone
        for device in self.proximity_devices:
            device_state = self.hass.states.get(device)
            
            if 'latitude' not in device_state.attributes:
                continue

            device_state_lat = device_state.attributes['latitude']
            device_state_lon = device_state.attributes['longitude']

            for ignored_zone in self.ignored_zones:
                ignored_zone_state = self.hass.states.get('zone.' +
                                                          ignored_zone)
                if not zone.in_zone(ignored_zone_state,
                                    device_state_lat,
                                    device_state_lon):
                    devices_to_calculate = True

            # check the location of all devices
            if zone.in_zone(zone_state,
                            device_state_lat,
                            device_state_lon):
                device_friendly = device_state.name
                if devices_in_zone != '':
                    devices_in_zone = devices_in_zone + ', '
                devices_in_zone = devices_in_zone + device_friendly

        # no-one to track so reset the entity
        if not devices_to_calculate:
            self.dist_to = 'not set'
            self.dir_of_travel = 'not set'
            self.nearest = 'not set'
            self.update_ha_state()
            return

        # at least one device is in the monitored zone so update the entity
        if devices_in_zone != '':
            self.dist_to = 0
            self.dir_of_travel = 'arrived'
            self.nearest = devices_in_zone
            self.update_ha_state()
            return

        # we can't check proximity because latitude and longitude don't exist
        if 'latitude' not in new_state.attributes:
            return

        # collect distances to the zone for all devices
        distances_to_zone = {}
        for device in self.proximity_devices:
            # ignore devices in an ignored zone
            device_state = self.hass.states.get(device)

            # ignore devices if proximity cannot be calculated
            if 'latitude' not in device_state.attributes:
                continue

            device_state_lat = device_state.attributes['latitude']
            device_state_lon = device_state.attributes['longitude']

            device_in_ignored_zone = False
            for ignored_zone in self.ignored_zones:
                ignored_zone_state = self.hass.states.get('zone.' +
                                                          ignored_zone)
                if zone.in_zone(ignored_zone_state,
                                device_state_lat,
                                device_state_lon):
                    device_in_ignored_zone = True
                    continue
            if device_in_ignored_zone:
                continue

            # calculate the distance to the proximity zone
            dist_to_zone = distance(proximity_latitude,
                                    proximity_longitude,
                                    device_state_lat,
                                    device_state_lon)

            # add the device and distance to a dictionary
            distances_to_zone[device] = round(dist_to_zone / 1000, 1)

        # loop through each of the distances collected and work out the closest
        closest_device = ''
        dist_to_zone = 1000000

        for device in distances_to_zone:
            if distances_to_zone[device] < dist_to_zone:
                closest_device = device
                dist_to_zone = distances_to_zone[device]

        # if the closest device is one of the other devices
        if closest_device != entity:
            self.dist_to = round(distances_to_zone[closest_device])
            self.dir_of_travel = 'unknown'
            device_state = self.hass.states.get(closest_device)
            self.nearest = device_state.name
            self.update_ha_state()
            return

        # stop if we cannot calculate the direction of travel (i.e. we don't
        # have a previous state and a current LAT and LONG)
        if old_state is None or 'latitude' not in old_state.attributes:
            self.dist_to = round(distances_to_zone[entity])
            self.dir_of_travel = 'unknown'
            self.nearest = entity_name
            self.update_ha_state()
            return

        # reset the variables
        distance_travelled = 0

        # calculate the distance travelled
        old_distance = distance(proximity_latitude, proximity_longitude,
                                old_state.attributes['latitude'],
                                old_state.attributes['longitude'])
        new_distance = distance(proximity_latitude, proximity_longitude,
                                new_state.attributes['latitude'],
                                new_state.attributes['longitude'])
        distance_travelled = round(new_distance - old_distance, 1)

        # check for tolerance
        if distance_travelled < self.tolerance * -1:
            direction_of_travel = 'towards'
        elif distance_travelled > self.tolerance:
            direction_of_travel = 'away_from'
        else:
            direction_of_travel = 'stationary'

        # update the proximity entity
        self.dist_to = round(dist_to_zone)
        self.dir_of_travel = direction_of_travel
        self.nearest = entity_name
        self.update_ha_state()
        _LOGGER.debug('proximity.%s update entity: distance=%s: direction=%s: '
                      'device=%s', self.friendly_name, round(dist_to_zone),
                      direction_of_travel, entity_name)

        _LOGGER.info('%s: proximity calculation complete', entity_name)
