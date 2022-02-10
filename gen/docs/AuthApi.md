# openapi_client.AuthApi

All URIs are relative to *https://auth-prod.api.wyze.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**app_user_refresh_token_post**](AuthApi.md#app_user_refresh_token_post) | **POST** /app/user/refresh_token | Refreshes the access_token using the refresh_token
[**user_login_post**](AuthApi.md#user_login_post) | **POST** /user/login | Logs user into the system
[**user_login_send_sms_code_post**](AuthApi.md#user_login_send_sms_code_post) | **POST** /user/login/sendSmsCode | Sends an SMS MFA Code to the user


# **app_user_refresh_token_post**
> InlineResponse2002 app_user_refresh_token_post(inline_object2)

Refreshes the access_token using the refresh_token

### Example

```python
import time
import openapi_client
from openapi_client.api import auth_api
from openapi_client.model.inline_object2 import InlineObject2
from openapi_client.model.inline_response2002 import InlineResponse2002
from pprint import pprint
# Defining the host is optional and defaults to https://auth-prod.api.wyze.com
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://auth-prod.api.wyze.com"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = auth_api.AuthApi(api_client)
    inline_object2 = InlineObject2(
        phone_id="5A036F98-D673-403A-B760-54B433092B9D",
        app_name="com.hualai.WyzeCam",
        app_version="2.18.43",
        sc="9f275790cab94a72bd206c8876429f3c",
        sv="9d74946e652647e9b6c9d59326aef104",
        phone_system_type="1",
        app_ver="com.hualai.WyzeCam___2.18.43",
        ts=1,
        refresh_token="IwOGYzYTlmM2YxOTQ5MGE3YmNmMDFkNTVk",
    ) # InlineObject2 | 

    # example passing only required values which don't have defaults set
    try:
        # Refreshes the access_token using the refresh_token
        api_response = api_instance.app_user_refresh_token_post(inline_object2)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AuthApi->app_user_refresh_token_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **inline_object2** | [**InlineObject2**](InlineObject2.md)|  |
 **x_api_key** | **str**|  | defaults to "WMXHYf79Nr5gIlt3r0r7p9Tcw5bvs6BB4U8O8nGJ"

### Return type

[**InlineResponse2002**](InlineResponse2002.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **user_login_post**
> InlineResponse200 user_login_post(phone_id, inline_object)

Logs user into the system

### Example

```python
import time
import openapi_client
from openapi_client.api import auth_api
from openapi_client.model.inline_object import InlineObject
from openapi_client.model.error_response import ErrorResponse
from openapi_client.model.inline_response200 import InlineResponse200
from pprint import pprint
# Defining the host is optional and defaults to https://auth-prod.api.wyze.com
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://auth-prod.api.wyze.com"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = auth_api.AuthApi(api_client)
    phone_id = "5A036F98-D673-403A-B760-54B433092B9D" # str | 
    inline_object = InlineObject(
        email="email_example",
        password="password_example",
        mfa_type=MfaType("TotpVerificationCode"),
        verification_id="BA4B907A-BE74-4960-B3A7-B96DAB41E8EA",
        verification_code=TotpCode(111111),
    ) # InlineObject | 

    # example passing only required values which don't have defaults set
    try:
        # Logs user into the system
        api_response = api_instance.user_login_post(phone_id, inline_object)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AuthApi->user_login_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **phone_id** | **str**|  |
 **inline_object** | [**InlineObject**](InlineObject.md)|  |
 **user_agent** | **str**|  | defaults to "wyze_android_2.19.14"
 **x_api_key** | **str**|  | defaults to "WMXHYf79Nr5gIlt3r0r7p9Tcw5bvs6BB4U8O8nGJ"

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Response object from the request |  -  |
**400** | Login error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **user_login_send_sms_code_post**
> InlineResponse2001 user_login_send_sms_code_post(phone_id, session_id, user_id)

Sends an SMS MFA Code to the user

### Example

```python
import time
import openapi_client
from openapi_client.api import auth_api
from openapi_client.model.inline_response2001 import InlineResponse2001
from openapi_client.model.str_none_type import StrNoneType
from pprint import pprint
# Defining the host is optional and defaults to https://auth-prod.api.wyze.com
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://auth-prod.api.wyze.com"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = auth_api.AuthApi(api_client)
    phone_id = "5A036F98-D673-403A-B760-54B433092B9D" # str | 
    session_id = "session_id_example" # str, none_type | 
    user_id = "9819dc122168028d5d574c817c8c5e75" # str | 

    # example passing only required values which don't have defaults set
    try:
        # Sends an SMS MFA Code to the user
        api_response = api_instance.user_login_send_sms_code_post(phone_id, session_id, user_id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AuthApi->user_login_send_sms_code_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **phone_id** | **str**|  |
 **session_id** | **str, none_type**|  |
 **user_id** | **str**|  |
 **user_agent** | **str**|  | defaults to "wyze_android_2.19.14"
 **x_api_key** | **str**|  | defaults to "WMXHYf79Nr5gIlt3r0r7p9Tcw5bvs6BB4U8O8nGJ"
 **mfa_phone_type** | **str**|  | defaults to "Primary"

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success response; sms sent |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

