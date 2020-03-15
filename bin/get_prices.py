import datetime
import requests
import sys

sys.path.append("../source")

import private
import settings
import utils

def parse_contracts(contract):
    row = {
        'contract_id': contract['contractId'],
        'contract_name': contract['contractName'],
        'market_id': contract['marketId'],
        'is_active': contract['isActive'],
        'is_open': contract['isOpen'],
        'best_yes_price': contract['bestYesPrice'],
        'best_yes_quantity': contract['bestYesQuantity'],
        'best_no_price': contract['bestNoPrice'],
        'best_no_quantity': contract['bestNoQuantity'],
        'is_trading_suspended': contract['isTradingSuspended'],
        'date_opened': contract['dateOpened']
    }

    return row


if __name__ == '__main__':
    run_id = utils.generate_run_id()
    date_added = utils.right_now()
    market_ids = utils.get_list_from_db(settings.QUERY_GET_MARKET_IDS)

    for market_id in market_ids:
        response = requests.get('https://www.predictit.org/api/Market/{}/Contracts'.format(market_id))
        for contract in response.json():
            row = parse_contracts(contract)
            bundled_data = utils.bundled_data(date_added, run_id)
            row.update(bundled_data)
            utils.write_to_database(row, settings.QUERY_INSERT_PRICES)
