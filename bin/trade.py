import datetime
import requests
import sys

sys.path.append("../source")

import private
import settings
import utils

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

def parse_offer(offer):
    row = {
        'offer_id': offer['offerId'],
        'contract_id': offer['contractId'],
        'price_per_share': offer['pricePerShare'],
        'quantity': offer['quantity'],
        'remaining_quantity': offer['remainingQuantity'],
        'trade_type': offer['tradeType'],
        'date_created': offer['dateCreated'],
        'is_processed': offer['isProcessed'],
    }
    return row

def submit_trade(trade_data):
    response = requests.post(settings.URL_SUBMIT_TRADE, headers=headers, data=trade_data)
    return response.json()['offer']

if __name__ == '__main__':
    run_id = utils.generate_run_id()

    access_token = get_authorization_token()
    headers = {'Authorization': 'Bearer {access_token}'.format(access_token=access_token)}
    headers.update(settings.HEADERS_PREDICTIT)

    contract_id = '7729'
    buy_price = utils.get_object_from_db(settings.QUERY_GET_BUY_PRICE.format(contract_id=contract_id))

    trade_data = {
      'quantity': '1',
      'pricePerShare': str(buy_price),
      'contractId': contract_id,
      'tradeType': '1'
    }

    date_added = utils.right_now()
    offer = submit_trade(trade_data)
    row = parse_offer(offer)
    bundled_data = utils.bundled_data(date_added, run_id)
    row.update(bundled_data)
    utils.write_to_database(row, settings.QUERY_INSERT_TRADE)
