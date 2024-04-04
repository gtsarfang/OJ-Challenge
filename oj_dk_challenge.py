"""DraftKings MLB API ETL"""

import pandas as pd
import requests

def dk_api_call(event_group: int):
    """Function to call Draft Kings API
    
    param event_group: used to query specfic league in DraftKings API
    return: return successful API response
    """
    # call DraftKings front-end API
    url = f'https://sportsbook-nash-usny.draftkings.com/sites/US-NY-SB/api/v5/eventgroups/{event_group}?format=json'
    params = {'format': 'json'}
    response = requests.get(url, params, timeout=20)

    # pass response if status code is good
    if response.status_code == 200:
        return response

    # raise Error if status code is not 200
    raise ValueError(f"API returned status code of {response.status_code}")

def format_offers_and_outcomes(response):
    """Formats the json from the public DraftKings API to combine and
    return all outcomes and offers into a single DataFrame
    
    param response: response from the DraftKings front-end API
    return: cleaned DataFrame with both offers and outcomes
    """
    # normalize json into pandas DataFrame containing 3 columns of dictionatires,
    # with each column representing a differet bet type (moneyline, spread, etc..)
    # and a row representing a different game
    df = pd.json_normalize(response.json()['eventGroup']['offerCategories']
                           [0]['offerSubcategoryDescriptors'][0]['offerSubcategory']['offers'])

    # initialize DFs to use within the for-loops
    df_offers = pd.DataFrame()
    df_outcomes = pd.DataFrame()
    # iterate over these columns for each type of bet (Moneyline, total, etc...)
    for series_name, _ in df.items():
        # explode the single dictionary column into multiple columns
        df_offers_temp = pd.DataFrame(df[series_name].tolist())

        # combine all offers together
        df_offers = pd.concat([df_offers, df_offers_temp])

        # explode outcomes into columns of outcome dictionaries
        df_outcomes_unf = pd.DataFrame(df_offers_temp['outcomes'].tolist(),
                                       index=df_offers_temp.index)

        # iterate over columns again for each side of the outcome
        for series_name, _ in df_outcomes_unf.items():
            df_outcomes_temp = pd.DataFrame(df_outcomes_unf[series_name].tolist(),
                                            index=df_outcomes_unf.index)

            # Filter and normalize moneyline outcome result
            # Moneylines are missing the "line" value
            if 'Moneyline' in df_offers_temp['label'].values:
                # add line column with "Win" value
                df_outcomes_temp['line'] = 'Win'
            else:
                # add + sign to positive "line" values to use in batName later
                df_outcomes_temp['line'] = df_outcomes_temp['line'].apply(lambda x: f'{x:+}')

            # combine normalized outcomes
            df_outcomes = pd.concat([df_outcomes,
                                     df_outcomes_temp[['label', 'line',
                                                       'oddsAmerican', 'providerOfferId']]])

    # rename offers "label" column to "betType" to avoid conflict with outcomes "label" column
    df_offers.rename(columns={'label': 'betType'}, inplace=True)

    # merge outcomes and subet offers important columns
    # providerOfferId is the primary key
    df_offers_outcomes = df_outcomes.merge(df_offers[['betType', 'isSuspended',
                                                      'isOpen', 'eventId', 'providerOfferId']],
                                                      how='left', on='providerOfferId')

    return df_offers_outcomes

def main():
    """Pulls moneyline, run line, and total bets from DraftKings
    for MLB games and prints the result dataframe to a csv"""

    # call Draft Kings API using the MLB event group id 84240
    response = dk_api_call(84240)

    # run transforms on response
    df_offers_outcomes = format_offers_and_outcomes(response)

    # grab the events data from the API call, contains data specific to each specific MLB game
    df_events = pd.json_normalize(response.json()['eventGroup']['events'])
    # subset imporant columns
    df_events_subset = df_events[['eventId', 'displayGroupId', 'eventGroupId', 'eventGroupName',
                                  'nameIdentifier', 'startDate', 'teamName1', 'teamName2',
                                  'teamShortName1', 'teamShortName2']]
    # merge events with offers and outcomes
    df_offers_events = df_offers_outcomes.merge(df_events_subset, how='left', on='eventId')

    ## add constant columns
    # timestamp from API call header
    df_offers_events['timestamp'] = response.headers['Date']
    df_offers_events['sport'] = 'Baseball'
    df_offers_events['sportsbook'] = 'DraftKings'

    # create betName column combining label with line to get a human readable bet name
    df_offers_events['betName'] = df_offers_events['label'] + ' ' \
        + df_offers_events['line'].astype(str)

    # remove na rows, these are produced when a bet is not open
    df_offers_events.dropna(inplace=True)

    # sort by specific MLB game
    df_offers_events = df_offers_events.sort_values(by='nameIdentifier')

    # reorder columns
    df_offers_events = df_offers_events[['sportsbook', 'displayGroupId', 'sport', 'eventGroupName',
                                         'eventGroupId', 'nameIdentifier', 'eventId',
                                         'providerOfferId', 'startDate', 'teamName1', 'teamName2',
                                         'teamShortName1', 'teamShortName2', 'betType', 'betName',
                                         'label', 'line', 'oddsAmerican', 'timestamp',
                                         'isSuspended', 'isOpen']]

    # create a csv with result dataframe
    df_offers_events.to_csv('results.csv', index=False)


if __name__ == "__main__":
    main()
