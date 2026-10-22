import logging
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Union

from .base_service import BaseService
from ..const import VENUS_APP_ID, VENUS_SIGNING_SECRET, VENUS_URL
from ..types import Device, DeviceTypes, VacuumProps

_LOGGER = logging.getLogger(__name__)

VACUUM_KEYS = (
    "iot_state,battary,mode,chargeState,cleanSize,cleanTime,fault_type,fault_code,"
    "current_mapid,count,cleanlevel,notice_save_map,memory_map_update_time,"
    "filter,side_brush,main_brush"
)


class VacuumMode(Enum):
    """The vacuum's reported activity.

    Wyze reports a raw integer whose meaning is per-attachment: the same activity
    carries a different code for the vacuum, mop and 2-in-1 heads, which is why
    each member holds a list rather than a single code.
    """

    IDLE = ("Idle", [0, 14, 29, 35, 40])
    CLEANING = ("Cleaning", [1, 30, 1101, 1201, 1301, 1401])
    SWEEPING = ("Sweeping", [7, 25, 36])
    PAUSED = ("Paused", [4, 9, 27, 31, 37, 1102, 1202, 1302, 1402])
    BREAK_POINT = ("Break point", [39])
    RETURNING_TO_CHARGE = ("Returning to charge", [5])
    FINISHED_RETURNING_TO_CHARGE = (
        "Cleaning completed, returning to charge",
        [10, 12, 26, 32, 38, 1103, 1203, 1303, 1403],
    )
    DOCKED_NOT_COMPLETE = (
        "Cleaning will resume after charging",
        [11, 33, 1104, 1204, 1304, 1404],
    )
    MAPPING = ("Mapping", [45])
    MAPPING_PAUSED = ("Mapping paused", [46])
    MAPPING_FINISHED_RETURNING_TO_CHARGE = (
        "Mapping completed, returning to charge",
        [47],
    )
    MAPPING_DOCKED_NOT_COMPLETE = ("Mapping will resume after charging", [48])
    UNKNOWN = ("Unknown", [])

    def __init__(self, description: str, codes: Sequence[int]):
        self.description = description
        self.codes = list(codes)

    @classmethod
    def parse(cls, code: Union[str, int, None]) -> "VacuumMode":
        try:
            code = int(code)
        except (TypeError, ValueError):
            return cls.UNKNOWN

        for mode in cls:
            if code in mode.codes:
                return mode
        return cls.UNKNOWN


class VacuumFaultCode(Enum):
    """The faults the vacuum firmware reports.

    `fault_code` carries status as well as faults: a healthy vacuum publishes
    codes in the 2100s that track charge and dock state. Membership of this set
    is what identifies a fault, not a non-zero value.
    """

    RADAR_OUT_OF_TIME = ("Lidar sensor blocked", 500)
    WHEEL_LIFT_UP = ("Vacuum not on ground", 501)
    DUST_BOX_NO_EXIST = ("Dustbin not installed", 503)
    RELOCATE_FAILED = ("Relocation failed", 507)
    SLOPE_START = ("Vacuum not on flat ground", 508)
    COLLISION_EXCEPTION = ("Vacuum stuck", 510)
    GO_CHARGE_FAILED = ("Failed to return to the charging station", 511)
    STOP_POINT_GO_CHARGE_FAILED = ("Failed to return to the charging station", 512)
    NAVIGATION_FAILED = ("Mapping failed", 513)
    GET_OUT_OF_TROUBLE_FAILED = ("Wheels stuck", 514)
    ROBOT_NO_WATER = ("Water tank not installed", 521)
    ROBOT_NO_MOP = ("Mop not installed", 522)
    ROBOT_NO_DUSTANDWATER_MOP = ("Water tank and mop not installed", 529)
    ROBOT_NO_DUSTANDWATER_HURRI = (
        "2-in-1 dustbin with water tank and mop not installed",
        530,
    )
    ROBOT_NO_WATER_HURRI = ("2-in-1 dustbin with water tank not installed", 531)
    ROBOT_IN_VIRTUALWALL = ("Vacuum stuck in no-go zone", 567)

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code

    @classmethod
    def parse(cls, code: Union[str, int, None]) -> Optional["VacuumFaultCode"]:
        try:
            code = int(code)
        except (TypeError, ValueError):
            return None

        for fault in cls:
            if code == fault.code:
                return fault
        return None


