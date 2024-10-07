#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  katie@mulliken.net to receive a copy
import time
from typing import Any, Dict

from .const import FORD_APP_KEY
from .crypto import ford_create_signature


def ford_create_payload(access_token: str, payload: Dict[str, Any],
                        url_path: str, request_method: str) -> Dict[str, Any]:
    payload["access_token"] = access_token
    payload["key"] = FORD_APP_KEY
    payload["timestamp"] = str(int(time.time() * 1000))
    payload["sign"] = ford_create_signature(url_path, request_method, payload)
    return payload


def olive_create_get_payload(device_mac: str, keys: str) -> Dict[str, Any]:
    nonce = int(time.time() * 1000)

    return {
        'keys': keys,
        'did': device_mac,
        'nonce': nonce
    }


def olive_create_post_payload(device_mac: str, device_model: str, prop_key: str, value: Any) -> Dict[str, Any]:
    nonce = int(time.time() * 1000)

    return {
        "did": device_mac,
        "model": device_model,
        "props": {
            prop_key: value
        },
        "is_sub_device": 0,
        "nonce": str(nonce)
    }


def olive_create_hms_payload() -> Dict[str, str]:
    nonce = int(time.time() * 1000)

    return {
        "group_id": "hms",
        "nonce": str(nonce)
    }


def olive_create_user_info_payload() -> Dict[str, str]:
    nonce = int(time.time() * 1000)

    return {
        "nonce": str(nonce)
    }


def olive_create_hms_get_payload(hms_id: str) -> Dict[str, str]:
    nonce = int(time.time() * 1000)
    return {
        "hms_id": hms_id,
        "nonce": str(nonce)
    }


def olive_create_hms_patch_payload(hms_id: str) -> Dict[str, Any]:
    return {
        "hms_id": hms_id
    }


def devicemgmt_create_capabilities_payload(type: str, value: str):
    match type:
        case "floodlight":
            return {
                "iid": 4,
                "name": "floodlight",
                "properties": [
                    {
                        "prop": "on",
                        "value": value
                    }
                ]
            }
        case "spotlight":
            return {
                "iid": 5,
                "name": "spotlight",
                "properties": [
                    {
                        "prop": "on",
                        "value": value
                    }
                ]
            }
        case "power":
            return {
                "functions": [
                    {
                        "in": {
                            "wakeup-live-view": "1"
                        },
                        "name": value
                    }
                ],
                "iid": 1,
                "name": "iot-device"
            }
        case "siren":
            return {
                "functions": [
                    {
                        "in": {},
                        "name": value
                    }
                ],
                "name": "siren"
            }
        case _:
            raise NotImplementedError(f"No action of type ({type}) has been implemented.")


