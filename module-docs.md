---
description: |
    API documentation for modules: wyzeapy, wyzeapy.const, wyzeapy.crypto, wyzeapy.exceptions, wyzeapy.payload_factory, wyzeapy.services, wyzeapy.services.base_service, wyzeapy.services.bulb_service, wyzeapy.services.camera_service, wyzeapy.services.hms_service, wyzeapy.services.lock_service, wyzeapy.services.sensor_service, wyzeapy.services.switch_service, wyzeapy.services.thermostat_service, wyzeapy.types, wyzeapy.utils, wyzeapy.wyze_auth_lib.

lang: en

classoption: oneside
geometry: margin=1in
papersize: a4

linkcolor: blue
links-as-notes: true
...


    
# Module `wyzeapy` {#wyzeapy}




    
## Sub-modules

* [wyzeapy.const](#wyzeapy.const)
* [wyzeapy.crypto](#wyzeapy.crypto)
* [wyzeapy.exceptions](#wyzeapy.exceptions)
* [wyzeapy.payload_factory](#wyzeapy.payload_factory)
* [wyzeapy.services](#wyzeapy.services)
* [wyzeapy.types](#wyzeapy.types)
* [wyzeapy.utils](#wyzeapy.utils)
* [wyzeapy.wyze_auth_lib](#wyzeapy.wyze_auth_lib)




    
## Classes


    
### Class `Wyzeapy` {#wyzeapy.Wyzeapy}




>     class Wyzeapy


A module to assist developers in interacting with the Wyze service





    
#### Instance variables


    
##### Variable `bulb_service` {#wyzeapy.Wyzeapy.bulb_service}



Type: `wyzeapy.services.bulb_service.BulbService`



    
##### Variable `camera_service` {#wyzeapy.Wyzeapy.camera_service}



Type: `wyzeapy.services.camera_service.CameraService`



    
##### Variable `hms_service` {#wyzeapy.Wyzeapy.hms_service}



Type: `wyzeapy.services.hms_service.HMSService`



    
##### Variable `lock_service` {#wyzeapy.Wyzeapy.lock_service}



Type: `wyzeapy.services.lock_service.LockService`



    
##### Variable `notifications_are_on` {#wyzeapy.Wyzeapy.notifications_are_on}



Type: `bool`



    
##### Variable `sensor_service` {#wyzeapy.Wyzeapy.sensor_service}



Type: `wyzeapy.services.sensor_service.SensorService`



    
##### Variable `switch_service` {#wyzeapy.Wyzeapy.switch_service}



Type: `wyzeapy.services.switch_service.SwitchService`



    
##### Variable `thermostat_service` {#wyzeapy.Wyzeapy.thermostat_service}



Type: `wyzeapy.services.thermostat_service.ThermostatService`



    
##### Variable `unique_device_ids` {#wyzeapy.Wyzeapy.unique_device_ids}



Type: `Set[str]`




    
#### Static methods


    
##### `Method create` {#wyzeapy.Wyzeapy.create}




>     async def create()


Creates the Wyzeapy class

:return: An instance of the Wyzeapy class

    
##### `Method valid_login` {#wyzeapy.Wyzeapy.valid_login}




>     async def valid_login(
>         email: str,
>         password: str
>     ) ‑> bool





    
#### Methods


    
##### Method `async_close` {#wyzeapy.Wyzeapy.async_close}




>     async def async_close(
>         self
>     )




    
##### Method `disable_notifications` {#wyzeapy.Wyzeapy.disable_notifications}




>     async def disable_notifications(
>         self
>     )




    
##### Method `enable_notifications` {#wyzeapy.Wyzeapy.enable_notifications}




>     async def enable_notifications(
>         self
>     )




    
##### Method `login` {#wyzeapy.Wyzeapy.login}




>     async def login(
>         self,
>         email,
>         password
>     )






    
# Module `wyzeapy.const` {#wyzeapy.const}









    
# Module `wyzeapy.crypto` {#wyzeapy.crypto}






    
## Functions


    
### Function `ford_create_signature` {#wyzeapy.crypto.ford_create_signature}




>     def ford_create_signature(
>         url_path: str,
>         request_method: str,
>         payload: Dict[Any, Any]
>     ) ‑> str




    
### Function `olive_create_signature` {#wyzeapy.crypto.olive_create_signature}




>     def olive_create_signature(
>         payload: Union[Dict[Any, Any], str],
>         access_token: str
>     ) ‑> str







    
# Module `wyzeapy.exceptions` {#wyzeapy.exceptions}







    
## Classes


    
### Class `AccessTokenError` {#wyzeapy.exceptions.AccessTokenError}




>     class AccessTokenError(
>         *args,
>         **kwargs
>     )


Common base class for all non-exit exceptions.


    
#### Ancestors (in MRO)

* [builtins.Exception](#builtins.Exception)
* [builtins.BaseException](#builtins.BaseException)






    
### Class `ActionNotSupported` {#wyzeapy.exceptions.ActionNotSupported}




>     class ActionNotSupported(
>         device_type: str
>     )


Common base class for all non-exit exceptions.


    
#### Ancestors (in MRO)

* [builtins.Exception](#builtins.Exception)
* [builtins.BaseException](#builtins.BaseException)






    
### Class `LoginError` {#wyzeapy.exceptions.LoginError}




>     class LoginError(
>         *args,
>         **kwargs
>     )


Common base class for all non-exit exceptions.


    
#### Ancestors (in MRO)

* [builtins.Exception](#builtins.Exception)
* [builtins.BaseException](#builtins.BaseException)






    
### Class `ParameterError` {#wyzeapy.exceptions.ParameterError}




>     class ParameterError(
>         *args,
>         **kwargs
>     )


Common base class for all non-exit exceptions.


    
#### Ancestors (in MRO)

* [builtins.Exception](#builtins.Exception)
* [builtins.BaseException](#builtins.BaseException)






    
### Class `UnknownApiError` {#wyzeapy.exceptions.UnknownApiError}




>     class UnknownApiError(
>         response_json: Dict[str, Any]
>     )


Common base class for all non-exit exceptions.


    
#### Ancestors (in MRO)

* [builtins.Exception](#builtins.Exception)
* [builtins.BaseException](#builtins.BaseException)








    
# Module `wyzeapy.payload_factory` {#wyzeapy.payload_factory}






    
## Functions


    
### Function `ford_create_payload` {#wyzeapy.payload_factory.ford_create_payload}




>     def ford_create_payload(
>         access_token: str,
>         payload: Dict[str, Any],
>         url_path: str,
>         request_method: str
>     ) ‑> Dict[str, Any]




    
### Function `olive_create_get_payload` {#wyzeapy.payload_factory.olive_create_get_payload}




>     def olive_create_get_payload(
>         device_mac: str
>     ) ‑> Dict[str, Any]




    
### Function `olive_create_hms_get_payload` {#wyzeapy.payload_factory.olive_create_hms_get_payload}




>     def olive_create_hms_get_payload(
>         hms_id: str
>     ) ‑> Dict[str, str]




    
### Function `olive_create_hms_patch_payload` {#wyzeapy.payload_factory.olive_create_hms_patch_payload}




>     def olive_create_hms_patch_payload(
>         hms_id: str
>     ) ‑> Dict[str, Any]




    
### Function `olive_create_hms_payload` {#wyzeapy.payload_factory.olive_create_hms_payload}




>     def olive_create_hms_payload() ‑> Dict[str, str]




    
### Function `olive_create_post_payload` {#wyzeapy.payload_factory.olive_create_post_payload}




>     def olive_create_post_payload(
>         device_mac: str,
>         device_model: str,
>         prop: wyzeapy.types.ThermostatProps,
>         value: Any
>     ) ‑> Dict[str, Any]




    
### Function `olive_create_user_info_payload` {#wyzeapy.payload_factory.olive_create_user_info_payload}




>     def olive_create_user_info_payload() ‑> Dict[str, str]







    
# Module `wyzeapy.services` {#wyzeapy.services}

This package provides all the services to the system


    
## Sub-modules

* [wyzeapy.services.base_service](#wyzeapy.services.base_service)
* [wyzeapy.services.bulb_service](#wyzeapy.services.bulb_service)
* [wyzeapy.services.camera_service](#wyzeapy.services.camera_service)
* [wyzeapy.services.hms_service](#wyzeapy.services.hms_service)
* [wyzeapy.services.lock_service](#wyzeapy.services.lock_service)
* [wyzeapy.services.sensor_service](#wyzeapy.services.sensor_service)
* [wyzeapy.services.switch_service](#wyzeapy.services.switch_service)
* [wyzeapy.services.thermostat_service](#wyzeapy.services.thermostat_service)






    
# Module `wyzeapy.services.base_service` {#wyzeapy.services.base_service}







    
## Classes


    
### Class `BaseService` {#wyzeapy.services.base_service.BaseService}




>     class BaseService(
>         auth_lib: wyzeapy.wyze_auth_lib.WyzeAuthLib
>     )






    
#### Descendants

* [wyzeapy.services.bulb_service.BulbService](#wyzeapy.services.bulb_service.BulbService)
* [wyzeapy.services.camera_service.CameraService](#wyzeapy.services.camera_service.CameraService)
* [wyzeapy.services.hms_service.HMSService](#wyzeapy.services.hms_service.HMSService)
* [wyzeapy.services.lock_service.LockService](#wyzeapy.services.lock_service.LockService)
* [wyzeapy.services.sensor_service.SensorService](#wyzeapy.services.sensor_service.SensorService)
* [wyzeapy.services.switch_service.SwitchService](#wyzeapy.services.switch_service.SwitchService)
* [wyzeapy.services.thermostat_service.ThermostatService](#wyzeapy.services.thermostat_service.ThermostatService)





    
#### Methods


    
##### Method `get_object_list` {#wyzeapy.services.base_service.BaseService.get_object_list}




>     async def get_object_list(
>         self
>     ) ‑> List[wyzeapy.types.Device]


Wraps the api.wyzecam.com/app/v2/home_page/get_object_list endpoint

:return: List of devices

    
##### Method `get_user_profile` {#wyzeapy.services.base_service.BaseService.get_user_profile}




>     async def get_user_profile(
>         self
>     ) ‑> Dict[Any, Any]




    
##### Method `set_push_info` {#wyzeapy.services.base_service.BaseService.set_push_info}




>     async def set_push_info(
>         self,
>         on: bool
>     ) ‑> NoneType






    
# Module `wyzeapy.services.bulb_service` {#wyzeapy.services.bulb_service}







    
## Classes


    
### Class `Bulb` {#wyzeapy.services.bulb_service.Bulb}




>     class Bulb(
>         dictionary: Dict[Any, Any]
>     )





    
#### Ancestors (in MRO)

* [wyzeapy.types.Device](#wyzeapy.types.Device)



    
#### Class variables


    
##### Variable `on` {#wyzeapy.services.bulb_service.Bulb.on}



Type: `bool`




    
#### Instance variables


    
##### Variable `brightness` {#wyzeapy.services.bulb_service.Bulb.brightness}



Type: `int`



    
##### Variable `color` {#wyzeapy.services.bulb_service.Bulb.color}



Type: `Optional[str]`



    
##### Variable `color_temp` {#wyzeapy.services.bulb_service.Bulb.color_temp}



Type: `int`





    
### Class `BulbService` {#wyzeapy.services.bulb_service.BulbService}




>     class BulbService(
>         auth_lib: wyzeapy.wyze_auth_lib.WyzeAuthLib
>     )





    
#### Ancestors (in MRO)

* [wyzeapy.services.base_service.BaseService](#wyzeapy.services.base_service.BaseService)






    
#### Methods


    
##### Method `get_bulbs` {#wyzeapy.services.bulb_service.BulbService.get_bulbs}




>     async def get_bulbs(
>         self
>     ) ‑> List[wyzeapy.services.bulb_service.Bulb]




    
##### Method `set_brightness` {#wyzeapy.services.bulb_service.BulbService.set_brightness}




>     async def set_brightness(
>         self,
>         bulb: wyzeapy.types.Device,
>         brightness: int
>     )




    
##### Method `set_color` {#wyzeapy.services.bulb_service.BulbService.set_color}




>     async def set_color(
>         self,
>         bulb: wyzeapy.services.bulb_service.Bulb,
>         color: str
>     )




    
##### Method `set_color_temp` {#wyzeapy.services.bulb_service.BulbService.set_color_temp}




>     async def set_color_temp(
>         self,
>         bulb: wyzeapy.services.bulb_service.Bulb,
>         color_temp: int
>     )




    
##### Method `turn_off` {#wyzeapy.services.bulb_service.BulbService.turn_off}




>     async def turn_off(
>         self,
>         bulb: wyzeapy.services.bulb_service.Bulb
>     )




    
##### Method `turn_on` {#wyzeapy.services.bulb_service.BulbService.turn_on}




>     async def turn_on(
>         self,
>         bulb: wyzeapy.services.bulb_service.Bulb,
>         options=None
>     )




    
##### Method `update` {#wyzeapy.services.bulb_service.BulbService.update}




>     async def update(
>         self,
>         bulb: wyzeapy.services.bulb_service.Bulb
>     ) ‑> wyzeapy.services.bulb_service.Bulb






    
# Module `wyzeapy.services.camera_service` {#wyzeapy.services.camera_service}







    
## Classes


    
### Class `Camera` {#wyzeapy.services.camera_service.Camera}




>     class Camera(
>         dictionary: Dict[Any, Any]
>     )





    
#### Ancestors (in MRO)

* [wyzeapy.types.Device](#wyzeapy.types.Device)



    
#### Class variables


    
##### Variable `device_params` {#wyzeapy.services.camera_service.Camera.device_params}



Type: `Dict[str, Any]`



    
##### Variable `mac` {#wyzeapy.services.camera_service.Camera.mac}



Type: `str`



    
##### Variable `nickname` {#wyzeapy.services.camera_service.Camera.nickname}



Type: `str`



    
##### Variable `product_model` {#wyzeapy.services.camera_service.Camera.product_model}



Type: `str`



    
##### Variable `product_type` {#wyzeapy.services.camera_service.Camera.product_type}



Type: `str`



    
##### Variable `raw_dict` {#wyzeapy.services.camera_service.Camera.raw_dict}



Type: `Dict[str, Any]`






    
### Class `CameraService` {#wyzeapy.services.camera_service.CameraService}




>     class CameraService(
>         auth_lib: wyzeapy.wyze_auth_lib.WyzeAuthLib
>     )





    
#### Ancestors (in MRO)

* [wyzeapy.services.base_service.BaseService](#wyzeapy.services.base_service.BaseService)






    
#### Methods


    
##### Method `get_cameras` {#wyzeapy.services.camera_service.CameraService.get_cameras}




>     async def get_cameras(
>         self
>     ) ‑> List[wyzeapy.services.camera_service.Camera]




    
##### Method `register_for_updates` {#wyzeapy.services.camera_service.CameraService.register_for_updates}




>     async def register_for_updates(
>         self,
>         camera: wyzeapy.services.camera_service.Camera,
>         callback: Callable[[wyzeapy.services.camera_service.Camera], NoneType]
>     )




    
##### Method `turn_off` {#wyzeapy.services.camera_service.CameraService.turn_off}




>     async def turn_off(
>         self,
>         camera: wyzeapy.services.camera_service.Camera
>     )




    
##### Method `turn_off_notifications` {#wyzeapy.services.camera_service.CameraService.turn_off_notifications}




>     async def turn_off_notifications(
>         self,
>         camera: wyzeapy.services.camera_service.Camera
>     )




    
##### Method `turn_on` {#wyzeapy.services.camera_service.CameraService.turn_on}




>     async def turn_on(
>         self,
>         camera: wyzeapy.services.camera_service.Camera
>     )




    
##### Method `turn_on_notifications` {#wyzeapy.services.camera_service.CameraService.turn_on_notifications}




>     async def turn_on_notifications(
>         self,
>         camera: wyzeapy.services.camera_service.Camera
>     )




    
##### Method `update` {#wyzeapy.services.camera_service.CameraService.update}




>     async def update(
>         self,
>         camera: wyzeapy.services.camera_service.Camera
>     )




    
##### Method `update_worker` {#wyzeapy.services.camera_service.CameraService.update_worker}




>     def update_worker(
>         self,
>         loop
>     )






    
# Module `wyzeapy.services.hms_service` {#wyzeapy.services.hms_service}







    
## Classes


    
### Class `HMSMode` {#wyzeapy.services.hms_service.HMSMode}




>     class HMSMode(
>         value,
>         names=None,
>         *,
>         module=None,
>         qualname=None,
>         type=None,
>         start=1
>     )


An enumeration.


    
#### Ancestors (in MRO)

* [enum.Enum](#enum.Enum)



    
#### Class variables


    
##### Variable `AWAY` {#wyzeapy.services.hms_service.HMSMode.AWAY}






    
##### Variable `CHANGING` {#wyzeapy.services.hms_service.HMSMode.CHANGING}






    
##### Variable `DISARMED` {#wyzeapy.services.hms_service.HMSMode.DISARMED}






    
##### Variable `HOME` {#wyzeapy.services.hms_service.HMSMode.HOME}









    
### Class `HMSService` {#wyzeapy.services.hms_service.HMSService}




>     class HMSService(
>         auth_lib: wyzeapy.wyze_auth_lib.WyzeAuthLib
>     )





    
#### Ancestors (in MRO)

* [wyzeapy.services.base_service.BaseService](#wyzeapy.services.base_service.BaseService)




    
#### Instance variables


    
##### Variable `has_hms` {#wyzeapy.services.hms_service.HMSService.has_hms}






    
##### Variable `hms_id` {#wyzeapy.services.hms_service.HMSService.hms_id}



Type: `Optional[str]`




    
#### Static methods


    
##### `Method create` {#wyzeapy.services.hms_service.HMSService.create}




>     async def create(
>         auth_lib: wyzeapy.wyze_auth_lib.WyzeAuthLib
>     )





    
#### Methods


    
##### Method `set_mode` {#wyzeapy.services.hms_service.HMSService.set_mode}




>     async def set_mode(
>         self,
>         mode: wyzeapy.services.hms_service.HMSMode
>     )




    
##### Method `update` {#wyzeapy.services.hms_service.HMSService.update}




>     async def update(
>         self,
>         hms_id: str
>     )






    
# Module `wyzeapy.services.lock_service` {#wyzeapy.services.lock_service}







    
## Classes


    
### Class `Lock` {#wyzeapy.services.lock_service.Lock}




>     class Lock(
>         dictionary: Dict[Any, Any]
>     )





    
#### Ancestors (in MRO)

* [wyzeapy.types.Device](#wyzeapy.types.Device)



    
#### Class variables


    
##### Variable `device_params` {#wyzeapy.services.lock_service.Lock.device_params}



Type: `Dict[str, Any]`



    
##### Variable `door_open` {#wyzeapy.services.lock_service.Lock.door_open}






    
##### Variable `mac` {#wyzeapy.services.lock_service.Lock.mac}



Type: `str`



    
##### Variable `nickname` {#wyzeapy.services.lock_service.Lock.nickname}



Type: `str`



    
##### Variable `product_model` {#wyzeapy.services.lock_service.Lock.product_model}



Type: `str`



    
##### Variable `product_type` {#wyzeapy.services.lock_service.Lock.product_type}



Type: `str`



    
##### Variable `raw_dict` {#wyzeapy.services.lock_service.Lock.raw_dict}



Type: `Dict[str, Any]`



    
##### Variable `unlocked` {#wyzeapy.services.lock_service.Lock.unlocked}









    
### Class `LockService` {#wyzeapy.services.lock_service.LockService}




>     class LockService(
>         auth_lib: wyzeapy.wyze_auth_lib.WyzeAuthLib
>     )





    
#### Ancestors (in MRO)

* [wyzeapy.services.base_service.BaseService](#wyzeapy.services.base_service.BaseService)






    
#### Methods


    
##### Method `get_locks` {#wyzeapy.services.lock_service.LockService.get_locks}




>     async def get_locks(
>         self
>     )




    
##### Method `lock` {#wyzeapy.services.lock_service.LockService.lock}




>     async def lock(
>         self,
>         lock: wyzeapy.services.lock_service.Lock
>     )




    
##### Method `unlock` {#wyzeapy.services.lock_service.LockService.unlock}




>     async def unlock(
>         self,
>         lock: wyzeapy.services.lock_service.Lock
>     )




    
##### Method `update` {#wyzeapy.services.lock_service.LockService.update}




>     async def update(
>         self,
>         lock: wyzeapy.services.lock_service.Lock
>     )






    
# Module `wyzeapy.services.sensor_service` {#wyzeapy.services.sensor_service}







    
## Classes


    
### Class `Sensor` {#wyzeapy.services.sensor_service.Sensor}




>     class Sensor(
>         dictionary: Dict[Any, Any]
>     )





    
#### Ancestors (in MRO)

* [wyzeapy.types.Device](#wyzeapy.types.Device)



    
#### Class variables


    
##### Variable `detected` {#wyzeapy.services.sensor_service.Sensor.detected}



Type: `bool`






    
### Class `SensorService` {#wyzeapy.services.sensor_service.SensorService}




>     class SensorService(
>         auth_lib: wyzeapy.wyze_auth_lib.WyzeAuthLib
>     )





    
#### Ancestors (in MRO)

* [wyzeapy.services.base_service.BaseService](#wyzeapy.services.base_service.BaseService)






    
#### Methods


    
##### Method `get_sensors` {#wyzeapy.services.sensor_service.SensorService.get_sensors}




>     async def get_sensors(
>         self
>     ) ‑> List[wyzeapy.services.sensor_service.Sensor]




    
##### Method `register_for_updates` {#wyzeapy.services.sensor_service.SensorService.register_for_updates}




>     async def register_for_updates(
>         self,
>         sensor: wyzeapy.services.sensor_service.Sensor,
>         callback: Callable[[wyzeapy.services.sensor_service.Sensor], NoneType]
>     )




    
##### Method `update` {#wyzeapy.services.sensor_service.SensorService.update}




>     async def update(
>         self,
>         sensor: wyzeapy.services.sensor_service.Sensor
>     ) ‑> wyzeapy.services.sensor_service.Sensor




    
##### Method `update_worker` {#wyzeapy.services.sensor_service.SensorService.update_worker}




>     def update_worker(
>         self,
>         loop
>     )






    
# Module `wyzeapy.services.switch_service` {#wyzeapy.services.switch_service}







    
## Classes


    
### Class `Switch` {#wyzeapy.services.switch_service.Switch}




>     class Switch(
>         dictionary: Dict[Any, Any]
>     )





    
#### Ancestors (in MRO)

* [wyzeapy.types.Device](#wyzeapy.types.Device)



    
#### Class variables


    
##### Variable `device_params` {#wyzeapy.services.switch_service.Switch.device_params}



Type: `Dict[str, Any]`



    
##### Variable `mac` {#wyzeapy.services.switch_service.Switch.mac}



Type: `str`



    
##### Variable `nickname` {#wyzeapy.services.switch_service.Switch.nickname}



Type: `str`



    
##### Variable `product_model` {#wyzeapy.services.switch_service.Switch.product_model}



Type: `str`



    
##### Variable `product_type` {#wyzeapy.services.switch_service.Switch.product_type}



Type: `str`



    
##### Variable `raw_dict` {#wyzeapy.services.switch_service.Switch.raw_dict}



Type: `Dict[str, Any]`






    
### Class `SwitchService` {#wyzeapy.services.switch_service.SwitchService}




>     class SwitchService(
>         auth_lib: wyzeapy.wyze_auth_lib.WyzeAuthLib
>     )





    
#### Ancestors (in MRO)

* [wyzeapy.services.base_service.BaseService](#wyzeapy.services.base_service.BaseService)






    
#### Methods


    
##### Method `get_switches` {#wyzeapy.services.switch_service.SwitchService.get_switches}




>     async def get_switches(
>         self
>     ) ‑> List[wyzeapy.services.switch_service.Switch]




    
##### Method `turn_off` {#wyzeapy.services.switch_service.SwitchService.turn_off}




>     async def turn_off(
>         self,
>         switch: wyzeapy.services.switch_service.Switch
>     )




    
##### Method `turn_on` {#wyzeapy.services.switch_service.SwitchService.turn_on}




>     async def turn_on(
>         self,
>         switch: wyzeapy.services.switch_service.Switch
>     )




    
##### Method `update` {#wyzeapy.services.switch_service.SwitchService.update}




>     async def update(
>         self,
>         switch: wyzeapy.services.switch_service.Switch
>     )






    
# Module `wyzeapy.services.thermostat_service` {#wyzeapy.services.thermostat_service}







    
## Classes


    
### Class `FanMode` {#wyzeapy.services.thermostat_service.FanMode}




>     class FanMode(
>         value,
>         names=None,
>         *,
>         module=None,
>         qualname=None,
>         type=None,
>         start=1
>     )


An enumeration.


    
#### Ancestors (in MRO)

* [enum.Enum](#enum.Enum)



    
#### Class variables


    
##### Variable `AUTO` {#wyzeapy.services.thermostat_service.FanMode.AUTO}






    
##### Variable `ON` {#wyzeapy.services.thermostat_service.FanMode.ON}









    
### Class `HVACMode` {#wyzeapy.services.thermostat_service.HVACMode}




>     class HVACMode(
>         value,
>         names=None,
>         *,
>         module=None,
>         qualname=None,
>         type=None,
>         start=1
>     )


An enumeration.


    
#### Ancestors (in MRO)

* [enum.Enum](#enum.Enum)



    
#### Class variables


    
##### Variable `AUTO` {#wyzeapy.services.thermostat_service.HVACMode.AUTO}






    
##### Variable `COOL` {#wyzeapy.services.thermostat_service.HVACMode.COOL}






    
##### Variable `HEAT` {#wyzeapy.services.thermostat_service.HVACMode.HEAT}






    
##### Variable `OFF` {#wyzeapy.services.thermostat_service.HVACMode.OFF}









    
### Class `HVACState` {#wyzeapy.services.thermostat_service.HVACState}




>     class HVACState(
>         value,
>         names=None,
>         *,
>         module=None,
>         qualname=None,
>         type=None,
>         start=1
>     )


An enumeration.


    
#### Ancestors (in MRO)

* [enum.Enum](#enum.Enum)



    
#### Class variables


    
##### Variable `COOLING` {#wyzeapy.services.thermostat_service.HVACState.COOLING}






    
##### Variable `HEATING` {#wyzeapy.services.thermostat_service.HVACState.HEATING}






    
##### Variable `IDLE` {#wyzeapy.services.thermostat_service.HVACState.IDLE}









    
### Class `Preset` {#wyzeapy.services.thermostat_service.Preset}




>     class Preset(
>         value,
>         names=None,
>         *,
>         module=None,
>         qualname=None,
>         type=None,
>         start=1
>     )


An enumeration.


    
#### Ancestors (in MRO)

* [enum.Enum](#enum.Enum)



    
#### Class variables


    
##### Variable `AWAY` {#wyzeapy.services.thermostat_service.Preset.AWAY}






    
##### Variable `HOME` {#wyzeapy.services.thermostat_service.Preset.HOME}






    
##### Variable `SLEEP` {#wyzeapy.services.thermostat_service.Preset.SLEEP}









    
### Class `TemperatureUnit` {#wyzeapy.services.thermostat_service.TemperatureUnit}




>     class TemperatureUnit(
>         value,
>         names=None,
>         *,
>         module=None,
>         qualname=None,
>         type=None,
>         start=1
>     )


An enumeration.


    
#### Ancestors (in MRO)

* [enum.Enum](#enum.Enum)



    
#### Class variables


    
##### Variable `CELSIUS` {#wyzeapy.services.thermostat_service.TemperatureUnit.CELSIUS}






    
##### Variable `FAHRENHEIT` {#wyzeapy.services.thermostat_service.TemperatureUnit.FAHRENHEIT}









    
### Class `Thermostat` {#wyzeapy.services.thermostat_service.Thermostat}




>     class Thermostat(
>         dictionary: Dict[Any, Any]
>     )





    
#### Ancestors (in MRO)

* [wyzeapy.types.Device](#wyzeapy.types.Device)



    
#### Class variables


    
##### Variable `device_params` {#wyzeapy.services.thermostat_service.Thermostat.device_params}



Type: `Dict[str, Any]`



    
##### Variable `mac` {#wyzeapy.services.thermostat_service.Thermostat.mac}



Type: `str`



    
##### Variable `nickname` {#wyzeapy.services.thermostat_service.Thermostat.nickname}



Type: `str`



    
##### Variable `product_model` {#wyzeapy.services.thermostat_service.Thermostat.product_model}



Type: `str`



    
##### Variable `product_type` {#wyzeapy.services.thermostat_service.Thermostat.product_type}



Type: `str`



    
##### Variable `raw_dict` {#wyzeapy.services.thermostat_service.Thermostat.raw_dict}



Type: `Dict[str, Any]`






    
### Class `ThermostatService` {#wyzeapy.services.thermostat_service.ThermostatService}




>     class ThermostatService(
>         auth_lib: wyzeapy.wyze_auth_lib.WyzeAuthLib
>     )





    
#### Ancestors (in MRO)

* [wyzeapy.services.base_service.BaseService](#wyzeapy.services.base_service.BaseService)






    
#### Methods


    
##### Method `get_thermostats` {#wyzeapy.services.thermostat_service.ThermostatService.get_thermostats}




>     async def get_thermostats(
>         self
>     ) ‑> List[wyzeapy.services.thermostat_service.Thermostat]




    
##### Method `set_cool_point` {#wyzeapy.services.thermostat_service.ThermostatService.set_cool_point}




>     async def set_cool_point(
>         self,
>         thermostat: wyzeapy.types.Device,
>         temp: int
>     )




    
##### Method `set_fan_mode` {#wyzeapy.services.thermostat_service.ThermostatService.set_fan_mode}




>     async def set_fan_mode(
>         self,
>         thermostat: wyzeapy.types.Device,
>         fan_mode: wyzeapy.services.thermostat_service.FanMode
>     )




    
##### Method `set_heat_point` {#wyzeapy.services.thermostat_service.ThermostatService.set_heat_point}




>     async def set_heat_point(
>         self,
>         thermostat: wyzeapy.types.Device,
>         temp: int
>     )




    
##### Method `set_hvac_mode` {#wyzeapy.services.thermostat_service.ThermostatService.set_hvac_mode}




>     async def set_hvac_mode(
>         self,
>         thermostat: wyzeapy.types.Device,
>         hvac_mode: wyzeapy.services.thermostat_service.HVACMode
>     )




    
##### Method `set_preset` {#wyzeapy.services.thermostat_service.ThermostatService.set_preset}




>     async def set_preset(
>         self,
>         thermostat: wyzeapy.services.thermostat_service.Thermostat,
>         preset: wyzeapy.services.thermostat_service.Preset
>     )




    
##### Method `update` {#wyzeapy.services.thermostat_service.ThermostatService.update}




>     async def update(
>         self,
>         thermostat: wyzeapy.services.thermostat_service.Thermostat
>     ) ‑> wyzeapy.services.thermostat_service.Thermostat






    
# Module `wyzeapy.types` {#wyzeapy.types}







    
## Classes


    
### Class `Device` {#wyzeapy.types.Device}




>     class Device(
>         dictionary: Dict[Any, Any]
>     )






    
#### Descendants

* [wyzeapy.services.bulb_service.Bulb](#wyzeapy.services.bulb_service.Bulb)
* [wyzeapy.services.camera_service.Camera](#wyzeapy.services.camera_service.Camera)
* [wyzeapy.services.lock_service.Lock](#wyzeapy.services.lock_service.Lock)
* [wyzeapy.services.sensor_service.Sensor](#wyzeapy.services.sensor_service.Sensor)
* [wyzeapy.services.switch_service.Switch](#wyzeapy.services.switch_service.Switch)
* [wyzeapy.services.thermostat_service.Thermostat](#wyzeapy.services.thermostat_service.Thermostat)
* [wyzeapy.types.Sensor](#wyzeapy.types.Sensor)


    
#### Class variables


    
##### Variable `device_params` {#wyzeapy.types.Device.device_params}



Type: `Dict[str, Any]`



    
##### Variable `mac` {#wyzeapy.types.Device.mac}



Type: `str`



    
##### Variable `nickname` {#wyzeapy.types.Device.nickname}



Type: `str`



    
##### Variable `product_model` {#wyzeapy.types.Device.product_model}



Type: `str`



    
##### Variable `product_type` {#wyzeapy.types.Device.product_type}



Type: `str`



    
##### Variable `raw_dict` {#wyzeapy.types.Device.raw_dict}



Type: `Dict[str, Any]`




    
#### Instance variables


    
##### Variable `type` {#wyzeapy.types.Device.type}



Type: `wyzeapy.types.DeviceTypes`





    
### Class `DeviceTypes` {#wyzeapy.types.DeviceTypes}




>     class DeviceTypes(
>         value,
>         names=None,
>         *,
>         module=None,
>         qualname=None,
>         type=None,
>         start=1
>     )


An enumeration.


    
#### Ancestors (in MRO)

* [enum.Enum](#enum.Enum)



    
#### Class variables


    
##### Variable `BASE_STATION` {#wyzeapy.types.DeviceTypes.BASE_STATION}






    
##### Variable `CAMERA` {#wyzeapy.types.DeviceTypes.CAMERA}






    
##### Variable `CHIME_SENSOR` {#wyzeapy.types.DeviceTypes.CHIME_SENSOR}






    
##### Variable `COMMON` {#wyzeapy.types.DeviceTypes.COMMON}






    
##### Variable `CONTACT_SENSOR` {#wyzeapy.types.DeviceTypes.CONTACT_SENSOR}






    
##### Variable `GATEWAY` {#wyzeapy.types.DeviceTypes.GATEWAY}






    
##### Variable `GATEWAY_V2` {#wyzeapy.types.DeviceTypes.GATEWAY_V2}






    
##### Variable `HEADPHONES` {#wyzeapy.types.DeviceTypes.HEADPHONES}






    
##### Variable `KEYPAD` {#wyzeapy.types.DeviceTypes.KEYPAD}






    
##### Variable `LIGHT` {#wyzeapy.types.DeviceTypes.LIGHT}






    
##### Variable `LOCK` {#wyzeapy.types.DeviceTypes.LOCK}






    
##### Variable `MESH_LIGHT` {#wyzeapy.types.DeviceTypes.MESH_LIGHT}






    
##### Variable `MOTION_SENSOR` {#wyzeapy.types.DeviceTypes.MOTION_SENSOR}






    
##### Variable `OUTDOOR_PLUG` {#wyzeapy.types.DeviceTypes.OUTDOOR_PLUG}






    
##### Variable `PLUG` {#wyzeapy.types.DeviceTypes.PLUG}






    
##### Variable `SCALE` {#wyzeapy.types.DeviceTypes.SCALE}






    
##### Variable `SENSE_V2_GATEWAY` {#wyzeapy.types.DeviceTypes.SENSE_V2_GATEWAY}






    
##### Variable `THERMOSTAT` {#wyzeapy.types.DeviceTypes.THERMOSTAT}






    
##### Variable `UNKNOWN` {#wyzeapy.types.DeviceTypes.UNKNOWN}






    
##### Variable `VACUUM` {#wyzeapy.types.DeviceTypes.VACUUM}






    
##### Variable `WRIST` {#wyzeapy.types.DeviceTypes.WRIST}









    
### Class `Event` {#wyzeapy.types.Event}




>     class Event(
>         dictionary: Dict[Any, Any]
>     )







    
#### Class variables


    
##### Variable `device_mac` {#wyzeapy.types.Event.device_mac}



Type: `str`



    
##### Variable `device_model` {#wyzeapy.types.Event.device_model}



Type: `str`



    
##### Variable `event_ack_result` {#wyzeapy.types.Event.event_ack_result}



Type: `int`



    
##### Variable `event_category` {#wyzeapy.types.Event.event_category}



Type: `int`



    
##### Variable `event_id` {#wyzeapy.types.Event.event_id}



Type: `str`



    
##### Variable `event_params` {#wyzeapy.types.Event.event_params}



Type: `Dict[Any, Any]`



    
##### Variable `event_ts` {#wyzeapy.types.Event.event_ts}



Type: `int`



    
##### Variable `event_value` {#wyzeapy.types.Event.event_value}



Type: `str`



    
##### Variable `file_list` {#wyzeapy.types.Event.file_list}



Type: `List[Dict[Any, Any]]`



    
##### Variable `is_feedback_correct` {#wyzeapy.types.Event.is_feedback_correct}



Type: `int`



    
##### Variable `is_feedback_face` {#wyzeapy.types.Event.is_feedback_face}



Type: `int`



    
##### Variable `is_feedback_person` {#wyzeapy.types.Event.is_feedback_person}



Type: `int`



    
##### Variable `read_state` {#wyzeapy.types.Event.read_state}



Type: `int`



    
##### Variable `recognized_instance_list` {#wyzeapy.types.Event.recognized_instance_list}



Type: `List[Any]`



    
##### Variable `tag_list` {#wyzeapy.types.Event.tag_list}



Type: `List[Any]`



    
##### Variable `typed_file_list` {#wyzeapy.types.Event.typed_file_list}



Type: `List[wyzeapy.types.File]`






    
### Class `File` {#wyzeapy.types.File}




>     class File(
>         dictionary: Dict[Any, Any]
>     )







    
#### Class variables


    
##### Variable `ai_tag_list` {#wyzeapy.types.File.ai_tag_list}



Type: `List[Any]`



    
##### Variable `ai_url` {#wyzeapy.types.File.ai_url}



Type: `str`



    
##### Variable `en_algorithm` {#wyzeapy.types.File.en_algorithm}



Type: `int`



    
##### Variable `en_password` {#wyzeapy.types.File.en_password}



Type: `str`



    
##### Variable `file_id` {#wyzeapy.types.File.file_id}



Type: `str`



    
##### Variable `file_params` {#wyzeapy.types.File.file_params}



Type: `Dict[Any, Any]`



    
##### Variable `is_ai` {#wyzeapy.types.File.is_ai}



Type: `int`



    
##### Variable `status` {#wyzeapy.types.File.status}



Type: `int`



    
##### Variable `type` {#wyzeapy.types.File.type}



Type: `Union[int, str]`



    
##### Variable `url` {#wyzeapy.types.File.url}



Type: `str`






    
### Class `Group` {#wyzeapy.types.Group}




>     class Group(
>         dictionary: Dict[Any, Any]
>     )







    
#### Class variables


    
##### Variable `group_id` {#wyzeapy.types.Group.group_id}



Type: `str`



    
##### Variable `group_name` {#wyzeapy.types.Group.group_name}



Type: `str`






    
### Class `HMSStatus` {#wyzeapy.types.HMSStatus}




>     class HMSStatus(
>         value,
>         names=None,
>         *,
>         module=None,
>         qualname=None,
>         type=None,
>         start=1
>     )


An enumeration.


    
#### Ancestors (in MRO)

* [enum.Enum](#enum.Enum)



    
#### Class variables


    
##### Variable `AWAY` {#wyzeapy.types.HMSStatus.AWAY}






    
##### Variable `DISARMED` {#wyzeapy.types.HMSStatus.DISARMED}






    
##### Variable `HOME` {#wyzeapy.types.HMSStatus.HOME}









    
### Class `PropertyIDs` {#wyzeapy.types.PropertyIDs}




>     class PropertyIDs(
>         value,
>         names=None,
>         *,
>         module=None,
>         qualname=None,
>         type=None,
>         start=1
>     )


An enumeration.


    
#### Ancestors (in MRO)

* [enum.Enum](#enum.Enum)



    
#### Class variables


    
##### Variable `AVAILABLE` {#wyzeapy.types.PropertyIDs.AVAILABLE}






    
##### Variable `BRIGHTNESS` {#wyzeapy.types.PropertyIDs.BRIGHTNESS}






    
##### Variable `COLOR` {#wyzeapy.types.PropertyIDs.COLOR}






    
##### Variable `COLOR_TEMP` {#wyzeapy.types.PropertyIDs.COLOR_TEMP}






    
##### Variable `CONTACT_STATE` {#wyzeapy.types.PropertyIDs.CONTACT_STATE}






    
##### Variable `DOOR_OPEN` {#wyzeapy.types.PropertyIDs.DOOR_OPEN}






    
##### Variable `MOTION_STATE` {#wyzeapy.types.PropertyIDs.MOTION_STATE}






    
##### Variable `NOTIFICATION` {#wyzeapy.types.PropertyIDs.NOTIFICATION}






    
##### Variable `ON` {#wyzeapy.types.PropertyIDs.ON}









    
### Class `ResponseCodes` {#wyzeapy.types.ResponseCodes}




>     class ResponseCodes(
>         value,
>         names=None,
>         *,
>         module=None,
>         qualname=None,
>         type=None,
>         start=1
>     )


An enumeration.


    
#### Ancestors (in MRO)

* [enum.Enum](#enum.Enum)



    
#### Class variables


    
##### Variable `ACCESS_TOKEN_ERROR` {#wyzeapy.types.ResponseCodes.ACCESS_TOKEN_ERROR}






    
##### Variable `DEVICE_OFFLINE` {#wyzeapy.types.ResponseCodes.DEVICE_OFFLINE}






    
##### Variable `PARAMETER_ERROR` {#wyzeapy.types.ResponseCodes.PARAMETER_ERROR}






    
##### Variable `SUCCESS` {#wyzeapy.types.ResponseCodes.SUCCESS}









    
### Class `ResponseCodesLock` {#wyzeapy.types.ResponseCodesLock}




>     class ResponseCodesLock(
>         value,
>         names=None,
>         *,
>         module=None,
>         qualname=None,
>         type=None,
>         start=1
>     )


An enumeration.


    
#### Ancestors (in MRO)

* [enum.Enum](#enum.Enum)



    
#### Class variables


    
##### Variable `SUCCESS` {#wyzeapy.types.ResponseCodesLock.SUCCESS}









    
### Class `Sensor` {#wyzeapy.types.Sensor}




>     class Sensor(
>         dictionary: Dict[Any, Any]
>     )





    
#### Ancestors (in MRO)

* [wyzeapy.types.Device](#wyzeapy.types.Device)



    
#### Class variables


    
##### Variable `device_params` {#wyzeapy.types.Sensor.device_params}



Type: `Dict[str, Any]`



    
##### Variable `mac` {#wyzeapy.types.Sensor.mac}



Type: `str`



    
##### Variable `nickname` {#wyzeapy.types.Sensor.nickname}



Type: `str`



    
##### Variable `product_model` {#wyzeapy.types.Sensor.product_model}



Type: `str`



    
##### Variable `product_type` {#wyzeapy.types.Sensor.product_type}



Type: `str`



    
##### Variable `raw_dict` {#wyzeapy.types.Sensor.raw_dict}



Type: `Dict[str, Any]`




    
#### Instance variables


    
##### Variable `activity_detected` {#wyzeapy.types.Sensor.activity_detected}



Type: `int`



    
##### Variable `is_low_battery` {#wyzeapy.types.Sensor.is_low_battery}



Type: `int`





    
### Class `ThermostatProps` {#wyzeapy.types.ThermostatProps}




>     class ThermostatProps(
>         value,
>         names=None,
>         *,
>         module=None,
>         qualname=None,
>         type=None,
>         start=1
>     )


An enumeration.


    
#### Ancestors (in MRO)

* [enum.Enum](#enum.Enum)



    
#### Class variables


    
##### Variable `APP_VERSION` {#wyzeapy.types.ThermostatProps.APP_VERSION}






    
##### Variable `ASW_HOLD` {#wyzeapy.types.ThermostatProps.ASW_HOLD}






    
##### Variable `CALIBRATE_HUMIDITY` {#wyzeapy.types.ThermostatProps.CALIBRATE_HUMIDITY}






    
##### Variable `CALIBRATE_TEMPERATURE` {#wyzeapy.types.ThermostatProps.CALIBRATE_TEMPERATURE}






    
##### Variable `CONFIG_SCENARIO` {#wyzeapy.types.ThermostatProps.CONFIG_SCENARIO}






    
##### Variable `COOL_SP` {#wyzeapy.types.ThermostatProps.COOL_SP}






    
##### Variable `CURRENT_SCENARIO` {#wyzeapy.types.ThermostatProps.CURRENT_SCENARIO}






    
##### Variable `DEV_HOLD` {#wyzeapy.types.ThermostatProps.DEV_HOLD}






    
##### Variable `EMHEAT` {#wyzeapy.types.ThermostatProps.EMHEAT}






    
##### Variable `FANCIRC_TIME` {#wyzeapy.types.ThermostatProps.FANCIRC_TIME}






    
##### Variable `FAN_MODE` {#wyzeapy.types.ThermostatProps.FAN_MODE}






    
##### Variable `HEAT_SP` {#wyzeapy.types.ThermostatProps.HEAT_SP}






    
##### Variable `HUMIDITY` {#wyzeapy.types.ThermostatProps.HUMIDITY}






    
##### Variable `IOT_STATE` {#wyzeapy.types.ThermostatProps.IOT_STATE}






    
##### Variable `KID_LOCK` {#wyzeapy.types.ThermostatProps.KID_LOCK}






    
##### Variable `MODE_SYS` {#wyzeapy.types.ThermostatProps.MODE_SYS}






    
##### Variable `PROTECT_TIME` {#wyzeapy.types.ThermostatProps.PROTECT_TIME}






    
##### Variable `QUERY_SCHEDULE` {#wyzeapy.types.ThermostatProps.QUERY_SCHEDULE}






    
##### Variable `SAVE_COMFORT_BALANCE` {#wyzeapy.types.ThermostatProps.SAVE_COMFORT_BALANCE}






    
##### Variable `SETUP_STATE` {#wyzeapy.types.ThermostatProps.SETUP_STATE}






    
##### Variable `TEMPERATURE` {#wyzeapy.types.ThermostatProps.TEMPERATURE}






    
##### Variable `TEMP_UNIT` {#wyzeapy.types.ThermostatProps.TEMP_UNIT}






    
##### Variable `TIME2TEMP_VAL` {#wyzeapy.types.ThermostatProps.TIME2TEMP_VAL}






    
##### Variable `WIRING_LOGIC_ID` {#wyzeapy.types.ThermostatProps.WIRING_LOGIC_ID}






    
##### Variable `WORKING_STATE` {#wyzeapy.types.ThermostatProps.WORKING_STATE}






    
##### Variable `W_CITY_ID` {#wyzeapy.types.ThermostatProps.W_CITY_ID}






    
##### Variable `W_LAT` {#wyzeapy.types.ThermostatProps.W_LAT}






    
##### Variable `W_LON` {#wyzeapy.types.ThermostatProps.W_LON}











    
# Module `wyzeapy.utils` {#wyzeapy.utils}






    
## Functions


    
### Function `check_for_errors_hms` {#wyzeapy.utils.check_for_errors_hms}




>     def check_for_errors_hms(
>         response_json: Dict[Any, Any]
>     ) ‑> NoneType




    
### Function `check_for_errors_lock` {#wyzeapy.utils.check_for_errors_lock}




>     def check_for_errors_lock(
>         response_json: Dict[str, Any]
>     ) ‑> NoneType




    
### Function `check_for_errors_standard` {#wyzeapy.utils.check_for_errors_standard}




>     def check_for_errors_standard(
>         response_json: Dict[str, Any]
>     ) ‑> NoneType




    
### Function `check_for_errors_thermostat` {#wyzeapy.utils.check_for_errors_thermostat}




>     def check_for_errors_thermostat(
>         response_json: Dict[Any, Any]
>     ) ‑> NoneType




    
### Function `create_password` {#wyzeapy.utils.create_password}




>     def create_password(
>         password: str
>     ) ‑> str




    
### Function `create_pid_pair` {#wyzeapy.utils.create_pid_pair}




>     def create_pid_pair(
>         pid_enum: wyzeapy.types.PropertyIDs,
>         value: str
>     ) ‑> Dict[str, str]




    
### Function `return_event_for_device` {#wyzeapy.utils.return_event_for_device}




>     def return_event_for_device(
>         device: wyzeapy.types.Device,
>         events: List[wyzeapy.types.Event]
>     ) ‑> Optional[wyzeapy.types.Event]







    
# Module `wyzeapy.wyze_auth_lib` {#wyzeapy.wyze_auth_lib}







    
## Classes


    
### Class `Token` {#wyzeapy.wyze_auth_lib.Token}




>     class Token(
>         access_token,
>         refresh_token,
>         last_login_time
>     )










    
### Class `WyzeAuthLib` {#wyzeapy.wyze_auth_lib.WyzeAuthLib}




>     class WyzeAuthLib(
>         username=None,
>         password=None,
>         token: wyzeapy.wyze_auth_lib.Token = None
>     )







    
#### Class variables


    
##### Variable `token` {#wyzeapy.wyze_auth_lib.WyzeAuthLib.token}



Type: `Optional[wyzeapy.wyze_auth_lib.Token]`




    
#### Instance variables


    
##### Variable `should_refresh` {#wyzeapy.wyze_auth_lib.WyzeAuthLib.should_refresh}



Type: `bool`




    
#### Static methods


    
##### `Method create` {#wyzeapy.wyze_auth_lib.WyzeAuthLib.create}




>     async def create(
>         username=None,
>         password=None,
>         token: wyzeapy.wyze_auth_lib.Token = None
>     )





    
#### Methods


    
##### Method `close` {#wyzeapy.wyze_auth_lib.WyzeAuthLib.close}




>     async def close(
>         self
>     )




    
##### Method `delete` {#wyzeapy.wyze_auth_lib.WyzeAuthLib.delete}




>     async def delete(
>         self,
>         url,
>         headers=None,
>         json=None
>     ) ‑> Dict[Any, Any]




    
##### Method `gen_session` {#wyzeapy.wyze_auth_lib.WyzeAuthLib.gen_session}




>     async def gen_session(
>         self
>     )




    
##### Method `get` {#wyzeapy.wyze_auth_lib.WyzeAuthLib.get}




>     async def get(
>         self,
>         url,
>         headers=None,
>         params=None
>     ) ‑> Dict[Any, Any]




    
##### Method `get_token_with_username_password` {#wyzeapy.wyze_auth_lib.WyzeAuthLib.get_token_with_username_password}




>     async def get_token_with_username_password(
>         self,
>         username,
>         password
>     ) ‑> wyzeapy.wyze_auth_lib.Token




    
##### Method `patch` {#wyzeapy.wyze_auth_lib.WyzeAuthLib.patch}




>     async def patch(
>         self,
>         url,
>         headers=None,
>         params=None,
>         json=None
>     ) ‑> Dict[Any, Any]




    
##### Method `post` {#wyzeapy.wyze_auth_lib.WyzeAuthLib.post}




>     async def post(
>         self,
>         url,
>         json=None,
>         headers=None,
>         data=None
>     ) ‑> Dict[Any, Any]




    
##### Method `refresh` {#wyzeapy.wyze_auth_lib.WyzeAuthLib.refresh}




>     async def refresh(
>         self
>     ) ‑> NoneType




    
##### Method `refresh_if_should` {#wyzeapy.wyze_auth_lib.WyzeAuthLib.refresh_if_should}




>     async def refresh_if_should(
>         self
>     )





-----
Generated by *pdoc* 0.9.2 (<https://pdoc3.github.io>).