class VacuumSuctionLevel(Enum):
    QUIET = ("Quiet", 1)
    STANDARD = ("Standard", 2)
    STRONG = ("Strong", 3)

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code

    @classmethod
    def parse(cls, value: Union["VacuumSuctionLevel", str, int, None]):
        if isinstance(value, cls):
            return value
        for level in cls:
            if value == level.code or value == level.description:
                return level
        return None


class VacuumControlType(Enum):
    GLOBAL_SWEEPING = 0
    RETURN_TO_CHARGING = 3
    AREA_CLEAN = 6
    QUICK_MAPPING = 7


class VacuumControlValue(Enum):
    STOP = 0
    START = 1
    PAUSE = 2
    FALSE_PAUSE = 3


# The suction level is preference slot 1 on the venus set_preference command.
SUCTION_LEVEL_CONTROL_TYPE = 1


class Vacuum(Device):
    def __init__(self, dictionary: Dict[Any, Any]):
        super().__init__(dictionary)

        self.available: bool = False
        self.mode: VacuumMode = VacuumMode.UNKNOWN
        self.battery: Optional[int] = None
        self.charging: bool = False
        self.clean_size: Optional[int] = None
        self.clean_time: Optional[int] = None
        self.suction_level: Optional[VacuumSuctionLevel] = None
        self.fault_code: Optional[int] = None
        self.fault: Optional[VacuumFaultCode] = None
        self.current_map_id: Optional[int] = None
        self.filter_remaining: Optional[int] = None
        self.side_brush_remaining: Optional[int] = None
        self.main_brush_remaining: Optional[int] = None


