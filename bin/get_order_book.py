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


def unpack_orderbook(orderbook):
    all_orders = []

    for order_type in order_types:
        orders = orderbook[order_type]
        for order in orders:
            all_orders.append(order)

    return all_orders

def parse_order(order):
    row = {
        'contract_id': order['contractId'],
        'trade_type': order['tradeType'],
        'price_per_share': order['pricePerShare'],
        'cost_per_share_yes': order['costPerShareYes'],
        'cost_per_share_no': order['costPerShareNo'],
        'quantity' : order['quantity'],
        }
    return row


if __name__ == '__main__':
    run_id = utils.generate_run_id()

    contracts = utils.get_list_from_db(settings.QUERY_GET_CONTRACTS)
    access_token = get_authorization_token()
    headers = {'Authorization': 'Bearer {access_token}'.format(access_token=access_token)}
    headers.update(settings.HEADERS_PREDICTIT)
    import ipdb; ipdb.set_trace()

    for contract_id in contracts:
        try:
            date_added = utils.right_now()
            data = requests.get(settings.URL_ORDER_BOOKS.format(contract_id=contract_id), headers=headers).json()
            orders = unpack_orderbook(data)
            for order in orders:
                row = parse_order(order)
                bundled_data = utils.bundled_data(date_added, run_id)
                row.update(bundled_data)
                utils.write_to_database(row, settings.QUERY_INSERT_ORDERS)
        except Exception as e:
            print(e)
