#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import base64
import hashlib
from typing import Dict, Any, List, Optional

from Crypto.Cipher import AES

from wyzeapy.exceptions import ParameterError, AccessTokenError, UnknownApiError
from wyzeapy.types import ResponseCodes, PropertyIDs, Device, Event


def pad(plain_text):
    """
    func to pad cleartext to be multiples of 8-byte blocks.
    If you want to encrypt a text message that is not multiples of 8-byte
    blocks, the text message must be padded with additional bytes to make the
    text message to be multiples of 8-byte blocks.
    """
    number_of_bytes_to_pad = AES.block_size - len(plain_text) % AES.block_size
    ascii_string = chr(number_of_bytes_to_pad)
    padding_str = number_of_bytes_to_pad * ascii_string
    padded_plain_text = plain_text + padding_str
    return padded_plain_text


def wyze_encrypt(plain_text, key):
    """
    func to encrypt plain text using AES-128-CBC

    Based on the implementation found in the Wyze Android App:
    https://paste.sr.ht/~joshmulliken/e9f67e05c4a774004b226d2ac1f070b6d341cb39

    :param plain_text: plain text to be encrypted
    :param key: key to encrypt plain text
    """
    padded_plain_text = pad(plain_text)
    raw_text = padded_plain_text.encode('utf-8')
    raw_key = key.encode('utf-8')
    cipher = AES.new(raw_key, AES.MODE_CBC, raw_key)  # Wyze uses the key as the IV
    cipher_text = cipher.encrypt(raw_text)
    cipher_text_b64 = base64.b64encode(cipher_text).decode('utf-8')
    return cipher_text_b64


def wyze_decrypt(cipher_text, key):
    """
    func to decrypt cipher text using AES-128-CBC

    Based on the implementation found in the Wyze Android App:
    https://paste.sr.ht/~joshmulliken/e9f67e05c4a774004b226d2ac1f070b6d341cb39

    :param cipher_text: cipher text to be decrypted
    :param key: key to decrypt cipher text
    """
    raw_cipher_text = base64.b64decode(cipher_text)
    raw_key = key.encode('utf-8')
    cipher = AES.new(raw_key, AES.MODE_CBC, raw_key)  # Wyze uses the key as the IV
    raw_text = cipher.decrypt(raw_cipher_text)
    plain_text = raw_text.decode('utf-8')
    return plain_text


def create_password(password: str) -> str:
    hex1 = hashlib.md5(password.encode()).hexdigest()
    hex2 = hashlib.md5(hex1.encode()).hexdigest()
    return hashlib.md5(hex2.encode()).hexdigest()


def check_for_errors_standard(response_json: Dict[str, Any]) -> None:
    if response_json['code'] != ResponseCodes.SUCCESS.value:
        if response_json['code'] == ResponseCodes.PARAMETER_ERROR.value:
            raise ParameterError(response_json)
        elif response_json['code'] == ResponseCodes.ACCESS_TOKEN_ERROR.value:
            raise AccessTokenError
        elif response_json['code'] == ResponseCodes.DEVICE_OFFLINE.value:
            return
        else:
            raise UnknownApiError(response_json)


def check_for_errors_lock(response_json: Dict[str, Any]) -> None:
    if response_json['ErrNo'] != 0:
        if response_json.get('code') == ResponseCodes.PARAMETER_ERROR.value:
            raise ParameterError
        elif response_json.get('code') == ResponseCodes.ACCESS_TOKEN_ERROR.value:
            raise AccessTokenError
        else:
            raise UnknownApiError(response_json)


def check_for_errors_thermostat(response_json: Dict[Any, Any]) -> None:
    if response_json['code'] != 1:
        raise UnknownApiError(response_json)


def check_for_errors_hms(response_json: Dict[Any, Any]) -> None:
    if response_json['message'] is None:
        raise AccessTokenError


def return_event_for_device(device: Device, events: List[Event]) -> Optional[Event]:
    for event in events:
        if event.device_mac == device.mac:
            return event

    return None


def create_pid_pair(pid_enum: PropertyIDs, value: str) -> Dict[str, str]:
    return {"pid": pid_enum.value, "pvalue": value}
