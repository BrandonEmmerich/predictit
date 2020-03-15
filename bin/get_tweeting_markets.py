import datetime
import requests
import sys

sys.path.append("../source")

import private
import settings
import utils

def parse_markets(data):
    row = {
        'market_id': data['marketId'],
        'market_name': data['marketName'],
        'total_shares_traded': data['totalSharesTraded'],
        'total_trades': data['totalTrades'],
        'market_status': data['status']
    }
    return row

params = (
    ('page', '1'),
    ('itemsPerPage', '30'),
)


if __name__ == '__main__':
    run_id = utils.generate_run_id()
    date_added = utils.right_now()
    response = requests.get('https://www.predictit.org/api/Browse/Search/twitter',params=params, headers=settings.HEADERS_PREDICTIT)

    for data in response.json()['markets']:
        row = parse_markets(data)
        bundled_data = utils.bundled_data(date_added, run_id)
        row.update(bundled_data)
        utils.write_to_database(row, settings.QUERY_INSERT_TWEETING_MARKETS)
