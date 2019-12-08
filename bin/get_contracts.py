import datetime
import requests
import sys

sys.path.append("../source")

import private
import settings
import utils

def parse_contracts(data):
    row = {
        'contract_id': data['contractId'],
        'contract_name': data['contractName'],
        'market_id': data['marketId'],
        'market_name': data['marketName'],
        'is_active': data['isActive'],
        'is_open': data['isOpen'],
    }
    return row


if __name__ == '__main__':
    run_id = utils.generate_run_id()

    for market_id in settings.ALL_MARKET_IDS:
        try:
            date_added = utils.right_now()
            contracts = requests.get(settings.URL_CONTRACTS.format(market_id=market_id)).json()
            for contract in contracts:
                row = parse_contracts(contract)
                bundled_data = utils.bundled_data(date_added, run_id)
                row.update(bundled_data)
                utils.write_to_database(row, settings.QUERY_INSERT_CONTRACTS)
        except Exception as e:
            pass
