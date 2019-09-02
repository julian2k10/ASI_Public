import os
import random
import requests

class Robinhood():

    def __init__(self, testing=False):
        self.device_token = self.GenerateDeviceToken()
        self.logged_in = False
        self.user_name = 'None'
        self.password = 'None'
        self.access_token = 'None'
        self.refresh_token = 'None'
        self.session = requests.Session()

        if not testing:
            self.session.headers = self.read_from_File('session_header.txt')
            self.payload = self.read_from_File('payload.txt')
        else:
            self.session.headers = -1
            self.payload = -1

        login_url = "https://api.robinhood.com/oauth2/token/"

        if isinstance(self.session.headers, dict) and isinstance(self.payload, dict):
            self.user_name = self.payload['username']
            self.password = self.payload['password']
            r = self.session.post(login_url, data=self.payload, headers=self.session.headers)
            data = r.json()
            if 'access_token' in data:
                print(f'Login Successful!\n')
            else:
                print('Token Expired! Creating New Session...')
                self.session.headers = {"Accept": "*/*",
                                        "Accept-Encoding": "gzip, deflate",
                                        "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",
                                        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                                        "X-Robinhood-API-Version": "1.0.0",
                                        "Connection": "keep-alive",
                                        "User-Agent": "Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)"
                                        }
                self.payload = {"client_id": "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS",
                                "expires_in": 86400,
                                "grant_type": "password",
                                "password": self.password,
                                "scope": "internal",
                                "username": self.user_name,
                                "challenge_type": 'sms',
                                "device_token": self.device_token
                                }

                self.login(self.user_name, self.password, remember_me=True)
        else:
            if testing == False : authenticate_user = self.read_from_File('auth.txt')
            else : authenticate_user = -1
            if isinstance(authenticate_user, dict) and 'username' in list(authenticate_user.keys()):
                print('Token Expired! Creating New Session...')
                self.user_name = authenticate_user['username']
                self.password = authenticate_user['password']
                self.session.headers = {"Accept": "*/*",
                                        "Accept-Encoding": "gzip, deflate",
                                        "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",
                                        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                                        "X-Robinhood-API-Version": "1.0.0",
                                        "Connection": "keep-alive",
                                        "User-Agent": "Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)"
                                        }
                self.payload = {"client_id": "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS",
                                "expires_in": 86400,
                                "grant_type": "password",
                                "password": self.password,
                                "scope": "internal",
                                "username": self.user_name,
                                "challenge_type": 'sms',
                                "device_token": self.device_token
                                }

                self.login(self.user_name, self.password, remember_me=True)
            else:
                print("\nLogin Credential Not Found! Please don't forget to login...\n")

    def GenerateDeviceToken(self):
        """
        This function will generate a token used when loggin on.
        :returns: A string representing the token.
        """
        rands = []
        for i in range(0,16):
            r = random.random()
            rand = 4294967296.0 * r
            rands.append((int(rand) >> ((3 & i) << 3)) & 255)

        hexa = []
        for i in range(0,256):
            hexa.append(str(hex(i+256)).lstrip("0x").rstrip("L")[1:])

        id = ""
        for i in range(0,16):
            id += hexa[rands[i]]

            if (i == 3) or (i == 5) or (i == 7) or (i == 9):
                id += "-"

        return(id)

    def write_to_File(self, File_Name, data):
    	with open(File_Name, 'w+') as f:
        	status = f.write(str(data))
        
    	return status

    def read_from_File(self, File_Name):
        import ast
        data = 0
        try:
            with open(File_Name, 'r') as f:
                s = f.read()
                data = ast.literal_eval(s)
            
        except FileNotFoundError:
            return -1
        except:
            return data
    
        return data

    def login(self, username, password, remember_me=False):
        self.username = username
        self.password = password

        login_url = "https://api.robinhood.com/oauth2/token/"
        r = self.session.post(login_url, data=self.payload, headers=self.session.headers)
        data = r.json()

        while not self.logged_in:
        
            if 'challenge' in data:
                challenge_id = data['challenge']['id']
                user_id = data['challenge']['user']
                robinhood_code = input("Enter Robinhood Code : ")
        
                challenge_url = f"https://api.robinhood.com/challenge/{challenge_id}/respond/"
                respond = {"response" : robinhood_code}
                self.payload.update(respond)
        
                r = self.session.post(challenge_url, data=self.payload, headers=self.session.headers)
                data = r.json()
        
                respond = {"X-ROBINHOOD-CHALLENGE-RESPONSE-ID" : challenge_id }
        
                self.session.headers.update(respond)
        
            r = self.session.post(login_url, data=self.payload, headers=self.session.headers)
            data = r.json()
            
            if 'access_token' in data:
                self.access_token = data['access_token']
                self.refresh_token = data['refresh_token']
                
                self.session.headers.update({'Authorization' : 'Bearer ' + self.access_token})
                if remember_me: 
                    self.write_to_File('session_header.txt', self.session.headers)
                    self.write_to_File('payload.txt', self.payload)
        
                print(f'Login Successful!\n')
                self.logged_in = True
    
        return data  
    
    def logout(self):
        '''
        Deletes stored token from session header.
        '''
        self.session.headers['Authorization'] = None
        self.write_to_File('session_header.txt', 'None')
        self.write_to_File('payload.txt', 'None')
        
    def get_id(self,symbol):
        '''
        Summary
        -------
        Returns the id of the stock

        Parameters
        ----------
        symbol : string
            This represents a stock ticker.

        Returns
        -------
        string
            Returns an string representing the id.

        '''
        symbol = symbol.upper()
        return(self.get_instruments_by_symbols(symbol,info='id')[0])

    def get_option_id(self,symbol):
        '''
        Summary
        -------
        Returns the option id of the stock.

        Parameters
        ----------
        symbol : string
            This represents a stock ticker.

        Returns
        -------
        string
            Returns an string representing the id.

        '''
        symbol = symbol.upper()
        return(self.get_chains(symbol)['underlying_instruments'][0]['id'])

    def get_tradable_chain_id(self,symbol):
        '''
        Summary
        -------
        Returns the tradable chain id of the option.

        Parameters
        ----------
        symbol : string
            This represents a stock ticker.

        Returns
        -------
        string
            Returns an string representing the id.

        '''
        symbol = symbol.upper()
        return(self.get_instruments_by_symbols(symbol)[0]['tradable_chain_id'])

    def get_specific_option_id(self,symbol,expirationData,strike,optionType='both'):
        '''
        Summary
        -------
        Returns the id of the option order.

        Parameters
        ----------
        symbol : string
            This represents a stock ticker.
        expriationDate : string
            This represents expiration date in the format YYYY-MM-DD.
        strike : string
            This represents a price of the option as a string.
        optionType : string
            Can be either call or put

        Returns
        -------
        string
            Returns an string representing the id.

        '''
        symbol = symbol.upper()
        return(self.find_options_for_stock_by_expiration_and_strike(symbol,expirationData,strike,optionType)[0]['id'])

    def get_specific_option_id_alternative(self,symbol,expirationDate,strike,optionType):

        return(self.get_specific_option_instrument_data(symbol,expirationDate,strike,optionType)['id'])

    def error_argument_not_key_in_dictionary(self,keyword):
        '''
        Summary
        -------
        Returns an error message for a given keyword.

        Parameters
        ----------
        keyword : string
            Represents a keyword that the user was trying to search for.

        Returns
        -------
        string
            Returns an string representing an error message.

        '''
        return('Error: The keyword "'+str(keyword)+'" is not a key value in the dictionary.')

    def error_api_endpoint_not_loaded(self,url):
        '''
        Summary
        -------
        Returns an error message for a missing url.

        Parameters
        ----------
        url : string
            Represents a url that the user was trying to search for.

        Returns
        -------
        string
            Returns an string representing an error message.

        '''
        return('Error: The url "'+str(url)+'" is either missing (404) or could not be loaded.')

    def error_api_endpoint_not_posted(self,url):
        '''
        Summary
        -------
        Returns an error message for a missing url.

        Parameters
        ----------
        url : string
            Represents a url that the user was trying to search for.

        Returns
        -------
        string
            Returns an string representing an error message.

        '''
        return('Error: The POST request to the url "'+str(url)+'" could not be completed.')

    def error_ticker_does_not_exist(self,ticker):
        '''
        Summary
        -------
        Returns an error message for a given ticker.

        Parameters
        ----------
        ticker : string
            Represents a keyword that the user was trying to search for.

        Returns
        -------
        string
            Returns an string representing an error message.

        '''
        return('Warning: "'+str(ticker)+'" is not a valid stock ticker. It is being ignored')

    def error_not_a_string(self,info):
        '''
        Summary
        -------
        Returns an error message for an input info.

        Parameters
        ----------
        info : string
            Represents a keyword that the user was passing as a parameter.

        Returns
        -------
        String
            Returns an string representing an error message.

        '''
        return('Error: The input parameter "'+str(info)+'" must be a string')

    def error_not_a_integer(self,info):
        '''
        Summary
        -------
        Returns an error message for an input info.

        Parameters
        ----------
        info : string
            Represents a keyword that the user was passing as a parameter.

        Returns
        -------
        String
            Returns an string representing an error message.

        '''
        return('Error: The input parameter "'+str(info)+'" must be an integer')

    def error_not_a_integer_or_float(self,info):
        '''
        Summary
        -------
        Returns an error message for an input info.

        Parameters
        ----------
        info : string
            Represents a keyword that the user was passing as a parameter.

        Returns
        -------
        String
            Returns an string representing an error message.

        '''
        return('Error: The input parameter "'+str(info)+'" must be an integer or a float.')

    def error_must_be_nonzero(self,info):
        '''
        Summary
        -------
        Returns an error message for an input info.

        Parameters
        ----------
        info : string
            Represents a keyword that the user was passing as a parameter.

        Returns
        -------
        String
            Returns an string representing an error message.

        '''
        return('Error: The input parameter "'+str(info)+'" must be an integer larger than zero and non-negative')

    def inputs_to_set(self,inputSymbols):
        '''
        Summary
        -------
        Takes any number of string items, makes them all uppercase, and removes all duplicates.

        Parameters
        ----------
        *inputSymbols : string
            May be a single string, a list of strings, or a tuple of strings.

        Returns
        -------
        set
            Returns a set of strings that are all uppercase.

        '''
        symbols = set()

        for symbol in inputSymbols:
            if type(symbol) is str:
                symbols.add(symbol.upper().strip())
            elif type(symbol) is list or type(symbol) is tuple or type(symbol) is set:
                symbol = [comp for comp in symbol if type(comp) is str]
                for item in symbol:
                    symbols.add(item.upper().strip())

        return list(symbols)

    def append_dataset_with_pagination(self,res,data):
        '''
        Summary
        -------
        Some of the data returned from API is seperated in different urls and needs to be loaded page by page.

        Parameters
        ----------
        res : requests.models.Response
            What is returned by session.get(url)
        data : List
            List to be appeneded with new information.

        Returns
        -------
        list
            Contains a list with the value that corresponds to the 'results' keyword. If the 'next' keyword is not none,
            then the results from that page are added to the list.

        '''
        counter = 2
        res_json = res.json()

        if res_json['next']:
            print('Found Additional pages.')
        while res_json['next']:
            try:
                res = self.session.get(res_json['next'])
                res_json = res.json()
            except:
                print('Additional pages exist but could not be loaded.')
                return(data)
            print('Loading page '+str(counter)+' ...')
            counter += 1
            for item in res_json['results']:
                data.append(item)

        return(data)

    def filter(self,data,info):
        '''
        Summary
        -------
        Takes the res_data and filters out the results to only include the value that corresponds to the keyword that is the same as info.

        Parameters
        ----------
        res : requests.models.Response
            What is returned by session.get(url)
        data : List
            List to be appeneded with new information.

        Returns
        -------
        list
            Contains a list with the value that corresponds to the 'results' keyword. If the 'next' keyword is not none,
            then the results from that page are added to the list.

        '''
        if (type(data) == list):
            if (len(data) == 0):
                return([None])
            compareDict = data[0]
            noneType = [None]
        elif (type(data) == dict):
            compareDict = data
            noneType = (None)

        if info is not None:
            if info in compareDict and type(data) == list:
                return([x[info] for x in data])
            elif info in compareDict and type(data) == dict:
                return(data[info])
            else:
                print(self.error_argument_not_key_in_dictionary(info))
                return(noneType)
        else:
            return(data)


    def get_user_profile(self,info=None):
        '''
        Summary
        -------
        Gets the information associated with the user profile, such as username, email, and links to the urls for other profiles.

        Parameters
        ----------
        info : string, optional
            Will filter the results to return the value for the key that matches info.

        Returns
        -------
        dictionary or string
            If info parameter is left as None then the function returns a dictionary of key/value pairs.
            Otherwise, the function will return a string corresponding to the value of the key that matches the info parameter.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return(None)

        url = 'https://api.robinhood.com/user/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return(None)

        return(self.filter(res_data,info))

    def get_investment_profile(self,info=None):
        '''
        Summary
        -------
        Gets the information associated with the investment profile. These are the answers to the questionaire you filled out
        when you made your profile.

        Parameters
        ----------
        info : string, optional
            Will filter the results to return the value for the key that matches info.

        Returns
        -------
        dictionary or string
            If info parameter is left as None then the function returns a dictionary of key/value pairs.
            Otherwise, the function will return a string corresponding to the value of the key that matches the info parameter.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return(None)

        url = 'https://api.robinhood.com/user/investment_profile/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return(None)

        return(self.filter(res_data,info))

    def get_basic_profile(self,info=None):
        '''
        Summary
        -------
        Gets the information associated with the personal profile, such as phone number, city, marital status, and date of birth.

        Parameters
        ----------
        info : string, optional
            Will filter the results to return the value for the key that matches info.

        Returns
        -------
        dictionary or string
            If info parameter is left as None then the function returns a dictionary of key/value pairs.
            Otherwise, the function will return a string corresponding to the value of the key that matches the info parameter.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return(None)

        url = 'https://api.robinhood.com/user/basic_info/'
        try:
            res = self.session.get(url)
            res_data = res.json()
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return(None)

        return(self.filter(res_data,info))

    def get_portfolios_profile(self,info=None):
        '''
        Summary
        -------
        Gets the information associated with the portfolios profile, such as withdrawable amount, market value of account, and excess margin.

        Parameters
        ----------
        info : string, optional
            Will filter the results to return the value for the key that matches info.

        Returns
        -------
        dictionary or string
            If info parameter is left as None then the function returns a dictionary of key/value pairs.
            Otherwise, the function will return a string corresponding to the value of the key that matches the info parameter.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return(None)

        url = 'https://api.robinhood.com/portfolios/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results'][0]
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return(None)


        return(self.filter(res_data,info))

    def get_accounts_profile(self,info=None):
        '''
        Summary
        -------
        Gets the information associated with the accounts profile, including day trading information and cash being held by robinhood

        Parameters
        ----------
        info : string, optional
            Will filter the results to return the value for the key that matches info.

        Returns
        -------
        dictionary or string
            If info parameter is left as None then the function returns a dictionary of key/value pairs.
            Otherwise, the function will return a string corresponding to the value of the key that matches the info parameter.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return(None)

        url = 'https://api.robinhood.com/accounts/'
        try:
            res = self.session.get(url)
            res_data = res.json()['results'][0]
            
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return(None)

        return(self.filter(res_data,info))

    def get_security_profile(self,info=None):
        '''
        Summary
        -------
        Gets the information associated with the security profile.

        Parameters
        ----------
        info : string, optional
            Will filter the results to return the value for the key that matches info.

        Returns
        -------
        dictionary or string
            If info parameter is left as None then the function returns a dictionary of key/value pairs.
            Otherwise, the function will return a string corresponding to the value of the key that matches the info parameter.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return(None)

        url = 'https://api.robinhood.com/user/additional_info/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return(None)

        return(self.filter(res_data,info))

    def get_quotes(self,*inputSymbols,info=None):
        '''
        Summary
        -------
        Takes any number of stock tickers and returns information pertaining to its price.

        Parameters
        ----------
        *inputSymbols : string
            This is a variable length parameter that represents a stock ticker. May be several tickers seperated by commas or a list of tickers.
        info : string, optional
            This is a keyword only parameter. Will filter the results to have a list of the values that correspond to key that matches info.

        Returns
        -------
        List
            If info parameter is left as None then the list will contain a dictionary of key/value pairs for each ticker.
            Otherwise will be a list of strings where the strings are the values of the key that corresponds to info.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        symbols = self.inputs_to_set(inputSymbols)
        url = 'https://api.robinhood.com/quotes/?symbols='+','.join(symbols)
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        for count,item in enumerate(res_data['results']):
            if item is None:
                print(self.error_ticker_does_not_exist(symbols[count]))

        res_data = [item for item in res_data['results'] if item is not None]

        return(self.filter(res_data,info))

    def get_latest_price(self,*inputSymbols):
        '''
        Summary
        -------
        Takes any number of stock tickers and returns the latest price of each one as a string.

        Parameters
        ----------
        *inputSymbols : string
            This is a variable length parameter that represents a stock ticker. May be several tickers seperated by commas or a list of tickers.

        Returns
        -------
        List
            Returns a list of strings of the latest price of each ticker.

        '''
        symbols = self.inputs_to_set(inputSymbols)
        myquote = self.get_quotes(symbols)

        price_list = []
        for item in myquote:
            if isinstance(item, dict):
                if item['last_extended_hours_trade_price'] is None:
                    price_list.append(item['last_trade_price'])
                else:
                    price_list.append(item['last_extended_hours_trade_price'])
        return(price_list)

    def get_fundamentals(self,*inputSymbols,info=None):
        '''
        Summary
        -------
        Takes any number of stock tickers and returns fundamental information about the stock such as what sector it is in,
        a description of the company, dividend yield, and market cap.

        Parameters
        ----------
        *inputSymbols : string
            This is a variable length parameter that represents a stock ticker. May be several tickers seperated by commas or a list of tickers.
        info : string, optional
            This is a keyword only parameter. Will filter the results to have a list of the values that correspond to key that matches info.

        Returns
        -------
        List
            If info parameter is left as None then the list will contain a dictionary of key/value pairs for each ticker.
            Otherwise will be a list of strings where the strings are the values of the key that corresponds to info.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        symbols = self.inputs_to_set(inputSymbols)
        url = 'https://api.robinhood.com/fundamentals/?symbols='+','.join(symbols)
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        for count,item in enumerate(res_data['results']):
            if item is None:
                print(self.error_ticker_does_not_exist(symbols[count]))

        res_data = [item for item in res_data['results'] if item is not None]

        return(self.filter(res_data,info))

    def get_instruments_by_symbols(self,*inputSymbols,info=None):
        '''
        Summary
        -------
        Takes any number of stock tickers and returns information held by the market such as ticker name, bloomberg id, and listing date.

        Parameters
        ----------
        *inputSymbols : string
            This is a variable length parameter that represents a stock ticker. May be several tickers seperated by commas or a list of tickers.
        info : string, optional
            This is a keyword only parameter. Will filter the results to have a list of the values that correspond to key that matches info.

        Returns
        -------
        List
            If info parameter is left as None then the list will contain a dictionary of key/value pairs for each ticker.
            Otherwise will be a list of strings where the strings are the values of the key that corresponds to info.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        symbols = self.inputs_to_set(inputSymbols)
        res_data = []
        for item in symbols:
            url = 'https://api.robinhood.com/instruments/?symbol='+item
            try:
                res = self.session.get(url)
                res.raise_for_status()
                res_other = res.json()['results'][0]
            except:
                res_other = []

            if len(res_other) == 0:
                print(self.error_ticker_does_not_exist(item))
            else:
                res_data.append(res_other)

        return(self.filter(res_data,info))

    def get_instrument_by_url(self,url,info=None):
        '''
        Summary
        -------
        Takes a single url for the stock. Should be located at https://api.robinhood.com/instruments/<id> where <id> is the
        id of the stock.

        Parameters
        ----------
        url : string
            Url of the stock.
        info : string, optional
            Will filter the results to have a list of the values that correspond to key that matches info.

        Returns
        -------
        dictionary or string
            If info parameter is left as None then the list will contain a dictionary of key/value pairs for the stock.
            Otherwise, the function will return a string corresponding to the value of the key that matches the info parameter.

        '''
        if (type(url) is not str):
            print(self.error_not_a_string(url))
            return(None)

        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return(None)

        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return(None)

        return(self.filter(res_data,info))

    def get_name_by_symbol(self,symbol):
        '''
        Summary
        -------
        Returns the name of a stock if given the symbol.

        Parameters
        ----------
        symbol : string
            The ticker of the stock as a string.

        Returns
        -------
        String
            Returns the simple name of the stock. If the simple name does not exist then returns the full name.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return(None)

        url = 'https://api.robinhood.com/instruments/?symbol='+symbol
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results'][0]
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return(None)

        if not res_data['simple_name']:
            name_data = res_data['name']
        else:
            name_data = res_data['simple_name']

        return(name_data)

    def get_name_by_url(self,url):
        '''
        Summary
        -------
        Returns the name of a stock if given the instrument url.

        Parameters
        ----------
        url : string
            The url of the stock as a string.

        Returns
        -------
        String
            Returns the simple name of the stock. If the simple name does not exist then returns the full name.

        '''
        if (type(url) is not str):
            print(self.error_not_a_string(url))
            return(None)

        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return(None)

        if not res_data['simple_name']:
            name_data = res_data['name']
        else:
            name_data = res_data['simple_name']

        return(name_data)

    def get_historicals(self,*inputSymbols,span='week',bounds='regular'):
        '''
        Summary
        -------
        Represents the data that is used to make the graphs.

        Parameters
        ----------
        *inputSymbols : string
            This is a variable length parameter that represents a stock ticker. May be several tickers seperated by commas or a list of tickers.
        span : string, optional
            Sets the range of the data to be either 'day', 'week', 'year', or '5year'. Default is 'week'.
        bounds : string,optional
            Represents if graph will include extended trading hours or just regular trading hours. Values are 'extended' or 'regular'.

        Returns
        -------
        List of Lists
            Returns a list that contains a list for each symbol. Each list contains a dictionary where each dictionary is for a different time.

        '''
        span_check = ['day','week','year','5year']
        bounds_check =['extended','regular','trading']
        if span not in span_check:
            print('ERROR: Span must be "day","week","year",or "5year"')
            return([None])
        if bounds not in bounds_check:
            print('ERROR: Bounds must be "extended","regular",or "trading"')
            return([None])
        if (bounds == 'extended' or bounds == 'trading') and span != 'day':
            print('ERROR: extended and trading bounds can only be used with a span of "day"')
            return([None])

        if span=='day':
            interval = '5minute'
        elif span=='week':
            interval = '10minute'
        elif span=='year':
            interval = 'day'
        else:
            interval = 'week'

        symbols = self.inputs_to_set(inputSymbols)
        symbols_joined = ','.join(symbols)

        url = 'https://api.robinhood.com/quotes/historicals/'+ \
               '?symbols='+symbols_joined+'&interval='+interval+'&span='+span+'&bounds='+bounds

        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        for count,item in enumerate(res_data):
            if (len(item['historicals']) == 0):
                print(self.error_ticker_does_not_exist(symbols[count]))

        res_data = [item['historicals'] for item in res_data if len(item['historicals']) is not 0]

        return(res_data)

    def query_instruments(self,query):
        '''
        Summary
        -------
        Will search the stocks for that contain the query keyword and return the instrument data.

        Parameters
        ----------
        query : string,
            Will filter the results to have a list of the dictionaries that contain the query keyword.

        Returns
        -------
        List
            Will be a list of dictionaries that contain the instrument data for each stock that matches the query.

        '''
        if (type(query) is not str):
            print(self.error_not_a_string(query))
            return([None])

        url = 'https://api.robinhood.com/instruments/?query='+query
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        if len(res_data) == 0:
            print('No results found for that keyword')
            return([None])
        else:
            print('Found '+str(len(res_data))+' results')
            return(res_data)

    def get_ratings(self,symbol,info=None):
        '''
        Summary
        -------
        Returns the ratings for a stock.

        Parameters
        ----------
        symbol : string
            This represents a stock ticker.

        Returns
        -------
        dictionary
            Returns a dictionary of key/value pairs.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return(None)

        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return(None)

        symbol = symbol.upper()
        url = 'https://api.robinhood.com/midlands/ratings/{}/'.format(self.get_id(symbol))
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()
        except:
            return(None)

        oldText = res_data['ratings'][0]['text']
        res_data['ratings'][0]['text'] = oldText.encode('UTF-8')

        return(self.filter(res_data,info))

    def get_popularity(self,symbol,info=None):
        '''
        Summary
        -------
        Returns the number of times a stock has been traded recently.

        Parameters
        ----------
        symbol : string
            This represents a stock ticker.

        Returns
        -------
        dictionary
            Returns a dictionary of key/value pairs.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return(None)

        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return(None)

        symbol = symbol.upper()
        url = 'https://api.robinhood.com/instruments/'+self.get_id(symbol)+'/popularity/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return(None)

        return(self.filter(res_data,info))

    def get_events(self,symbol,info=None):
        '''
        Summary
        -------
        Returns the events related to a stock.

        Parameters
        ----------
        symbol : string
            This represents a stock ticker.

        Returns
        -------
        list
            Returns a list of items.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return([None])

        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        symbol = symbol.upper()
        url = 'https://api.robinhood.com/options/events/?equity_instrument_id='+self.get_id(symbol)
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        return(self.filter(res_data,info))

    def get_earnings(self,symbol,info=None):
        '''
        Summary
        -------
        Returns the earnings for the differenct financial quarters.

        Parameters
        ----------
        symbol : string
            This represents a stock ticker.

        Returns
        -------
        list
            Returns a list of items.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return([None])

        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        symbol = symbol.upper()
        url = 'https://api.robinhood.com/marketdata/earnings/?symbol='+symbol
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        return(self.filter(res_data,info))

    def get_news(self,symbol,info=None):
        '''
        Summary
        -------
        Returns news stories for a stock.

        Parameters
        ----------
        symbol : string
            This represents a stock ticker.

        Returns
        -------
        list
            Returns a list of items.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return([None])

        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        symbol = symbol.upper()
        url = 'https://api.robinhood.com/midlands/news/'+symbol+'/?'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        return(self.filter(res_data,info))

    def get_splits(self,symbol,info=None):
        '''
        Summary
        -------
        Returns splits that have happened for a stock.

        Parameters
        ----------
        symbol : string
            This represents a stock ticker.

        Returns
        -------
        list of dictionaries
            Returns a list of dictionaries.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string('symbol'))
            return([None])

        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        symbol = symbol.upper()
        url = 'https://api.robinhood.com/instruments/'+self.get_id(symbol)+'/splits/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        return(self.filter(res_data,info))

    def get_positions(self,info=None):
        '''
        Summary
        -------
        Will return a list containing every position ever traded.

        Parameters
        ----------
        info : string, optional
            Will filter the results to have a list of the values that correspond to key that matches info.

        Returns
        -------
        List
            If info parameter is left as None then the list will contain a dictionary of key/value pairs for each ticker.
            Otherwise will be a list of strings where the strings are the values of the key that corresponds to info.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        url = 'https://api.robinhood.com/positions/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        return(self.filter(res_data,info))

    def get_owned_positions(self,info=None):
        '''
        Summary
        -------
        Same as get_positions() but will only return stocks/options that are currently held.

        Parameters
        ----------
        info : string, optional
            Will filter the results to have a list of the values that correspond to key that matches info.

        Returns
        -------
        List
            If info parameter is left as None then the list will contain a dictionary of key/value pairs for each ticker.
            Otherwise will be a list of strings where the strings are the values of the key that corresponds to info.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        url = 'https://api.robinhood.com/positions/?nonzero=true'
        try:
            res = self.session.get(url)
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        return(self.filter(res_data,info))

    def get_dividends(self,info=None):
        '''
        Summary
        -------
        Returns a list of dividend trasactions that include information such as the percentage rate, amount, shares of held stock,
        and date paid.

        Parameters
        ----------
        info : string, optional
            Will filter the results to have a list of the values that correspond to key that matches info.

        Returns
        -------
        List
            If info parameter is left as None then the list will contain a dictionary of key/value pairs for each ticker.
            Otherwise will be a list of strings where the strings are the values of the key that corresponds to info.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        url = 'https://api.robinhood.com/dividends/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        return(self.filter(res_data,info))

    def get_total_dividends(self):
        '''
        Summary
        -------
        Returns a double number representing the total amount of dividends paid to the account.

        Returns
        -------
        Float
            Total dollar amount of dividends paid to the account as a 2 precision float.

        '''
        url = 'https://api.robinhood.com/dividends/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return(None)

        res_data = self.append_dataset_with_pagination(res,res_data)

        dividend_total = 0
        for item in res_data:
            dividend_total += float(item['amount'])
        return("{0:.2f}".format(dividend_total))

    def get_documents(self,info=None):
        '''
        Summary
        -------
        Returns a list of document trasactions.

        Parameters
        ----------
        info : string, optional
            Will filter the results to have a list of the values that correspond to key that matches info.

        Returns
        -------
        List
            If info parameter is left as None then the list will contain a dictionary of key/value pairs for each ticker.
            Otherwise will be a list of strings where the strings are the values of the key that corresponds to info.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        url = 'https://api.robinhood.com/documents/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        return(self.filter(res_data,info))

    def download_document(self,url,name=None,dirpath=None):
        '''
        Summary
        -------
        Downloads a document and saves as a PDF when given download URL. Must choose a name and may choose a
        directory to save it in - otherwise it saves in the root directory of code.

        Parameters
        ----------
        url : string
            URL of the document to download.
        name : string, optional
            The name to save the document as. Defaults to url name.
        dirpath:
            The directory to save the document in.

        Returns
        -------
        None

        '''
        if (type(ulr) is not str):
            print(self.error_not_a_string(url))
            return(None)

        if (type(name) is not str and name is not None):
            print(self.error_not_a_string(name))
            return(None)

        if (type(dirpath) is not str and dirpath is not None):
            print(self.error_not_a_string(dirpath))
            return(None)

        try:
            res_data = self.session.get(url)
            res_data.raise_for_status()
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return(None)

        print('Writing PDF...')
        if not name:
            name = url[36:].split('/',1)[0]
        if dirpath:
            directory = dirpath
        else:
            directory = 'robin_documents/'
        filename = directory+name+'.pdf'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        open(filename, 'wb').write(res_data.content)
        print('Done - Wrote file '+name+'.pdf'+' to '+os.path.abspath(filename))

        return(None)

    def download_all_documents(self,doctype=None,dirpath=None):
        '''
        Summary
        -------
        Download all documents or all documents of a cetain doctype i.e. account_statement

        Parameters
        ----------
        doctype : string, optional
            The type of files to download.
        dirpath:
            The directory to save the document in.

        Returns
        -------
        None

        '''
        if (type(doctype) is not str and doctype is not None):
            print(self.error_not_a_string(name))
            return(None)

        if (type(dirpath) is not str and dirpath is not None):
            print(self.error_not_a_string(dirpath))
            return(None)

        documents = self.get_documents()

        downloaded_files = False
        print('Writing PDF...')
        if dirpath:
            directory = dirpath
        else:
            directory = 'robin_documents/'
        counter = 0
        for item in documents:
            if doctype == None:
                res_data = self.session.get(item['download_url'])
                name = item['created_at'][0:10]+'-'+item['type']+'-'+item['id']
                filename = directory+name+'.pdf'
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                open(filename, 'wb').write(res_data.content)
                downloaded_files = True
                counter += 1
            else:
                if item['type'] == doctype:
                    res_data = self.session.get(item['download_url'])
                    name = item['created_at'][0:10]+'-'+item['type']+'-'+item['id']
                    filename = directory+name+'.pdf'
                    os.makedirs(os.path.dirname(filename), exist_ok=True)
                    open(filename, 'wb').write(res_data.content)
                    downloaded_files = True
                    counter += 1

        if downloaded_files == False:
            print('WARNING: Could not find files of that doctype to download')
        else:
            if counter == 1:
                print('Done - wrote '+str(counter)+' file to '+os.path.abspath(directory))
            else:
                print('Done - wrote '+str(counter)+' files to '+os.path.abspath(directory))

        return(None)

    def get_all_watchlists(self,info=None):
        '''
        Summary
        -------
        Gets a list of all watchlists

        Parameters
        info : string, optional
            Optional variable to filter the results.

        Returns
        -------
        list
            Returns a list of items.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        url = 'https://api.robinhood.com/watchlists/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        return(self.filter(res_data,info))

    def get_watchlist_by_name(self,name='Default',info=None):
        '''
        Summary
        -------
        Gets list of stocks in a single watchlist.

        Parameters
        ----------
        name : string
            The name of the watchlist.
        info : string, optional
            Will filter the results.

        Returns
        -------
        list
            Returns a list of the items.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        url = 'https://api.robinhood.com/watchlists/'+name+'/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        return(self.filter(res_data,info))

    def post_symbols_to_watchlist(self,*inputSymbols,name='Default'):
        '''
        Summary
        -------
        Posts multiple symbols to a watchlist.

        Parameters
        ----------
        *inputSymbols : string
            Varaible length inputs that represent the stocks.
        name : string, optional
            Name of the watchlist to change.

        Returns
        -------
        dictionary
            Returns the information related to the session request.

        '''
        symbols = self.inputs_to_set(inputSymbols)
        data = {
        'symbols': ','.join(symbols)
        }
        url = 'https://api.robinhood.com/watchlists/'+name+'/bulk_add/'
        try:
            res = self.session.post(url,data=data)
            res.raise_for_status()
        except:
            raise

        return(res)

    def delete_symbols_from_watchlist(self,*inputSymbols,name='Default'):
        '''
        Summary
        -------
        Deletes multiple symbols from a watchlist.

        Parameters
        ----------
        *inputSymbols : string
            Varaible length inputs that represent the stocks.
        name : string, optional
            Name of the watchlist to change.

        Returns
        -------
        dictionary
            Returns the information related to the session request.

        '''
        symbols = self.inputs_to_set(inputSymbols)
        symbols = self.get_fundamentals(symbols,info='instrument')

        watchlist = self.get_watchlist_by_name(name=name)

        data = []

        for symbol in symbols:
            for list_ in watchlist:
                if symbol == list_['instrument']:
                    data.append(symbol[37:])

        for item in data:
            url = 'https://api.robinhood.com/watchlists/'+name+item
            try:
                res = self.session.delete(url)
                res.raise_for_status()
            except:
                raise

        return(res)

    def get_notifications(self,info=None):
        '''
        Summary
        -------
        Returns all notifications.

        Parameters
        ----------
        info : string
            Will filter the results to have a list of the values that correspond to key that matches info.

        Returns
        -------
        list
            Returns a list of items.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        url = 'https://api.robinhood.com/notifications/devices/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        return(self.filter(res_data,info))

    def get_latest_notification(self):
        '''
        Summary
        -------
        Gets the time of the latest notification.

        Returns
        -------
        dictionary
            Returns a dictionary of key/value pairs.

        '''
        url = 'https://api.robinhood.com/midlands/notifications/notification_tracker/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return(None)

        return(res_data)

    def get_top_movers(self,direction,info=None):
        '''
        Summary
        -------
        Returns all notifications.

        Parameters
        ----------
        info : string
            Will filter the results to have a list of the values that correspond to key that matches info.

        Returns
        -------
        list
            Returns a list of items.

        '''
        if (type(direction) is not str):
            print(self.error_not_a_string(direction))
            return([None])

        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        direction = direction.lower()
        if (direction != 'up' and direction != 'down'):
            print('Error: direction must be "up" or "down"')
            return([None])

        url = 'https://api.robinhood.com/midlands/movers/sp500/?direction='+direction
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        return(self.filter(res_data,info))

    def get_markets(self,info=None):
        '''
        Summary
        -------
        Returns a list of available markets.

        Parameters
        ----------
        info : string
            Will filter the results to have a list of the values that correspond to key that matches info.

        Returns
        -------
        list
            Returns a list of items.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        url = 'https://api.robinhood.com/markets/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        return(self.filter(res_data,info))

    def get_wire_transfers(self,info=None):
        '''
        Summary
        -------
        Returns all wire transers.

        Parameters
        ----------
        info : string
            Will filter the results to have a list of the values that correspond to key that matches info.

        Returns
        -------
        list
            Returns a list of items.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        url = 'https://api.robinhood.com/wire/transfers'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        return(self.filter(res_data,info))

    def get_margin_calls(self,symbol=None):
        '''
        Summary
        -------
        Returns margin calls executed on the account.

        Parameters
        ----------
        symbol : string
            This represents a stock ticker.

        Returns
        -------
        list
            Returns a list of items.

        '''
        if (type(symbol) is not str and symbol is not None):
            print(self.error_not_a_string(symbol))
            return([None])

        if symbol is not None:
            symbol = symbol.upper()
            url = 'https://api.robinhood.com/margin/calls/?equity_instrument_id='+self.get_id(symbol)
        else:
            url = 'https://api.robinhood.com/margin/calls/'

        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        return(res_data)

    def get_deposits(self):
        '''
        Summary
        -------
        Gets queued deposits.

        Returns
        -------
        dictionary
            Returns a dictionary of key/value pairs.

        '''
        url = 'https://api.robinhood.com/ach/iav/queued_deposit/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return(None)

        return(res_data)

    def get_all_orders(self,info=None):
        '''
        Summary
        -------
        Returns all orders that have been processed for account.

        Parameters
        ----------
        info : string, optional
            Will filter the results to have a list of the values that correspond to key that matches info.

        Returns
        -------
        list or string
            If info parameter is left as None then the list will contain a dictionary of key/value pairs for each ticker.
            Otherwise will be a list of strings where the strings are the values of the key that corresponds to info.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        url = 'https://api.robinhood.com/orders/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        return(self.filter(res_data,info))

    def get_all_open_orders(self,info=None):
        '''
        Summary
        -------
        Returns all open orders.

        Parameters
        ----------
        info : string, optional
            Will filter the results to have a list of the values that correspond to key that matches info.

        Returns
        -------
        list or string
            If info parameter is left as None then the list will contain a dictionary of key/value pairs for each ticker.
            Otherwise will be a list of strings where the strings are the values of the key that corresponds to info.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        url = 'https://api.robinhood.com/orders/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        res_data = [item for item in res_data if item['cancel'] is not None]

        return(self.filter(res_data,info))

    def get_order_info(self,order_id):
        '''
        Does Not Work!!!

        Summary
        -------
        Gets the order information

        Parameters
        ----------
        order_id : string
            Url that points to a specific order.

        Returns
        -------
        Dictionary
            Returns a dictionary of key/value pairs.

        '''
        if (type(order_id) is not str):
            print(self.error_not_a_string(order_id))
            return([None])

        url = 'https://api.robinhood.com/orders/'+order_id+'/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        return(res_data)

    def query_orders(self,**arguments):
        '''
        Summary
        -------
        Returns a list of orders that match the query.

        Parameters
        ----------
        **arguments : variable
            Variable length of keyword arguments. EX. find_orders(symbol='FB',cancel=None,quantity=1)

        Returns
        -------
        list
            Returns a list of orders that match.

        '''
        url = 'https://api.robinhood.com/orders/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        if (len(arguments) == 0):
            return(res_data)

        for item in res_data:
            item['quantity'] = str(int(float(item['quantity'])))

        if 'symbol' in arguments.keys():
            arguments['instrument'] = self.get_instruments_by_symbols(arguments['symbol'],info='url')[0]
            del arguments['symbol']

        if 'quantity' in arguments.keys():
            arguments['quantity'] = str(arguments['quantity'])

        stop = len(arguments.keys())-1
        list_of_orders=[]
        for item in res_data:
            for i,(key,value) in enumerate(arguments.items()):
                if key not in item:
                    print(self.error_argument_not_key_in_dictionary(key))
                    return([None])
                if value != item[key]:
                    break
                if i == stop:
                    list_of_orders.append(item)

        return(list_of_orders)

    def cancel_all_open_orders(self):
        '''
        Summary
        -------
        Cancels all open orders.

        Returns
        -------
        The request information

        '''
        url = 'https://api.robinhood.com/orders/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return(None)

        res_data = self.append_dataset_with_pagination(res,res_data)

        res_data = [item['id'] for item in res_data if item['cancel'] is not None]

        for item in res_data:
            cancel_url = 'https://api.robinhood.com/orders/'+item+'/cancel/'
            try:
                res = self.session.post(cancel_url)
                res.raise_for_status()
                res_data = res.json()
            except:
                print(self.error_api_endpoint_not_posted(cancel_url))
                return False

        print('All Orders Cancelled')
        return True

    def cancel_stock_orders(self, symbol):
        '''
        Summary
        -------
        Cancel pending orders for a specific stock.

        Parameters
        ----------
        symbol : string - Stock Ticker. 
        e.g cancel_stock_orders(symbol='MSFT')

        Returns
        -------
        True : Order was canceled successfully
        False: Order was not found
        '''
        order_cancel = False
        url = None
        try:
            order_history = self.query_orders(symbol=symbol)
            for order in order_history:
                if isinstance(order, dict):
                    url = order['cancel']
                    if isinstance(url, str):
                        res = self.session.post(url)
                        order_cancel = True
                        print(f'{symbol} Order Canceled!')

            return order_cancel

        except Exception as ex:
            try:
                print(f'Error canceling {symbol} order! \n{ex.message}')

            except:
                print(f'Error canceling {symbol} order! \n{ex}')

            return order_cancel

    def order_buy_market(self,symbol,quantity,timeInForce='gtc'):
        '''
        Summary
        -------
        Buys a certain quantity of a stock.

        Parameters
        ----------
        symbol : string
            The symbol of the stock as a string.
        quantity : int
            The amount to buy of the stock as an integer.
        timeInForce : string, optional
            Changes how long the order will be in effect forself. 'gtc' = good until cancelled.
            'gfd' = good for the day. 'ioc' = immediate or cancel. 'opg' execute at opening.

        Returns
        -------
        Dictionary
            Contains information regarding the purchase of stocks, such as the order id, the state of order (queued,confired,filled, failed, canceled, etc.),
            the price, and the quantity.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return(None)

        if (type(timeInForce) is not str):
            print(self.error_not_a_string(timeInForce))
            return(None)

        if (type(quantity) is not int):
            print(self.error_not_a_integer(quantity))
            return(None)
        elif (quantity < 1):
            print(self.error_must_be_nonzero(quantity))
            return(None)

        symbol = symbol.upper()

        data = {
        'account': self.get_accounts_profile(info='url'),
        'instrument': self.get_instruments_by_symbols(symbol,info='url')[0],
        'symbol': symbol,
        'price': float(self.get_latest_price(symbol)[0]),
        'quantity': quantity,
        'type': 'market',
        'stop_price': None,
        'time_in_force': timeInForce,
        'trigger': 'immediate',
        'side': 'buy'
        }

        url = "https://api.robinhood.com/orders/"
        res_json = None
        try:
            res = self.session.post(url,data=data)
            res.raise_for_status()
            res_json = res.json()
        except:
            raise

        return(res_json)

    def order_buy_limit(self,symbol,quantity,limitPrice,timeInForce='gtc'):
        '''
        Summary
        -------
        Sets a limit order to buy a certain quantity of a stock.

        Parameters
        ----------
        symbol : string
            The symbol of the stock as a string.
        quantity : int
            The amount to buy of the stock as an integer.
        limitPrice: int
            The amount you are willing to pay for the stock.
        timeInForce : string, optional
            Changes how long the order will be in effect forself. 'gtc' = good until cancelled.
            'gfd' = good for the day. 'ioc' = immediate or cancel. 'opg' execute at opening.

        Returns
        -------
        Dictionary
            Contains information regarding the purchase of stocks, such as the order id, the state of order (queued,confired,filled, failed, canceled, etc.),
            the price, and the quantity.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return(None)

        if (type(timeInForce) is not str):
            print(self.error_not_a_string(timeInForce))
            return(None)

        if (type(quantity) is not int):
            print(self.error_not_a_integer(quantity))
            return(None)
        elif (quantity < 1):
            print(self.error_must_be_nonzero(quantity))
            return(None)

        if (type(limitPrice) is not int and type(limitPrice) is not float):
            print(self.error_not_a_integer_or_float(limitPrice))
            return(None)

        symbol = symbol.upper()

        data = {
        'account': self.get_accounts_profile(info='url'),
        'instrument': self.get_instruments_by_symbols(symbol,info='url')[0],
        'symbol': symbol,
        'price': limitPrice,
        'quantity': quantity,
        'type': 'limit',
        'stop_price': None,
        'time_in_force': timeInForce,
        'trigger': 'immediate',
        'side': 'buy'
        }

        url = "https://api.robinhood.com/orders/"
        res_json = None
        try:
            res = self.session.post(url,data=data)
            res_json = res.json()
        except:
            raise

        return(res_json)

    def order_buy_stop_loss(self,symbol,quantity,stopPrice,timeInForce='gtc'):
        '''
        Summary
        -------
        Sets a stop loss order to buy a certain quantity of a stock.

        Parameters
        ----------
        symbol : string
            The symbol of the stock as a string.
        quantity : int
            The amount to buy of the stock as an integer.
        stopPrice: int
            The price above the current price that converts your order to market order.
        timeInForce : string, optional
            Changes how long the order will be in effect forself. 'gtc' = good until cancelled.
            'gfd' = good for the day. 'ioc' = immediate or cancel. 'opg' execute at opening.

        Returns
        -------
        Dictionary
            Contains information regarding the purchase of stocks, such as the order id, the state of order (queued,confired,filled, failed, canceled, etc.),
            the price, and the quantity.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return(None)

        if (type(timeInForce) is not str):
            print(self.error_not_a_string(timeInForce))
            return(None)

        if (type(quantity) is not int):
            print(self.error_not_a_integer(quantity))
            return(None)
        elif (quantity < 1):
            print(self.error_must_be_nonzero(quantity))
            return(None)

        if (type(stopPrice) is not int and type(stopPrice) is not float):
            print(self.error_not_a_integer_or_float(stopPrice))
            return(None)

        latestPrice = float(self.get_latest_price(symbol)[0])
        symbol = symbol.upper()

        if (latestPrice > stopPrice):
            print('Error: stopPrice must be above the current price.')
            return(None)

        data = {
        'account': self.get_accounts_profile(info='url'),
        'instrument': self.get_instruments_by_symbols(symbol,info='url')[0],
        'symbol': symbol,
        'price': stopPrice,
        'quantity': quantity,
        'type': 'market',
        'stop_price': stopPrice,
        'time_in_force': timeInForce,
        'trigger': 'stop',
        'side': 'buy'
        }

        url = "https://api.robinhood.com/orders/"
        res_json = None
        try:
            res = self.session.post(url,data=data)
            res.raise_for_status()
            res_json = res.json()
        except:
            raise

        return(res_json)

    def order_buy_stop_limit(self,symbol,quantity,limitPrice,stopPrice,timeInForce='gtc'):
        '''
        Summary
        -------
        Sets a stop limit order to buy a certain quantity of a stock.

        Parameters
        ----------
        symbol : string
            The symbol of the stock as a string.
        quantity : int
            The amount to buy of the stock as an integer.
        limitPrice: int
            The limit price to pay once the stop has triggered.
        stopPrice: int
            The price above the current price that converts your order to limit order.
        timeInForce : string, optional
            Changes how long the order will be in effect forself. 'gtc' = good until cancelled.
            'gfd' = good for the day. 'ioc' = immediate or cancel. 'opg' execute at opening.

        Returns
        -------
        Dictionary
            Contains information regarding the purchase of stocks, such as the order id, the state of order (queued,confired,filled, failed, canceled, etc.),
            the price, and the quantity.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return(None)

        if (type(timeInForce) is not str):
            print(self.error_not_a_string(timeInForce))
            return(None)

        if (type(quantity) is not int):
            print(self.error_not_a_integer(quantity))
            return(None)
        elif (quantity < 1):
            print(self.error_must_be_nonzero(quantity))
            return(None)

        if (type(limitPrice) is not int and type(limitPrice) is not float):
            print(self.error_not_a_integer_or_float(limitPrice))
            return(None)

        if (type(stopPrice) is not int and type(stopPrice) is not float):
            print(self.error_not_a_integer_or_float(stopPrice))
            return(None)

        latestPrice = float(self.get_latest_price(symbol)[0])
        symbol = symbol.upper()

        if (latestPrice > stopPrice):
            print('Error: stopPrice must be above the current price.')
            return(None)

        data = {
        'account': self.get_accounts_profile(info='url'),
        'instrument': self.get_instruments_by_symbols(symbol,info='url')[0],
        'symbol': symbol,
        'price': limitPrice,
        'quantity': quantity,
        'type': 'limit',
        'stop_price': stopPrice,
        'time_in_force': timeInForce,
        'trigger': 'stop',
        'side': 'buy'
        }

        url = "https://api.robinhood.com/orders/"
        res_json = None
        try:
            res = self.session.post(url,data=data)
            res.raise_for_status()
            res_json = res.json()
        except:
            raise

        return(res_json)

    def order_sell_market(self,symbol,quantity,timeInForce='gtc'):
        '''
        Summary
        -------
        Sells a certain quantity of a stock.

        Parameters
        ----------
        symbol : string
            The symbol of the stock as a string.
        quantity : int
            The amount to sell of the stock as an integer.
        timeInForce : string, optional
            Changes how long the order will be in effect forself. 'gtc' = good until cancelled.
            'gfd' = good for the day. 'ioc' = immediate or cancel. 'opg' execute at opening.

        Returns
        -------
        Dictionary
            Contains information regarding the selling of stocks, such as the order id, the state of order (queued,confired,filled, failed, canceled, etc.),
            the price, and the quantity.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return(None)

        if (type(timeInForce) is not str):
            print(self.error_not_a_string(timeInForce))
            return(None)

        if (type(quantity) is not int):
            print(self.error_not_a_integer(quantity))
            return(None)
        elif (quantity < 1):
            print(self.error_must_be_nonzero(quantity))
            return(None)

        symbol = symbol.upper()

        data = {
        'account': self.get_accounts_profile(info='url'),
        'instrument': self.get_instruments_by_symbols(symbol,info='url')[0],
        'symbol': symbol,
        'price': float(self.get_latest_price(symbol)[0]),
        'quantity': quantity,
        'type': 'market',
        'stop_price': None,
        'time_in_force': timeInForce,
        'trigger': 'immediate',
        'side': 'sell'
        }

        url = "https://api.robinhood.com/orders/"
        res_json = None
        try:
            res = self.session.post(url,data=data)
            res.raise_for_status()
            res_json = res.json()
        except:
            raise

        return(res_json)

    def order_sell_limit(self,symbol,quantity,limitPrice,timeInForce='gtc'):
        '''
        Summary
        -------
        Sets a limit order to sell a certain quantity of a stock.

        Parameters
        ----------
        symbol : string
            The symbol of the stock as a string.
        quantity : int
            The amount to sell of the stock as an integer.
        limitPrice: int
            The amount you are willing to sell the stock for.
        timeInForce : string, optional
            Changes how long the order will be in effect forself. 'gtc' = good until cancelled.
            'gfd' = good for the day. 'ioc' = immediate or cancel. 'opg' execute at opening.

        Returns
        -------
        Dictionary
            Contains information regarding the selling of stocks, such as the order id, the state of order (queued,confired,filled, failed, canceled, etc.),
            the price, and the quantity.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return(None)

        if (type(timeInForce) is not str):
            print(self.error_not_a_string(timeInForce))
            return(None)

        if (type(quantity) is not int):
            print(self.error_not_a_integer(quantity))
            return(None)
        elif (quantity < 1):
            print(self.error_must_be_nonzero(quantity))
            return(None)

        if (type(limitPrice) is not int and type(limitPrice) is not float):
            print(self.error_not_a_integer_or_float(limitPrice))
            return(None)

        symbol = symbol.upper()

        data = {
        'account': self.get_accounts_profile(info='url'),
        'instrument': self.get_instruments_by_symbols(symbol,info='url')[0],
        'symbol': symbol,
        'price': limitPrice,
        'quantity': quantity,
        'type': 'limit',
        'stop_price': None,
        'time_in_force': timeInForce,
        'trigger': 'immediate',
        'side': 'sell'
        }

        url = "https://api.robinhood.com/orders/"
        res_json = None
        try:
            res = self.session.post(url,data=data)
            res.raise_for_status()
            res_json = res.json()
        except:
            raise

        return(res_json)

    def order_sell_stop_loss(self,symbol,quantity,stopPrice,timeInForce='gtc'):
        '''
        Summary
        -------
        Sets a stop loss order to sell a certain quantity of a stock.

        Parameters
        ----------
        symbol : string
            The symbol of the stock as a string.
        quantity : int
            The amount to sell of the stock as an integer.
        stopPrice: int
            The price below the current price that converts your order to market order.
        timeInForce : string, optional
            Changes how long the order will be in effect forself. 'gtc' = good until cancelled.
            'gfd' = good for the day. 'ioc' = immediate or cancel. 'opg' execute at opening.

        Returns
        -------
        Dictionary
            Contains information regarding the selling of stocks, such as the order id, the state of order (queued,confired,filled, failed, canceled, etc.),
            the price, and the quantity.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return(None)

        if (type(timeInForce) is not str):
            print(self.error_not_a_string(timeInForce))
            return(None)

        if (type(quantity) is not int):
            print(self.error_not_a_integer(quantity))
            return(None)
        elif (quantity < 1):
            print(self.error_must_be_nonzero(quantity))
            return(None)

        if (type(stopPrice) is not int and type(stopPrice) is not float):
            print(self.error_not_a_integer_or_float(stopPrice))
            return(None)

        latestPrice = float(self.get_latest_price(symbol)[0])
        symbol = symbol.upper()

        if (latestPrice < stopPrice):
            print('Error: stopPrice must be below the current price.')
            return(None)

        data = {
        'account': self.get_accounts_profile(info='url'),
        'instrument': self.get_instruments_by_symbols(symbol,info='url')[0],
        'symbol': symbol,
        'price': stopPrice,
        'quantity': quantity,
        'type': 'market',
        'stop_price': stopPrice,
        'time_in_force': timeInForce,
        'trigger': 'stop',
        'side': 'sell'
        }

        url = "https://api.robinhood.com/orders/"
        res_json = None
        try:
            res = self.session.post(url,data=data)
            res.raise_for_status()
            res_json = res.json()
        except:
            raise

        return(res_json)

    def order_sell_stop_limit(self,symbol,quantity,limitPrice,stopPrice,timeInForce='gtc'):
        '''
        Summary
        -------
        Sets a stop limit order to sell a certain quantity of a stock.

        Parameters
        ----------
        symbol : string
            The symbol of the stock as a string.
        quantity : int
            The amount to sell of the stock as an integer.
        limitPrice: int
            The limit price to sell for once the stop has triggered.
        stopPrice: int
            The price below the current price that converts your order to limit order.
        timeInForce : string, optional
            Changes how long the order will be in effect forself. 'gtc' = good until cancelled.
            'gfd' = good for the day. 'ioc' = immediate or cancel. 'opg' execute at opening.

        Returns
        -------
        Dictionary
            Contains information regarding the purchase of stocks, such as the order id, the state of order (queued,confired,filled, failed, canceled, etc.),
            the price, and the quantity.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return(None)

        if (type(timeInForce) is not str):
            print(self.error_not_a_string(timeInForce))
            return(None)

        if (type(quantity) is not int):
            print(self.error_not_a_integer(quantity))
            return(None)
        elif (quantity < 1):
            print(self.error_must_be_nonzero(quantity))
            return(None)

        if (type(limitPrice) is not int and type(limitPrice) is not float):
            print(self.error_not_a_integer_or_float(limitPrice))
            return(None)

        if (type(stopPrice) is not int and type(stopPrice) is not float):
            print(self.error_not_a_integer_or_float(stopPrice))
            return(None)

        latestPrice = float(self.get_latest_price(symbol)[0])
        symbol = symbol.upper()

        if (latestPrice < stopPrice):
            print('Error: stopPrice must be below the current price.')
            return(None)

        data = {
        'account': self.get_accounts_profile(info='url'),
        'instrument': self.get_instruments_by_symbols(symbol,info='url')[0],
        'symbol': symbol,
        'price': limitPrice,
        'quantity': quantity,
        'type': 'limit',
        'stop_price': stopPrice,
        'time_in_force': timeInForce,
        'trigger': 'stop',
        'side': 'sell'
        }

        url = "https://api.robinhood.com/orders/"
        res_json = None
        try:
            res = self.session.post(url,data=data)
            res.raise_for_status()
            res_json = res.json()
        except:
            raise

        return(res_json)

    def order(self,symbol,quantity,orderType,limitPrice,stopPrice,trigger,side,timeInForce):
        '''
        Summary
        -------
        A generic order function. All parameters must be supplied.

        Parameters
        ----------
        symbol : string
            The symbol of the stock as a string.
        quantity : int
            The amount to buy of the stock as an integer.
        orderType: string
            Either 'market' or 'limit'
        limitPrice: int
            The limit price to pay once the stop has triggered.
        stopPrice: int
            The price above the current price that converts your order to limit order.
        trigger: string
            Either 'immediate' or 'stop'
        side : string
            Either 'buy' or 'sell'
        timeInForce : string
            Changes how long the order will be in effect forself. 'gtc' = good until cancelled.
            'gfd' = good for the day. 'ioc' = immediate or cancel. 'opg' execute at opening.

        Returns
        -------
        Dictionary
            Contains information regarding the purchase of stocks, such as the order id, the state of order (queued,confired,filled, failed, canceled, etc.),
            the price, and the quantity.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return(None)

        if (type(timeInForce) is not str):
            print(self.error_not_a_string(timeInForce))
            return(None)

        if (type(quantity) is not int):
            print(self.error_not_a_integer(quantity))
            return(None)
        elif (quantity < 1):
            print(self.error_must_be_nonzero(quantity))
            return(None)

        if (type(limitPrice) is not int and type(limitPrice) is not float):
            print(self.error_not_a_integer_or_float(limitPrice))
            return(None)

        if (type(stopPrice) is not int and type(stopPrice) is not float):
            print(self.error_not_a_integer_or_float(stopPrice))
            return(None)

        if (type(trigger) is not str):
            print(self.error_not_a_string(trigger))
            return(None)

        if (type(side) is not str):
            print(self.error_not_a_string(side))
            return(None)

        latestPrice = float(self.get_latest_price(symbol)[0])
        symbol = symbol.upper()

        data = {
        'account': self.get_accounts_profile(info='url'),
        'instrument': self.get_instruments_by_symbols(symbol,info='url')[0],
        'symbol': symbol,
        'price': limitPrice,
        'quantity': quantity,
        'type': orderType,
        'stop_price': stopPrice,
        'time_in_force': timeInForce,
        'trigger': trigger,
        'side': side
        }

        url = "https://api.robinhood.com/orders/"
        res_json = None
        try:
            res = self.session.post(url,data=data)
            res.raise_for_status()
            res_json = res.json()
        except:
            raise

        return(res_json)


    def get_aggregate_positions(self,info=None):
        '''
        Summary
        -------
        Collapses all like option orders into a single dictionary.

        Parameters
        ----------
        info : string,optional
            Will filter the results.

        Returns
        -------
        list
            Returns a list of items.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        url = 'https://api.robinhood.com/options/aggregate_positions/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        return(self.filter(res_data,info))

    def get_market_options(self,info=None):
        '''
        Summary
        -------
        Gets a list of all options.

        Parameters
        ----------
        info : string,optional
            Will filter the results.

        Returns
        -------
        list
            Returns a list of items.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        url = 'https://api.robinhood.com/options/orders/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        return(self.filter(res_data,info))

    def get_open_option_positions(self,info=None):
        '''
        Summary
        -------
        Returns all open option positions for the account.

        Parameters
        ----------
        info : string,optional
            Will filter the results.

        Returns
        -------
        list
            Returns a list of items.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        url = 'https://api.robinhood.com/options/positions/?nonzero=True'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        return(self.filter(res_data,info))

    def get_all_option_positions(self,info=None):
        '''
        Summary
        -------
        Returns all option positions ever held.

        Parameters
        ----------
        info : string,optional
            Will filter the results.

        Returns
        -------
        list
            Returns a list of items.

        '''
        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        url = 'https://api.robinhood.com/options/positions/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        return(self.filter(res_data,info))

    def get_chains(self,symbol,info=None):
        '''
        Summary
        -------
        Returns the chain information of an option.

        Parameters
        ----------
        symbol : string
            This represents a stock ticker.
        info : string,optional
            Will filter the results.

        Returns
        -------
        dictionary
            Returns option information for the ticker.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return(None)

        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return(None)

        symbol = symbol.upper()
        url = 'https://api.robinhood.com/options/chains/'+self.get_tradable_chain_id(symbol)+'/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return(None)

        return(self.filter(res_data,info))

    def find_options_for_stock_by_expiration(self,symbol,expirationDate,optionType='both'):
        '''
        Summary
        -------
        Returns a list of all the option orders that match the seach parameters

        Parameters
        ----------
        symbol : string
            This represents a stock ticker.
        expriationDate : string
            This represents expiration date in the format YYYY-MM-DD.
        optionType : string, optional
            Can be either call or put

        Returns
        -------
        list
            Returns a list of all the option orders that match.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return([None])

        if (type(expirationDate) is not str):
            print(self.error_not_a_string(expirationDate))
            return([None])

        if (type(optionType) is not str):
            print(self.error_not_a_string(optionType))
            return([None])

        symbol = symbol.upper()
        optionType = optionType.lower()
        if (optionType == 'call'):
            calls = self.get_available_option_calls(symbol)
            listOfCalls = [item for item in calls if item["expiration_date"] == expirationDate]
            mergedList = listOfCalls
        elif (optionType == 'put'):
            puts = self.get_available_option_puts(symbol)
            listOfPuts = [item for item in puts if item["expiration_date"] == expirationDate]
            mergedList = listOfPuts
        else:
            calls = self.get_available_option_calls(symbol)
            puts = self.get_available_option_puts(symbol)
            listOfCalls = [item for item in calls if item["expiration_date"] == expirationDate]
            listOfPuts = [item for item in puts if item["expiration_date"] == expirationDate]
            mergedList = listOfCalls + listOfPuts

        return(mergedList)

    def find_options_for_stock_by_strike(self,symbol,strike,optionType='both'):
        '''
        Summary
        -------
        Returns a list of all the option orders that match the seach parameters

        Parameters
        ----------
        symbol : string
            This represents a stock ticker.
        strike : string
            This represents a price of the option as a string.
        optionType : string, optional
            Can be either call or put

        Returns
        -------
        list
            Returns a list of all the option orders that match.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return([None])

        if (type(strike) is not int):
            print(self.error_not_a_string(strike))
            return([None])

        if (type(optionType) is not str):
            print(self.error_not_a_string(optionType))
            return([None])

        symbol = symbol.upper()
        optionType = optionType.lower()
        if (optionType == 'call'):
            calls = self.get_available_option_calls(symbol)
            listOfCalls = [item for item in calls if float(item["strike_price"])== float(strike)]
            mergedList = listOfCalls
        elif (optionType == 'put'):
            puts = self.get_available_option_puts(symbol)
            listOfPuts = [item for item in puts if float(item["strike_price"])== float(strike)]
            mergedList = listOfPuts
        else:
            calls = self.get_available_option_calls(symbol)
            puts = self.get_available_option_puts(symbol)
            listOfCalls = [item for item in calls if float(item["strike_price"])== float(strike)]
            listOfPuts = [item for item in puts if float(item["strike_price"])== float(strike)]
            mergedList = listOfCalls + listOfPuts

        return(mergedList)

    def find_options_for_stock_by_expiration_and_strike(self,symbol,expirationDate,strike,optionType='both'):
        '''
        Summary
        -------
        Returns a list of all the option orders that match the seach parameters

        Parameters
        ----------
        symbol : string
            This represents a stock ticker.
        expriationDate : string
            This represents expiration date in the format YYYY-MM-DD.
        strike : string
            This represents a price of the option as a string.
        optionType : string, optional
            Can be either call or put

        Returns
        -------
        list
            Returns a list of all the option orders that match.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return([None])

        if (type(expirationDate) is not str):
            print(self.error_not_a_string(expirationDate))
            return([None])

        if (type(strike) is not int):
            print(self.error_not_a_string(strike))
            return([None])

        if (type(optionType) is not str):
            print(self.error_not_a_string(optionType))
            return([None])

        symbol = symbol.upper()
        optionType = optionType.lower()
        if (optionType == 'call'):
            calls = self.get_available_option_calls(symbol)
            listOfCalls = [item for item in calls if item["expiration_date"] == expirationDate and float(item["strike_price"])== float(strike)]
            mergedList = listOfCalls
        elif (optionType == 'put'):
            puts = self.get_available_option_puts(symbol)
            listOfPuts = [item for item in puts if item["expiration_date"] == expirationDate and float(item["strike_price"])== float(strike)]
            mergedList = listOfPuts
        else:
            calls = self.get_available_option_calls(symbol)
            puts = self.get_available_option_puts(symbol)
            listOfCalls = [item for item in calls if item["expiration_date"] == expirationDate and float(item["strike_price"])== float(strike)]
            listOfPuts = [item for item in puts if item["expiration_date"] == expirationDate and float(item["strike_price"])== float(strike)]
            mergedList = listOfCalls + listOfPuts

        return(mergedList)

    def find_options_for_all_stocks_by_expiration_date(self,expirationDate,side=None):
        ''''
        NOT WORKING

        '''
        if (type(expirationDate) is not str):
            print(self.error_not_a_string(expirationDate))
            return([None])

        if (type(side) is not str and side is not None):
            print(self.error_not_a_string(side))
            return([None])

        symbol = symbol.upper()
        side = side.lower()
        if (side == 'put' or side == 'call' ):
            url = 'https://api.robinhood.com/options/instruments/expiration_date='+expirationDate+'&state=active&tradability=tradable&type='+side
        else:
            url = 'https://api.robinhood.com/options/instruments/expiration_date='+expirationDate+'&state=active&tradability=tradable'

        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        return(res_data)

    def get_available_option_calls(self,symbol,info=None):
        ''''
        Summary
        -------
        Returns a list of all available option calls for a stock.

        Parameters
        ----------
        symbol : string
            This represents a stock ticker.
        info : string,optional
            Will filter the results.

        Returns
        -------
        list
            Returns a list of all the option orders that match.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return([None])

        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        symbol = symbol.upper()
        url = 'https://api.robinhood.com/options/instruments/?chain_id='+self.get_tradable_chain_id(symbol)+'&state=active&tradability=tradable&type=call'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        return(self.filter(res_data,info))

    def get_available_option_puts(self,symbol,info=None):
        ''''
        Summary
        -------
        Returns a list of all available option puts for a stock.

        Parameters
        ----------
        symbol : string
            This represents a stock ticker.
        info : string,optional
            Will filter the results.

        Returns
        -------
        list
            Returns a list of all the option orders that match.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return([None])

        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        symbol = symbol.upper()
        url = 'https://api.robinhood.com/options/instruments/?chain_id='+self.get_tradable_chain_id(symbol)+'&state=active&tradability=tradable&type=put'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()['results']
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        res_data = self.append_dataset_with_pagination(res,res_data)

        return(self.filter(res_data,info))

    def get_specific_option_market_data(self,symbol,expirationDate,strike,optionType,info=None):
        '''
        Summary
        -------
        Returns the option order information, including the greeks, open interest, change of profit, and adjusted mark price.

        Parameters
        ----------
        symbol : string
            This represents a stock ticker.
        expriationDate : string
            This represents expiration date in the format YYYY-MM-DD.
        strike : string
            This represents a price of the option as an integer.
        optionType : string
            Can be either call or put
        info : string,optional
            Will filter the results.

        Returns
        -------
        dictionary
            Returns a dictionary of key/value pairs.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return([None])

        if (type(expirationDate) is not str):
            print(self.error_not_a_string(expirationDate))
            return([None])

        if (type(strike) is not int):
            print(self.error_not_a_string(strike))
            return([None])

        if (type(optionType) is not str):
            print(self.error_not_a_string(optionType))
            return([None])

        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        symbol = symbol.upper()
        optionType = optionType.lower()
        optionID= self.get_specific_option_id(symbol,expirationDate,strike,optionType)
        url = 'https://api.robinhood.com/marketdata/options/'+optionID+'/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        return(self.filter(res_data,info))

    def get_specific_option_instrument_data(self,symbol,expirationDate,strike,optionType,info=None):
        '''
        Summary
        -------
        Returns the option order information, including the greeks, open interest, change of profit, and adjusted mark price.

        Parameters
        ----------
        symbol : string
            This represents a stock ticker.
        expriationDate : string
            This represents expiration date in the format YYYY-MM-DD.
        strike : string
            This represents a price of the option as an integer.
        optionType : string
            Can be either call or put
        info : string,optional
            Will filter the results.

        Returns
        -------
        dictionary
            Returns a dictionary of key/value pairs.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return([None])

        if (type(expirationDate) is not str):
            print(self.error_not_a_string(expirationDate))
            return([None])

        if (type(strike) is not int):
            print(self.error_not_a_string(strike))
            return([None])

        if (type(optionType) is not str):
            print(self.error_not_a_string(optionType))
            return([None])

        if (type(info) is not str and info is not None):
            print(self.error_not_a_string(info))
            return([None])

        symbol = symbol.upper()
        optionType = optionType.lower()
        optionID= self.get_specific_option_id(symbol,expirationDate,strike,optionType)
        url = 'https://api.robinhood.com/options/instruments/'+optionID+'/'
        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        return(self.filter(res_data,info))

    def get_option_historicals(self,symbol,expirationDate,strike,optionType,span='week'):
        '''
        Summary
        -------
        Represents the data that is used to make the graphs.

        Parameters
        ----------
        symbol : string
            The option of the stock for the option.
        span : string, optional
            Sets the range of the data to be either 'day', 'week', 'year', or '5year'. Default is 'week'.
        bounds : string,optional
            Represents if graph will include extended trading hours or just regular trading hours. Values are 'extended' or 'regular'.

        Returns
        -------
        List of Lists
            Returns a list that contains a list for each symbol. Each list contains a dictionary where each dictionary is for a different time.

        '''
        if (type(symbol) is not str):
            print(self.error_not_a_string(symbol))
            return([None])

        if (type(expirationDate) is not str):
            print(self.error_not_a_string(expirationDate))
            return([None])

        if (type(strike) is not int):
            print(self.error_not_a_string(strike))
            return([None])

        if (type(optionType) is not str):
            print(self.error_not_a_string(optionType))
            return([None])

        if (type(span) is not str):
            print(self.error_not_a_string(span))
            return([None])

        symbol = symbol.upper()
        optionType = optionType.lower()
        span_check = ['day','week','year','5year']
        if span not in span_check:
            print('ERROR: Span must be "day","week","year",or "5year"')
            return([None])

        if span == 'day':
            interval = '5minute'
        elif span == 'week':
            interval = '10minute'
        elif span == 'year':
            interval = 'day'
        else:
            interval = 'week'

        optionID = self.get_specific_option_id_alternative(symbol,expirationDate,strike,optionType)

        url = 'https://api.robinhood.com/marketdata/options/historicals/'+optionID+'/?span='+span+'&interval='+interval

        try:
            res = self.session.get(url)
            res.raise_for_status()
            res_data = res.json()
        except:
            print(self.error_api_endpoint_not_loaded(url))
            return([None])

        return(res_data)

    def build_holdings(self):
        '''
        Summary
        -------
        Builds a dictionary of important information regarding the stocks and positions owned by the user.

        Returns
        -------
        dictionary
            Returns a dictionary of key/value pairs.
        '''

        holdings = {}
        positions_data = self.get_owned_positions()
        for item in positions_data:
            instrument_data = self.get_instrument_by_url(item['instrument'])
            symbol = instrument_data['symbol']
            price           = self.get_latest_price(instrument_data['symbol'])[0]
            quantity        = item['quantity']
            equity          = float(item['quantity'])*float(price)
            if (float(item['average_buy_price']) == 0.0):
                percent_change = 0.0
            else:
                percent_change  = (float(price)-float(item['average_buy_price']))*100/float(item['average_buy_price'])
            #
            holdings[symbol]=({'price': price })
            holdings[symbol].update({'quantity': quantity})
            holdings[symbol].update({'average_buy_price': item['average_buy_price']})
            holdings[symbol].update({'equity':"{0:.2f}".format(equity)})
            holdings[symbol].update({'percent_change': "{0:.2f}".format(percent_change)})
            holdings[symbol].update({'id': instrument_data['id']})

        return(holdings)

    def build_user_profile(self):
        '''
        Summary
        -------
        Builds a dictionary of important information regarding the user account.

        Returns
        -------
        dictionary
            Returns a dictionary of key/value pairs.
        '''
        user = {}

        portfolios_data = self.get_portfolios_profile()
        accounts_data = self.get_accounts_profile()

        user['equity'] = portfolios_data['equity']
        user['extended_hours_equity'] = portfolios_data['extended_hours_equity']

        cash = "{0:.2f}".format(float(accounts_data['cash'])+float(accounts_data['uncleared_deposits']))
        user['cash'] = cash

        user['dividend_total'] = self.get_total_dividends()

        return(user)
    
    
    