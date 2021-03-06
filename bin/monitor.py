import datetime
import numpy as np
import pandas as pd
import random
import requests
import sys
import tweepy

sys.path.append("../source")

import private
import utils


def get_hour(timestamp):
    return timestamp.hour

def get_day_of_week(timestamp):
    return timestamp.weekday()

def get_year_week(timestamp):
    year = timestamp.year
    week = datetime.datetime.strftime(timestamp, '%V')
    return str(year) + '-' + str(week)

def convert_from_utc(timestamp):
    return timestamp - datetime.timedelta(hours=4)

def get_market_close(market_id):
    response = requests.get('https://www.predictit.org/api/Market/{}'.format(market_id))
    raw_timestamp = response.json()['dateEndString'].replace(' PM (ET)', '').replace('/', '-')
    market_close = datetime.datetime.strptime(raw_timestamp, '%m-%d-%Y %H:%M')

    return market_close

def get_market_open(market_id):
    response = requests.get('https://www.predictit.org/api/Market/{}'.format(market_id))
    raw_timestamp = response.json()['dateOpened'].split('.')[0]
    market_open = datetime.datetime.strptime(raw_timestamp, '%Y-%m-%dT%H:%M:%S')

    return market_open

def twitter_api():
    auth = tweepy.OAuthHandler(private.CONSUMER_KEY, private.CONSUMER_SECRET)
    auth.set_access_token(private.ACCESS_KEY, private.ACCESS_SECRET)
    api = tweepy.API(auth)

    return api

def get_twitter_market_id(twitter_handle):
    params = (
        ('page', '1'),
        ('itemsPerPage', '30'),
    )

    response = requests.get(f'https://www.predictit.org/api/Browse/Search/{twitter_handle}',params=params)

    return response.json()['markets'][0]['marketId']

def get_all_tweets(api, screen_name):
    all_tweets = []

    for status in tweepy.Cursor(api.user_timeline, screen_name=screen_name).items():
        row = {
            'id': status.id,
            'created_at': status.created_at
        }
        all_tweets.append(row)

    return pd.DataFrame(all_tweets)

def get_poisson_distributions(input_data):
    '''
    Take in a set of tweets with clean timestamps.
    Return a dataframe with the number of tweets published each hour of each day of the week.
    This function makes hours with no tweets explicit zeros so we can sample them later in our model.
    '''
    data = input_data \
        .assign(
            created_at = lambda x: x['created_at'].apply(convert_from_utc),
            hour = lambda x: x['created_at'].apply(get_hour),
            day = lambda x: x['created_at'].apply(get_day_of_week),
            year_week = lambda x: x['created_at'].apply(get_year_week),
        )

    year_weeks = data['year_week'].unique().tolist()
    dummy_data = []

    for year_week in year_weeks:
        for day in np.arange(0,7):
            for hour in np.arange(0,24):
                row = {
                    'year_week': year_week,
                    'day': day,
                    'hour': hour,
                }
                dummy_data.append(row)

    frame = pd.DataFrame(dummy_data)

    observed_tweets = data.groupby(['year_week', 'day', 'hour']).agg({'id': 'count'}).reset_index().set_axis(['year_week', 'day', 'hour', 'tweets'], axis=1, inplace=False)

    distributions = pd.merge(frame, observed_tweets, how='left').fillna(0)

    return distributions

def get_remining_hours_in_market(market_id):
    market_close = get_market_close(market_id)
    right_now = datetime.datetime.now() - datetime.timedelta(hours=4)
    date_range = pd.date_range(start=right_now, end = market_close, freq='h')
    hours_remaining = [(x.weekday(), x.hour) for x in date_range]

    return hours_remaining

def get_distribution(day, hour):
    return distributions.query(f'hour == {hour}').query(f'day == {day}')['tweets'].tolist()

def simulate_future_tweets(tweets_since_market_open, hours_remaining, n_trials):
    all_periods = []

    for day, hour in hours_remaining:
        results = random.choices(get_distribution(day,hour), k=n_trials)
        period = str(day) + '-' + str(hour)
        df = pd.DataFrame(zip(np.arange(n_trials), results), columns=['trial_number', 'results'])
        df['period'] = period
        all_periods.append(df)

    simulation_results = pd.concat(all_periods) \
        .groupby('trial_number') \
        .agg({'results': 'sum'}) \
        .reset_index() \
        .assign(results = lambda x: x['results'] + tweets_since_market_open)['results'] \
        .to_list()

    return simulation_results

def get_min_max(bounds):
    if 'fewer' in bounds:
        maximum = int(bounds.split(' ')[0])
        minimum = 0
    elif 'more' in bounds:
        maximum = 1000
        minimum = int(bounds.split(' ')[0])
    else:
        maximum = int(bounds.split(' - ')[1])
        minimum = int(bounds.split(' - ')[0])

    return minimum, maximum

def get_contract_details(market_id):
    response = requests.get('https://www.predictit.org/api/Market/{}/Contracts'.format(market_id))

    bounds_clean = []

    for contract in response.json():
        bounds = contract['contractName']
        minimum, maximum = get_min_max(bounds)
        row = {
            'contract': bounds,
            'minimum': minimum,
            'maximum': maximum,
            'yes_price': contract['bestYesPrice']
        }
        bounds_clean.append(row)

    contract_details = pd.DataFrame(bounds_clean)

    return contract_details

def get_simulation_probabilities(contract_details, simulation_results):

    bins = [0] + contract_details['maximum'].tolist()

    probabilities = pd.DataFrame(pd.cut(x=simulation_results, bins=bins, labels = contract_details['contract']), columns=['bucket']) \
        .reset_index() \
        .groupby('bucket') \
        .count() \
        .reset_index() \
        .set_axis(['contract', 'observations'], axis=1, inplace=False) \
        .assign(probability = lambda x: round(100 * x['observations'] / n_trials, 1)) \
        [['contract', 'probability']]

    return probabilities

def report_block(table, name):
    block = '''
    <b> {} </b>
    {} <br>
    '''.format(name, table.to_html(index=False))
    return block

def create_email_body():
    contracts_block = report_block(pricing, '@potus')

    body = '''\
    <html>
      <head></head>
      <body>
        <p>Hello, Interested Reader - here is your PredictIt pricing Update:</p><br>
           There are currently {} tweets since market open.<br>
           {}
      </body>
    </html>
    '''.format(tweets_since_market_open, contracts_block)

    return body

def status_report(recipient):
    subject = 'PredictIt Bot: Pricing Update'
    body = create_email_body()
    utils.send_email(subject, body, recipient)

if __name__ == '__main__':
    n_trials = 10000
    twitter_handle = '@potus'
    market_id = get_twitter_market_id(twitter_handle)
    hours_remaining = get_remining_hours_in_market(market_id)
    market_open = get_market_open(market_id)

    api = twitter_api()
    all_tweets = get_all_tweets(api, screen_name=twitter_handle)
    tweets_since_market_open = all_tweets[all_tweets['created_at'] > market_open].shape[0]

    distributions = get_poisson_distributions(input_data=all_tweets)
    simulation_results = simulate_future_tweets(tweets_since_market_open, hours_remaining, n_trials)

    contract_details = get_contract_details(market_id)
    probabilities = get_simulation_probabilities(contract_details, simulation_results)

    pricing = pd.merge(contract_details, probabilities, how = 'left', on = 'contract').fillna(0)[['contract', 'yes_price', 'probability']]

    for recipient in private.EMAIL_RECIPIENT_LIST:
        status_report(recipient)
