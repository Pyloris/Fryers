![badge1](https://img.shields.io/badge/Fyers-Wrapper-blue)
![badge2](https://img.shields.io/badge/built%20for-python-orange?logo=python)
![badge3](https://img.shields.io/badge/fyers-v3-yello)


## Why Fryers?
> The reason i created this wrapper module for the `fyers_apiv3` module provided by the Fyers platform is because one has to make sure the access token is valid and if not generate new access token or use refresh_token, which added overhead to the scripts created using this module. But my wrapper takes care of all that.

> We Just have to provide my wrapper class `Fyers` with the `client_id`, `secret_key` and the `pin`. Once thats given, the login flow will be taken care of and we can enjoy the scripting without any hassel.


## How to Install
```terminal
pip install fryers
```

## Simple way to use
We can use this module for login flow and then use the native fyersModel instance to interact with the API.

Simple code to do this would be
```python
from fryers import Fyers

client_id = "xxxxx"
secret_key = "xxyyxyxy"
pin = "4783"

# Fyers logins automatically uses a saved token, if exists
# otherwise it re-initiates the login flow
# it outputs the returned URL which user has to visit
# and then copy the auth_code from there and paste it in the terminal
fyers = Fyers(client_id, secret_key, pin=pin)    # creates a file tokens.txt where tokens are stored

# grab the native instance and use native api
native_fyers = fyers.get_native_instance()

# we can use native api from (native_fyers) which is an instance of FyersModel
```

### NOTE
> This is current in development, i will be adding more features to make the api easy to use. I will also create a comprehensive documentation for this wrapper so that users dont have an issue using it.