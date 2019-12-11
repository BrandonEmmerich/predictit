import datetime
import requests
import sys

sys.path.append("../source")

import private
import settings
import utils

params = (
    ('timespan', '24h'),
    ('maxContracts', '50'),
    ('showHidden', 'true'),
)

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

    access_token = utils.get_authorization_token()
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
