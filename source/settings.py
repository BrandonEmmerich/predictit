ALL_MARKET_IDS = ['3633', '3698', '3537']

HEADERS_PREDICTIT = {
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
}

QUERY_GET_CONTRACTS = '''
    select distinct contract_id
    from predictit.contracts
    where is_active = TRUE
    '''

QUERY_INSERT_CONTRACTS = '''
    INSERT INTO predictit.contracts
    (contract_id, contract_name, market_id, market_name, date_added, run_id, is_active, is_open)
    VALUES
    (%(contract_id)s, %(contract_name)s, %(market_id)s, %(market_name)s, %(date_added)s, %(run_id)s, %(is_active)s, %(is_open)s)
    '''

QUERY_INSERT_ORDERS = '''
    INSERT INTO predictit.order_book
    (date_added, run_id, contract_id, trade_type, price_per_share, cost_per_share_yes, cost_per_share_no, quantity)
    VALUES
    (%(date_added)s, %(run_id)s, %(contract_id)s, %(trade_type)s, %(price_per_share)s, %(cost_per_share_yes)s, %(cost_per_share_no)s, %(quantity)s)
    '''

QUERY_INSERT_MARKET_DATA = '''
    INSERT INTO predictit.market_data
    (date_added, run_id, market_id, contract_id, contract_name, data_timestamp, open, high, low, close_price, volume)
    VALUES
    (%(date_added)s, %(run_id)s, %(market_id)s, %(contract_id)s, %(contract_name)s, %(data_timestamp)s, %(open)s, %(high)s, %(low)s, %(close_price)s, %(volume)s)
    '''

QUERY_INSERT_TRADE = '''
    INSERT INTO predictit.trade_log
    (run_id, date_added, contract_id, offer_id, price_per_share, remaining_quantity, quantity, trade_type, date_created, is_processed)
    VALUES
    (%(run_id)s, %(date_added)s, %(contract_id)s, %(offer_id)s, %(price_per_share)s, %(remaining_quantity)s, %(quantity)s, %(trade_type)s, %(date_created)s, %(is_processed)s)
    '''




URL_CONTRACTS = 'https://www.predictit.org/api/Market/{market_id}/Contracts'
URL_ORDER_BOOKS = 'https://www.predictit.org/api/Trade/{contract_id}/OrderBook'
URL_MARKET_DATA = 'https://www.predictit.org/api/Public/GetMarketChartData/{market_id}'
URL_SUBMIT_TRADE = 'https://www.predictit.org/api/Trade/SubmitTrade'
