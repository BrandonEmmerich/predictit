import datetime
import requests
import sys

sys.path.append("../source")

import private
import settings
import utils

order_types = ['yesOrders', 'noOrders']

params = (
    ('timespan', '24h'),
    ('maxContracts', '50'),
    ('showHidden', 'true'),
)

def get_authorization_token():
    data = {
        'email': private.PREDICTIT_EMAIL,
        'password': private.PREDICTIT_PASSWORD,
        'grant_type': 'password',
        'rememberMe': 'true'
    }
    response = requests.post('https://www.predictit.org/api/Account/token', data=data)
    access_token = response.json()['access_token']
    return access_token


def parse_market_data(data):
    row = {
        'market_id': data['marketId'],
        'contract_id': data['contractId'],
        'contract_name': data['contractName'],
        'data_timestamp': data['date'],
        'open': data['openSharePrice'],
        'high': data['highSharePrice'],
        'low': data['lowSharePrice'],
        'close_price': data['closeSharePrice'],
        'volume': data['tradeVolume'],
        }
    return row

if __name__ == '__main__':
    run_id = utils.generate_run_id()

    access_token = get_authorization_token()
    headers = {'Authorization': 'Bearer {access_token}'.format(access_token=access_token)}
    headers.update(settings.HEADERS_PREDICTIT)

    for market_id in settings.ALL_MARKET_IDS:
        try:
            date_added = utils.right_now()
            market_data = requests.get(settings.URL_MARKET_DATA.format(market_id=market_id), headers=headers, params=params).json()
            for tick in market_data:
                row = parse_market_data(tick)
                bundled_data = utils.bundled_data(date_added, run_id)
                row.update(bundled_data)
                utils.write_to_database(row, settings.QUERY_INSERT_MARKET_DATA)
        except Exception as e:
            print(e)
