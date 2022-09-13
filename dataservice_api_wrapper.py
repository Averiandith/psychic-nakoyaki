# 9th/Sept/2022
# Data Service API wrapper by Victor & Yen Wee

# Steps:
# 1) python -m pip install --index-url https://pypi.garenanow.com/simple datasuite-dataservice-sdk-python
# 2) pip install pycryptodome
# 3) if there's error regarding Crypto not found, head to the following directory "C:\Users\your.name\Anaconda3\Lib\site-packages" and rename "crypto" folder to "Crypto"

from dataservice.sdk import Client
from dataservice.body import Body, Expressions
import pandas as pd
from pandas import DataFrame
from time import sleep
from datetime import datetime, timedelta


class ClientWrapper:
    def __init__(self) -> None:
        """
        Client app key and secret credentials can be found here:
        https://datasuite.shopee.io/dataservice/ds_app_management
        
        Client initialisation with our project keys: Intranet (internal usage only)
        """
        self.client = Client() \
            .create() \
            .env(Client.Env.LIVE) \
            .queryPattern(Client.QueryPattern.OLAP) \
            .appKey('team_app_key') \
            .appSecret('team_app_secret') \
            .refresh()

    def call_api_to_dataframe(self, api_abbr: str, version: str) -> DataFrame:
        """
        Retrieve data from api to DataFrame
        
        Our team's api can be found here:
        https://datasuite.shopee.io/dataservice/ds_api_management
        """
        expressions = Expressions().getExpressions()
        body = Body(expressions).__dict__

        data_df = pd.DataFrame()
        start = datetime.now()
        print(f"\nRetrieving data from API: {api_abbr}, Version: {version}...")

        while datetime.now() - start < timedelta(seconds=72000):
            try:
                data_dict = self.client.call(
                    api_abbr = api_abbr,
                    version = version,
                    queue = '',
                    body = body
                )

                for nested_data_dicts in data_dict:
                    data_dicts = [x['values'] for x in nested_data_dicts]
                    temp = pd.DataFrame(data_dicts)
                    data_df = pd.concat([data_df, temp], ignore_index = True, sort = False)

                print(f"Retrieved data from {api_abbr} successfully!")
                break
            
            except Exception as e:
                print(f"{datetime.now()} Error: {e}")
                sleep(300)

        return data_df

    def call_api_to_csv(self, api_abbr: str, version: str) -> None:
        """
        Retrieve data from api to csv
        
        Our team's api can be found here:
        https://datasuite.shopee.io/dataservice/ds_api_management
        """
        df = self.call_api_to_dataframe(api_abbr, version)
        
        try:
            df.to_csv(f"{api_abbr}.csv")
            print(f"Output to '{api_abbr}.csv' successfully")

        except Exception as e:
            print(f"Fail to output to csv, Error: {e}")


# Sample on how to use wrapper
# if __name__ == "__main__":
    # Step 1: Instantiate ClientWrapper Object
    # c = ClientWrapper()

    # Step 2: Call either function based on your needs (df or csv)
    # df = c.call_api_to_dataframe('mybi_others_rf.weekly_supplier_otif', 'version-number')
    # c.call_api_to_csv('mybi_others_rf.replenishment_tool', 'version-number')