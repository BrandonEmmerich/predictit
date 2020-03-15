
HEADERS_PREDICTIT = {
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
}

QUERY_GET_MARKET_IDS = '''
    select market_id
    from predictit.tweeting_markets
    where run_id = (select max(run_id) from predictit.tweeting_markets)
    	and market_status = 'Open'
    '''

QUERY_INSERT_TWEETING_MARKETS = '''
    INSERT INTO predictit.tweeting_markets
    (run_id, date_added, market_id, market_name, total_shares_traded, market_status, total_trades)
    VALUES
    (%(run_id)s, %(date_added)s, %(market_id)s, %(market_name)s, %(total_shares_traded)s, %(market_status)s, %(total_trades)s)
    '''

QUERY_INSERT_PRICES = '''
    INSERT INTO predictit.prices
    (run_id, date_added, contract_id, contract_name, market_id, is_active, is_open, best_yes_price, best_yes_quantity, best_no_price, best_no_quantity, is_trading_suspended, date_opened)
    VALUES
    (%(run_id)s, %(date_added)s, %(contract_id)s, %(contract_name)s, %(market_id)s, %(is_active)s, %(is_open)s, %(best_yes_price)s, %(best_yes_quantity)s, %(best_no_price)s, %(best_no_quantity)s, %(is_trading_suspended)s, %(date_opened)s)
    '''
