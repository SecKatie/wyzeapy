import logging
from enum import Enum
from typing import Any, Dict, List

from .base_service import BaseService
from ..types import Device, IrrigationProps, DeviceTypes

_LOGGER = logging.getLogger(__name__)


class CropType(Enum):
    COOL_SEASON_GRASS = "cool_season_grass"
    WARM_SEASON_GRASS = "warm_season_grass"
    SHRUBS = "shrubs"
    TREES = "trees"
    ANNUALS = "annuals"
    PERENNIALS = "perennials"
    XERISCAPE = "xeriscape"
    GARDEN = "garden"


class ExposureType(Enum):  # auto, on
    LOTS_OF_SUN = "lots_of_sun"
    SOME_SHADE = "some_shade"


class NozzleType(Enum):
    FIXED_SPRAY_HEAD = "fixed_spray_head"
    ROTOR_HEAD = "rotor_head"
    ROTARY_NOZZLE = "rotary_nozzle"
    MISTER = "mister"
    BUBBLER = "bubbler"
    EMITTER = "emitter"
    DRIP_LINE = "drip_line"


class SlopeType(Enum):
    FLAT = "flat"
    SLIGHT = "slight"
    MODERATE = "moderate"
    STEEP = "steep"


class SoilType(Enum):
    CLAY_LOAM = 'clay_loam'
    CLAY = 'clay'
    SILTY_CLAY = 'silty_clay'
    LOAM = 'loam'
    SANDY_LOAM = 'sandy_loam'
    LOAMY_SAND = 'loamy_sand'
    SAND = 'sand'


class Zone:
    """Represents a single irrigation zone."""
    def __init__(self, dictionary: Dict[Any, Any]):
        self.zone_number: int = dictionary.get('zone_number', 1)
        self.name: str = dictionary.get('name', 'Zone 1')
        self.enabled: bool = dictionary.get('enabled', True)
        self.zone_id: str = dictionary.get('zone_id', 'zone_id')
        self.smart_duration: int = dictionary.get('smart_duration', 600)
        self.quickrun_duration: int = dictionary.get('quickrun_duration', 600)  # Default to 10 minutes
        #self.device_id: str = "device_id"
        #self.did_uid: str = "did_uid"
        #self.latest_events = latest_events[]
        #self.schedules = schedules[]
        #self.zone_disable_reason: null
        #self.camera_device_id: null
        #self.garden_subtypes: null
        #self.manual_crop_coefficient: null
        #self.manual_root_depth: null
        #self.number_of_sprinkler_heads: null
        #self.photo_url: null
        #self.smart_schedule_id: null
        #self.tree_subtypes: null
        #self.area: float = 500.0
        #self.available_water_capacity: float = 0.2
        #self.crop_coefficient: float = 0.8
        #self.crop_type: CropType = CropType.COOL_SEASON_GRASS
        #self.efficiency: float = 80.0
        #self.exposure_type: ExposureType = ExposureType.LOTS_OF_SUN
        #self.flow_rate: float = 1.5
        #self.manage_allow_depletion: float = 50.0
        #self.nozzle_type: NozzleType = NozzleType.FIXED_SPRAY_HEAD
        #self.root_depth: float = 6.0
        #self.slope_type: SlopeType = SlopeType.FLAT
        #self.soil_moisture_level_at_end_of_day_pct: float = 0.5
        #self.soil_type: SoilType = SoilType.CLAY_LOAM
        #self.updated: int = 1715919469326
        #self.user_id: str = "user_id"
        #self.wired: bool = True


class Irrigation(Device):
    def __init__(self, dictionary: Dict[Any, Any]):
        super().__init__(dictionary)

        #self.wiring
        #self.sensor
        #self.notification_enable
        #self.notification_watering_begins
        #self.notification_watering_ends
        #self.notification_watering_is_skipped
        #self.offline_schedule
        #self.quickrun_durations
        # the below comes from the get_iot_prop call
        self.RSSI: int = 0
        self.IP: str = "192.168.1.100"
        self.sn: str = "SN123456789"
        self.available: bool = False
        self.ssid: str = "ssid"
        # the below comes from the device_info call
        #self.enable_schedules: bool = False
        #self.skip_low_temp: int = 32
        #self.skip_wind: int = 20
        #self.skip_rain: float = 0.125
        #self.skip_saturation: int = 100
        #self.exit_setup_zonetest: int = 0
        #self.exit_setup_schedule: int = 0
        #self.setup_step: int = 2
        # the zones for the device go here
        self.zones: List[Zone] = []