def devicemgmt_get_iot_props_list(model: str):
    match model:
        case "LD_CFP": # Floodlight Pro
            return [
                {
                    "iid": 2,
                    "name": "camera",
                    "properties": [
                        "motion-detect",
                        "resolution",
                        "bit-rate",
                        "live-stream-mode",
                        "recording-mode",
                        "frame-rate",
                        "night-shot",
                        "night-shot-state",
                        "rotate-angle",
                        "time-watermark",
                        "logo-watermark",
                        "recording-trigger-source",
                        "recording-content-type",
                        "motion-push",
                        "speaker",
                        "microphone",
                        "unusual-sound-push",
                        "flip",
                        "motion-detect-recording",
                        "cool-down-interval",
                        "infrared-mode",
                        "sound-collection-on",
                        "live-stream-protocol",
                        "ai-push",
                        "voice-template",
                        "motion-category"
                    ]
                },
                {
                    "iid": 3,
                    "name": "device-info",
                    "properties": [
                        "device-id",
                        "device-model",
                        "firmware-ver",
                        "mac",
                        "timezone",
                        "lat",
                        "ip",
                        "lon",
                        "hardware-ver",
                        "public-ip"
                    ]
                },
                {
                    "iid": 1,
                    "name": "iot-device",
                    "properties": [
                        "iot-state",
                        "iot-power",
                        "push-switch"
                    ]
                },
                {
                    "iid": 9,
                    "name": "camera-ai",
                    "properties": [
                        "smart-detection-type",
                        "on"
                    ]
                },
                {
                    "iid": 4,
                    "name": "floodlight",
                    "properties": [
                        "on",
                        "enabled",
                        "mode",
                        "trigger-source",
                        "brightness",
                        "light-on-duration",
                        "voice-template",
                        "motion-warning-switch",
                        "motion-activate-light-switch",
                        "motion-activate-light-schedule",
                        "motion-activate-brightness",
                        "ambient-light-switch",
                        "ambient-light-schedule",
                        "ambient-light-brightness",
                        "motion-tag",
                        "light-model",
                        "flash-with-siren"
                    ]
                },
                {
                    "iid": 11,
                    "name": "indicator-light",
                    "properties": [
                        "on",
                        "mode",
                        "brightness",
                        "color",
                        "color-temperature"
                    ]
                },
                {
                    "iid": 8,
                    "name": "memory-card-management",
                    "properties": [
                        "storage-used-space",
                        "storage-total-space",
                        "storage-status",
                        "sd-card-playback-enabled"
                    ]
                },
                {
                    "iid": 6,
                    "name": "motion-detection",
                    "properties": [
                        "sensitivity-motion",
                        "on",
                        "motion-zone",
                        "motion-zone-selected-block",
                        "motion-zone-block-size",
                        "motion-tag",
                        "edge-detection-type",
                        "motion-warning-switch",
                        "motion-warning-tone",
                        "motion-warning-interval",
                        "motion-warning-schedule",
                        "motion-warning-sound",
                        "motion-warning-trigger-setting"
                    ]
                },
                {
                    "iid": 7,
                    "name": "siren",
                    "properties": [
                        "state"
                    ]
                },
                {
                    "iid": 5,
                    "name": "wifi",
                    "properties": [
                        "on",
                        "signal-strength",
                        "wifi-ssid",
                        "wifi-encrypted-password"
                    ]
                }
            ]
        case "AN_RSCW": # Battery Cam pro
            return [
                {
                    "iid": 2,
                    "name": "camera",
                    "properties": [
                        "motion-detect",
                        "resolution",
                        "bit-rate",
                        "live-stream-mode",
                        "recording-mode",
                        "frame-rate",
                        "night-shot",
                        "night-shot-state",
                        "time-watermark",
                        "logo-watermark",
                        "cool-down-interval",
                        "recording-content-type",
                        "video-length-limit",
                        "motion-push",
                        "speaker",
                        "unusual-sound-push",
                        "microphone",
                        "infrared-mode",
                        "motion-detect-recording",
                        "live-stream-protocol",
                        "recording-resolution",
                        "recording-start-time",
                        "recording-schedule-duration",
                        "voice-template",
                        "rotate-angle",
                        "sound-collection-on",
                        "ai-push"
                    ]
                },
                {
                    "iid": 3,
                    "name": "device-info",
                    "properties": [
                        "device-id",
                        "device-model",
                        "firmware-ver",
                        "mac",
                        "timezone",
                        "lat",
                        "ip",
                        "lon",
                        "company-code",
                        "device-setting-channel",
                        "network-connection-mode",
                        "hardware-ver",
                        "public-ip"
                    ]
                },
                {
                    "iid": 1,
                    "name": "iot-device",
                    "properties": [
                        "iot-state",
                        "iot-power",
                        "push-switch",
                        "mqtt-check"
                    ]
                },
                {
                    "iid": 7,
                    "name": "battery",
                    "properties": [
                        "battery-level",
                        "low-battery-push",
                        "power-source",
                        "charging-status",
                        "power-saving"
                    ]
                },
                {
                    "iid": 12,
                    "name": "camera-ai",
                    "properties": [
                        "smart-detection-type",
                        "on"
                    ]
                },
                {
                    "iid": 8,
                    "name": "indicator-light",
                    "properties": [
                        "on",
                        "mode"
                    ]
                },
                {
                    "iid": 6,
                    "name": "memory-card-management",
                    "properties": [
                        "storage-used-space",
                        "storage-total-space",
                        "storage-status",
                        "sd-card-playback-enabled"
                    ]
                },
                {
                    "iid": 11,
                    "name": "motion-detection",
                    "properties": [
                        "sensitivity-motion",
                        "on",
                        "area-length",
                        "motion-zone",
                        "motion-zone-block-size",
                        "motion-zone-selected-block",
                        "edge-detection-type",
                        "motion-tag"
                    ]
                },
                {
                    "iid": 4,
                    "name": "siren",
                    "properties": [
                        "state",
                        "siren-on-ts"
                    ]
                },
                {
                    "iid": 14,
                    "name": "solar-panel",
                    "properties": [
                        "enabled",
                        "on"
                    ]
                },
                {
                    "iid": 5,
                    "name": "spotlight",
                    "properties": [
                        "on",
                        "enabled",
                        "brightness",
                        "motion-activate-light-switch",
                        "sunset-to-sunrise",
                        "motion-activate-light-schedule",
                        "trigger-source"
                    ]
                },
                {
                    "iid": 9,
                    "name": "wifi",
                    "properties": [
                        "on",
                        "signal-strength",
                        "wifi-ssid",
                        "wifi-encrypted-password"
                    ]
                }
            ]
        case "GW_GC1": # OG
            return [
                {
                    "iid": 2,
                    "name": "camera",
                    "properties": [
                        "motion-detect",
                        "resolution",
                        "bit-rate",
                        "live-stream-mode",
                        "recording-mode",
                        "frame-rate",
                        "night-shot",
                        "night-shot-state",
                        "time-watermark",
                        "logo-watermark",
                        "cool-down-interval",
                        "recording-content-type",
                        "video-length-limit",
                        "motion-push",
                        "speaker",
                        "unusual-sound-push",
                        "microphone",
                        "infrared-mode",
                        "motion-detect-recording",
                        "live-stream-protocol",
                        "recording-resolution",
                        "recording-start-time",
                        "recording-schedule-duration",
                        "voice-template",
                        "rotate-angle",
                        "sound-collection-on",
                        "ai-push"
                    ]
                },
                {
                    "iid": 3,
                    "name": "device-info",
                    "properties": [
                        "device-id",
                        "device-model",
                        "firmware-ver",
                        "mac",
                        "timezone",
                        "lat",
                        "ip",
                        "lon",
                        "company-code",
                        "device-setting-channel",
                        "network-connection-mode",
                        "hardware-ver",
                        "public-ip"
                    ]
                },
                {
                    "iid": 1,
                    "name": "iot-device",
                    "properties": [
                        "iot-state",
                        "iot-power",
                        "push-switch",
                        "mqtt-check"
                    ]
                },
                {
                    "iid": 12,
                    "name": "camera-ai",
                    "properties": [
                        "smart-detection-type",
                        "on"
                    ]
                },
                {
                    "iid": 8,
                    "name": "indicator-light",
                    "properties": [
                        "on",
                        "mode"
                    ]
                },
                {
                    "iid": 6,
                    "name": "memory-card-management",
                    "properties": [
                        "storage-used-space",
                        "storage-total-space",
                        "storage-status",
                        "sd-card-playback-enabled"
                    ]
                },
                {
                    "iid": 11,
                    "name": "motion-detection",
                    "properties": [
                        "sensitivity-motion",
                        "on",
                        "area-length",
                        "motion-zone",
                        "motion-zone-block-size",
                        "motion-zone-selected-block",
                        "edge-detection-type",
                        "motion-tag"
                    ]
                },
                {
                    "iid": 4,
                    "name": "siren",
                    "properties": [
                        "state",
                        "siren-on-ts"
                    ]
                },
                {
                    "iid": 5,
                    "name": "spotlight",
                    "properties": [
                        "on",
                        "enabled",
                        "brightness",
                        "motion-activate-light-switch",
                        "sunset-to-sunrise",
                        "motion-activate-light-schedule",
                        "trigger-source"
                    ]
                },
                {
                    "iid": 9,
                    "name": "wifi",
                    "properties": [
                        "on",
                        "signal-strength",
                        "wifi-ssid",
                        "wifi-encrypted-password"
                    ]
                }
            ]
        case _:
            raise NotImplementedError(f"No iot props for model ({model}) have been defined.")