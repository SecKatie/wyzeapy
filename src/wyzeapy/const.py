"""Constants for Wyzeapy."""

# =============================================================================
# API Server URLs
# =============================================================================

AUTH_SERVER = "https://auth-prod.api.wyze.com"
MAIN_API_SERVER = "https://api.wyzecam.com"
APP_API_SERVER = "https://app.wyzecam.com"
LOCK_API_SERVER = "https://yd-saas-toc.wyzecam.com"
PLATFORM_SERVICE_URL = "https://wyze-platform-service.wyzecam.com"
DEVICEMGMT_SERVICE_URL = "https://devicemgmt-service-beta.wyze.com"


# =============================================================================
# App Constants
# =============================================================================

PHONE_SYSTEM_TYPE = "1"
APP_VERSION = "2.18.43"
APP_VER = "com.hualai.WyzeCam___2.18.43"
APP_NAME = "com.hualai.WyzeCam"
SC = "9f275790cab94a72bd206c8876429f3c"
SV = "9d74946e652647e9b6c9d59326aef104"
APP_INFO = "wyze_android_2.19.14"


# =============================================================================
# API Keys and Secrets
# =============================================================================

# Ford (Lock API) credentials
FORD_APP_KEY = "275965684684dbdaf29a0ed9"
FORD_APP_SECRET = "4deekof1ba311c5c33a9cb8e12787e8c"

# Olive (Platform Service) credentials
OLIVE_SIGNING_SECRET = "wyze_app_secret_key_132"
OLIVE_APP_ID = "9319141212m2ik"


# =============================================================================
# Device Property IDs
# =============================================================================


class PropertyID:
    """Common property IDs for Wyze devices."""

    # General
    POWER: str = "P3"  # Power on/off

    # Lighting
    BRIGHTNESS: str = "P1501"
    COLOR_TEMP: str = "P1502"
    COLOR: str = "P1507"
    COLOR_MODE: str = "P1508"  # 1=color, 2=white

    # Lock
    DOOR_OPEN: str = "P2001"

    # Camera
    CAMERA_SIREN: str = "P1049"
    MOTION_DETECTION: str = "P1047"  # Motion detection state
    MOTION_DETECTION_TOGGLE: str = "P1001"  # Toggle motion detection on/off
    ACCESSORY: str = "P1056"  # Camera accessories (floodlight, lamp socket, etc.)


# =============================================================================
# Camera Model Lists
# =============================================================================

# Camera models that use the newer devicemgmt API
DEVICEMGMT_API_MODELS = [
    "LD_CFP",   # Floodlight Pro
    "AN_RSCW",  # Battery Cam Pro
    "GW_GC1",   # OG
]

# Product models known to have floodlight/spotlight capability
FLOODLIGHT_MODELS = [
    "LD_CFP",   # Floodlight Pro
    "AN_RSCW",  # Battery Cam Pro (has spotlight)
    "HL_CFL2",  # Floodlight v2
]

# Product models with lamp socket accessory support
LAMP_SOCKET_MODELS = [
    "HL_LAMP",  # Lamp Socket
]
