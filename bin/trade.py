import datetime
import requests
import sys

sys.path.append("../source")

import private
import settings
import utils


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

def parse_trade_data(trade_data):
    row = {
        'contract_id': trade_data['contractId'],
        'price_per_share': trade_data['pricePerShare'],
        'quantity': trade_data['quantity'],
        'trade_type': trade_data['tradeType'],
    }
    return row

def get_trades():
    '''
    Do stuff to get a list of dictionaries, which are the trades to execute.
    For now, just get a sample sell Yes Joe Biden and Buy Yes Joe Biden, the
    first should fail the second should be successful.
    '''
    contract_id = '7729'
    buy_price = utils.get_object_from_db(settings.QUERY_GET_BUY_PRICE.format(contract_id=contract_id))

    trades = []

    for trade_type in ['3', '1']:
        trade_data = {
          'quantity': '1',
          'pricePerShare': str(buy_price),
          'contractId': contract_id,
          'tradeType': trade_type
        }
        trades.append(trade_data)

    return trades

def submit_trade(trade_data):
    response = requests.post(settings.URL_SUBMIT_TRADE, headers=headers, data=trade_data)
    return response

if __name__ == '__main__':
    run_id = utils.generate_run_id()

    access_token = utils.get_authorization_token()
    headers = {'Authorization': 'Bearer {access_token}'.format(access_token=access_token)}
    headers.update(settings.HEADERS_PREDICTIT)

    trades = get_trades()
    import ipdb; ipdb.set_trace()

    for trade_data in trades:
        date_added = utils.right_now()
        response = submit_trade(trade_data)

        if response.ok == True:
            row = parse_offer(response.json()['offer'])
            bundled_data = utils.bundled_data(date_added, run_id)
            row.update(bundled_data)
            utils.write_to_database(row, settings.QUERY_INSERT_TRADE)

        else:
            row = parse_trade_data(trade_data)
            bundled_data = utils.bundled_data(date_added, run_id)
            row.update(bundled_data)
            row.update({'message': response.json()['message']})
            utils.write_to_database(row, settings.QUERY_INSERT_FAILED_TRADE)
