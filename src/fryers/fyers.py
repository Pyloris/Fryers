from fyers_apiv3 import fyersModel
from datetime import datetime, timedelta
from Crypto.Hash import SHA256
from os import path
import requests
from termcolor import cprint
import pandas as pd
import json

class Fyers:
    def __init__(self, client_id, secret_key, redirect_uri = '', pin='', config=None):

        # variables used in the connection
        # and data retrieval
        self.file_name = 'tokens.txt'
        self.pin = pin
        self.client_id = client_id
        self.secret_key = secret_key
        self.redirect_uri = redirect_uri if redirect_uri else "https://trade.fyers.in/api-login/redirect-uri/index.html"
        self.response_type = "code"
        self.grant_type = "authorization_code"
        self.config = config or {}


        # check if tokens already exist
        if (path.isfile(self.file_name)):
            
            # read the tokens
            with open(self.file_name) as f:
                tokens = f.readlines()
            
            # parse the tokens
            self.access_token, self.refresh_token = list(map(lambda x: x.strip(), tokens))

            if not self.test_fire():
                # parse the refresh token
                expiry_time = datetime.fromtimestamp(float((self.refresh_token.split(":"))[0]))
                self.refresh_token = (self.refresh_token.split(":"))[1]
                
                # if refresh token is still valid
                if datetime.now() < expiry_time:

                    sha256 = SHA256.new()
                    sha256.update(bytes((self.client_id + self.secret_key).encode('utf-8')))
                    appid_hash = sha256.hexdigest()

                    print(appid_hash)
                    
                    # grab new access token via refresh_token
                    resp = requests.post('https://api-t1.fyers.in/api/v3/validate-refresh-token', headers={'Content-Type':'application/json'}, data=json.dumps({'grant_type':'refresh_token', 'appIdHash':str(appid_hash), 'refresh_token':self.refresh_token, 'pin':self.pin}))

                    # if no erros
                    resp = resp.json()
                    print(resp)
                    if resp['s'] == 'ok':
                        self.access_token = resp['access_token']
                        self.save_tokens(self.access_token, str(expiry_time.timestamp()) + ":" + self.refresh_token)
                    else:
                        self.access_token, self.refresh_token = self.login()
                        self.save_tokens()

                else:

                    # if refresh token is not valid
                    self.access_token, self.refresh_token = self.login()
                    self.save_tokens()
        
        else:
            self.access_token, self.refresh_token = self.login()
            self.save_tokens()

        self.connect()
                    

    # login to the platform using their login flow
    def login(self):
        
        # create a session and generate redirect url for user to login to
        session = fyersModel.SessionModel(
            client_id = self.client_id,
            secret_key = self.secret_key,
            redirect_uri = self.redirect_uri,
            response_type = self.response_type
        )

        # generate the auth code
        response = session.generate_authcode()

        print("Visit the below url and login: ")
        print(response)

        auth_code = input("Enter the Auth Code recieved : ")

        session = fyersModel.SessionModel(
            client_id=self.client_id,
            secret_key=self.secret_key, 
            redirect_uri=self.redirect_uri, 
            response_type=self.response_type, 
            grant_type=self.grant_type
        )

        # set the auth code
        session.set_token(auth_code)

        # generate access token using authorization code
        resp = session.generate_token()

        # return access_token and refresh_token
        return resp['access_token'], resp['refresh_token']
    
    # save the refresh token and access token somewhere in a text file
    def save_tokens(self, a_t=None, r_t=None):
        
        # calculate timestamp to 15 days in future
        # refresh token works for 15 days if access_token expires
        if not a_t and not r_t:
            expiry_timestamp = (datetime.now()+timedelta(days=14)).timestamp()

            # open the file and write lines
            with open(self.file_name, "w") as f:
                f.writelines([self.access_token + "\n", str(expiry_timestamp) + ":" + self.refresh_token + "\n"])
        else:
            with open(self.file_name, "w") as f:
                f.writelines([a_t + "\n", r_t + "\n"])
        
        return True


    # set the config for data grabbing
    def set_config(self, config):
        self.config = config
    
    # connect to fyers api
    def connect(self):

        # create app instance
        self.fyers = fyersModel.FyersModel(client_id = self.client_id, is_async=False, token=self.access_token, log_path="")

    
    # test fire a request to check if access token is working
    def test_fire(self) -> bool:
        self.connect()

        resp = self.fyers.history({
            "symbol":"NSE:NIFTYBANK-INDEX",
            "resolution":"15",
            "date_format":"1",
            "range_from":"2023-07-01",
            "range_to":"2023-08-28",
            "cont_flag":"1"
        })

        if resp['s'] == 'error':
            return False
        else:
            return True


    # grab historical data for a symbol
    # returns a dataframe
    def history(self, symbol):
        def get_data():
            return self.fyers.history({"symbol":symbol, **self.config})

        # simple 1 retry mechanism to tackle the unbound error 
        try:
            data = get_data()
        except Exception:
            time.sleep(1)
            data = get_data()
            
        # convert the data into a suitable dataframe
        if data['s'] == 'ok':
            candles = data['candles']

            df = pd.DataFrame(candles, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])

            # return the dataframe
            return df
    

    # grab the native instance of FyersModel
    def get_native_instance(self):
        return self.fyers