class IrrigationService(BaseService):
    async def update(self, irrigation: Irrigation) -> Irrigation:
        """Update the irrigation device with latest data from Wyze API."""
        # Get IoT properties
        properties = (await self.get_iot_prop(irrigation))['data']['props']
        
        # Update device properties
        irrigation.RSSI = properties.get('rssi', -65)
        irrigation.IP = properties.get('ip', '192.168.1.100')
        irrigation.sn = properties.get('sn', 'SN123456789')
        irrigation.ssid = properties.get('ssid', 'ssid')
        irrigation.available = (properties.get(IrrigationProps.IOT_STATE.value) == "connected")

        # Get zones
        zones = (await self.get_zone_by_device(irrigation))['data']['zones']
        
        # Update zones
        irrigation.zones = []
        for zone in zones:
            irrigation.zones.append(Zone(zone))
        
        return irrigation
    
    async def update_device_props(self, irrigation: Irrigation) -> Irrigation:
        """Update the irrigation device with latest data from Wyze API."""
        # Get IoT properties
        properties = (await self.get_iot_prop(irrigation))['data']['props']
        
        # Update device properties
        irrigation.RSSI = properties.get('rssi')
        irrigation.IP = properties.get('ip')
        irrigation.sn = properties.get('sn')
        irrigation.ssid = properties.get('ssid')
        irrigation.available = (properties.get(IrrigationProps.IOT_STATE.value) == 'connected')

        return irrigation

    async def get_irrigations(self) -> List[Irrigation]:
        if self._devices is None:
            self._devices = await self.get_object_list()

        irrigations = [device for device in self._devices if device.type is DeviceTypes.IRRIGATION and "BS_WK1" in device.product_model]

        return [Irrigation(irrigation.raw_dict) for irrigation in irrigations]

    async def start_zone(self, irrigation: Device, zone_number: int, quickrun_duration: int) -> Dict[Any, Any]:
        """Start a zone with the specified duration.
        
        Args:
            irrigation: The irrigation device
            zone_number: The zone number to start
            quickrun_duration: Duration in seconds to run the zone
            
        Returns:
            Dict containing the API response
        """
        url = "https://wyze-lockwood-service.wyzecam.com/plugin/irrigation/quickrun"
        return await self._start_zone(irrigation, url, zone_number, quickrun_duration)

    async def stop_running_schedule(self, device: Device) -> Dict[Any, Any]:
        """Stop any currently running irrigation schedule.
        
        Args:
            device: The irrigation device
            
        Returns:
            Dict containing the API response
        """
        url = "https://wyze-lockwood-service.wyzecam.com/plugin/irrigation/runningschedule"
        action = "STOP"    
        return await self._stop_running_schedule(url, device, action)

    async def set_zone_quickrun_duration(self, irrigation: Irrigation, zone_number: int, duration: int) -> None:
        """Set the quickrun duration for a specific zone.
        
        Args:
            irrigation: The irrigation device
            zone_number: The zone number to configure
            duration: Duration in seconds for quickrun
        """
        for zone in irrigation.zones:
            if zone.zone_number == zone_number:
                zone.quickrun_duration = duration
                break

    # Private implementation methods
    async def get_iot_prop(self, device: Device) -> Dict[Any, Any]:
        """Get IoT properties for a device."""
        url = "https://wyze-lockwood-service.wyzecam.com/plugin/irrigation/get_iot_prop"
        keys = 'zone_state,iot_state,iot_state_update_time,app_version,RSSI,' \
            'wifi_mac,sn,device_model,ssid,IP'
        return await self._get_iot_prop(url, device, keys)

    async def get_device_info(self, device: Device) -> Dict[Any, Any]:
        """Get device info from Wyze API."""
        url = "https://wyze-lockwood-service.wyzecam.com/plugin/irrigation/device_info"
        keys = 'wiring,sensor,enable_schedules,notification_enable,notification_watering_begins,' \
            'notification_watering_ends,notification_watering_is_skipped,skip_low_temp,skip_wind,' \
            'skip_rain,skip_saturation'
        return await self._irrigation_device_info(url, device, keys)

    async def get_zone_by_device(self, device: Device) -> List[Dict[Any, Any]]:
        """Get zones for a device."""
        url = "https://wyze-lockwood-service.wyzecam.com/plugin/irrigation/zone"
        return await self._get_zone_by_device(url, device)