class VacuumService(BaseService):
    async def update(self, vacuum: Vacuum) -> Vacuum:
        """Refresh the vacuum from the venus service.

        Absent keys leave the existing value alone: venus omits a prop it has no
        value for rather than sending a null, so treating absence as a reset
        would blank the state on every partial response.
        """
        properties = (await self._vacuum_get_iot_prop(vacuum))["data"]["props"]

        for key, value in properties.items():
            try:
                prop = VacuumProps(key)
            except ValueError as err:
                _LOGGER.debug(f"{err} with value {value}")
                continue

            if prop == VacuumProps.IOT_STATE:
                # `iot_state` tracks commandability, not readability. A sleeping
                # JA_RO2 reports "disconnected" while the cloud still answers a
                # read with a full prop set, but venus refuses every command with
                # code 3000 "Device is offline" until it reconnects.
                vacuum.available = value == "connected"
            elif prop == VacuumProps.MODE:
                vacuum.mode = VacuumMode.parse(value)
            elif prop == VacuumProps.BATTERY:
                vacuum.battery = self._parse_int(value)
            elif prop == VacuumProps.CHARGE_STATE:
                vacuum.charging = self._parse_int(value) == 1
            elif prop == VacuumProps.CLEAN_SIZE:
                vacuum.clean_size = self._parse_int(value)
            elif prop == VacuumProps.CLEAN_TIME:
                vacuum.clean_time = self._parse_int(value)
            elif prop == VacuumProps.CLEAN_LEVEL:
                vacuum.suction_level = VacuumSuctionLevel.parse(self._parse_int(value))
            elif prop == VacuumProps.FAULT_CODE:
                vacuum.fault_code = self._parse_int(value)
                vacuum.fault = VacuumFaultCode.parse(value)
            elif prop == VacuumProps.CURRENT_MAP_ID:
                vacuum.current_map_id = self._parse_int(value)
            elif prop == VacuumProps.FILTER:
                vacuum.filter_remaining = self._parse_int(value)
            elif prop == VacuumProps.SIDE_BRUSH:
                vacuum.side_brush_remaining = self._parse_int(value)
            elif prop == VacuumProps.MAIN_BRUSH:
                vacuum.main_brush_remaining = self._parse_int(value)

        return vacuum

    async def get_vacuums(self) -> List[Vacuum]:
        if self._devices is None:
            self._devices = await self.get_object_list()

        return [
            Vacuum(device.raw_dict)
            for device in self._devices
            if device.type is DeviceTypes.VACUUM
        ]

    async def sweep(self, vacuum: Vacuum) -> None:
        """Start a whole-home clean, or resume a paused one."""
        await self._venus_control(
            vacuum,
            VacuumControlType.GLOBAL_SWEEPING.value,
            VacuumControlValue.START.value,
        )

    async def sweep_rooms(
        self, vacuum: Vacuum, rooms: Union[int, Sequence[int]]
    ) -> None:
        """Clean only the named rooms of the current map.

        Room ids come from `get_rooms` and are only meaningful against the map
        that was current when they were read.
        """
        if isinstance(rooms, int):
            rooms = [rooms]
        rooms = list(rooms)
        if not rooms:
            # Venus reads an absent room list as a whole-home clean, so an empty
            # selection would quietly do far more than the caller asked.
            raise ValueError("sweep_rooms requires at least one room id")

        await self._venus_control(
            vacuum,
            VacuumControlType.GLOBAL_SWEEPING.value,
            VacuumControlValue.START.value,
            rooms=rooms,
        )

    async def get_rooms(self, vacuum: Vacuum) -> Dict[str, int]:
        """Return {room name: room id} for the vacuum's current map."""
        maps = (await self._venus_get_maps(vacuum)).get("data") or []
        current = next((m for m in maps if m.get("current_map")), None)
        if current is None:
            return {}

        return {
            room["room_name"]: room["room_id"]
            for room in current.get("room_info_list") or []
        }

    async def get_last_clean(self, vacuum: Vacuum) -> Optional[Dict[str, Any]]:
        """Return the most recent cleaning record, or None if there is no history."""
        response = await self._venus_get_sweep_records(vacuum, limit=1)
        records = ((response.get("data") or {}).get("data")) or []
        return records[0] if records else None

    async def pause(self, vacuum: Vacuum) -> None:
        await self._venus_control(
            vacuum,
            VacuumControlType.GLOBAL_SWEEPING.value,
            VacuumControlValue.PAUSE.value,
        )

    async def return_to_charge(self, vacuum: Vacuum) -> None:
        await self._venus_control(
            vacuum,
            VacuumControlType.RETURN_TO_CHARGING.value,
            VacuumControlValue.START.value,
        )

    async def stop(self, vacuum: Vacuum) -> None:
        """Cancel a return-to-charge, leaving the vacuum where it stands."""
        await self._venus_control(
            vacuum,
            VacuumControlType.RETURN_TO_CHARGING.value,
            VacuumControlValue.STOP.value,
        )

    async def set_suction_level(
        self, vacuum: Vacuum, suction_level: Union[VacuumSuctionLevel, str, int]
    ) -> None:
        level = VacuumSuctionLevel.parse(suction_level)
        if level is None:
            raise ValueError(f"Unknown suction level: {suction_level}")

        await self._venus_set_iot_action(
            vacuum,
            "set_preference",
            {"ctrltype": SUCTION_LEVEL_CONTROL_TYPE, "value": level.code},
        )

    async def _vacuum_get_iot_prop(self, device: Device) -> Dict[Any, Any]:
        return await self._get_iot_prop(
            f"{VENUS_URL}/plugin/venus/get_iot_prop",
            device,
            VACUUM_KEYS,
            app_id=VENUS_APP_ID,
            signing_secret=VENUS_SIGNING_SECRET,
        )

    async def _venus_control(
        self,
        device: Device,
        control_type: int,
        value: int,
        rooms: Optional[Sequence[int]] = None,
    ) -> Dict[Any, Any]:
        payload = {"type": control_type, "value": value, "vacuumMopMode": 0}
        if rooms is not None:
            payload["rooms_id"] = list(rooms)
        return await self._venus_post(
            f"/plugin/venus/{device.mac}/control", payload
        )

    async def _venus_get_maps(self, device: Device) -> Dict[Any, Any]:
        return await self._venus_get(
            "/plugin/venus/memory_map/list", {"did": device.mac}
        )

    async def _venus_get_sweep_records(
        self, device: Device, limit: int
    ) -> Dict[Any, Any]:
        return await self._venus_get(
            "/plugin/venus/sweep_record/query_data",
            {
                "did": device.mac,
                "purpose": "history_map",
                "count": limit,
                "last_time": int(time.time() * 1000),
            },
        )

    async def _venus_set_iot_action(
        self, device: Device, cmd: str, params: Dict[str, Any]
    ) -> Dict[Any, Any]:
        return await self._venus_post(
            "/plugin/venus/set_iot_action",
            {
                "cmd": cmd,
                "did": device.mac,
                "model": device.product_model,
                "is_sub_device": 0,
                "params": [params],
            },
        )

    @staticmethod
    def _parse_int(value: Any) -> Optional[int]:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
