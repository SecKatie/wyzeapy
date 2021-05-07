# How to use

Example code:
```python
from src.wyzeapy import Client, ActionNotSupported, PropertyIDs
from src.wyzeapy import AccessTokenError

# Testing what happens when not logged in
# try:
#     wyze_client.get_object_list()
# except ParameterError as e:
#     print(e)
#
# wyze_client.login("jocoder6@gmail.com", "7PRgKbiVUa.ZYk4tw@b@ij") # Don't worry it is an old password
#
# # Testing what happens when access token is bad
# try:
#     wyze_client.access_token = "BAD"
#     wyze_client.get_object_list()
# except AccessTokenError as e:
#     print(e)
#
# wyze_client.login("jocoder6@gmail.com", "7PRgKbiVUa.ZYk4tw@b@ij")
#
# for device in wyze_client.get_object_list():
#     try:
#         wyze_client.run_action_list(device, [
#             {"pid": PropertyIDs.ON.value, "pvalue": "0"},
#             {"pid": PropertyIDs.COLOR.value, "pvalue": "FF0000"}
#         ])
#     except ActionNotSupported as e:
#         print(e)
#
#     try:
#         wyze_client.set_property_list(device, [
#             {"pid": PropertyIDs.ON.value, "pvalue": "0"},
#             {"pid": PropertyIDs.BRIGHTNESS.value, "pvalue": "100"}
#         ])
#     except ActionNotSupported as e:
#         print(e)
#
#     try:
#         wyze_client.set_property(device, PropertyIDs.ON.value, "0")
#     except ActionNotSupported as e:
#         print(e)

if __name__ == '__main__':
    """Documentation on how to use the code"""
    wyze_client = Client("USERNAME", "PASSWORD")
    devices = wyze_client.get_devices()
    for device in devices:
        wyze_client.get_info(device)
        try:
            wyze_client.turn_on(device, [
                wyze_client.create_pid_pair(PropertyIDs.COLOR_TEMP, str(6500))
            ])
        except ActionNotSupported:
            pass
        # print("{} {} {}".format(device.product_type, device.mac, wyze_client.get_info(device)))
    # for device in devices:
    #     try:
    #         # wyze_client.turn_on(device, [
    #         #     wyze_client.create_pid_pair(PropertyIDs.COLOR, "FF0000"),
    #         #     wyze_client.create_pid_pair(PropertyIDs.BRIGHTNESS, str(25))
    #         # ])
    #         wyze_client.turn_off(device)
    #     except ActionNotSupported as e:
    #         print("{} {}".format(type(e), e))
    #     except AccessTokenError as e:
    #         wyze_client.reauthenticate()
    #         wyze_client.turn_off(device)

```
