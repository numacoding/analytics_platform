import datetime
import pandas as pd
from database.connection import run_query, zeitgeist_uri, status_code
import database.queries as queries

def get_dataframe_to_analyze(time_delta):
    today = datetime.date.today()
    today_minus_delta = today - datetime.timedelta(days=time_delta)

    last_week_users_query = run_query(zeitgeist_uri, queries.active_users_per_period(str(today_minus_delta)), status_code)
    last_week_users_json = last_week_users_query['data']['historicalAssets']
    
    last_week_users_dataframe = pd.DataFrame([])
    for key, value in enumerate(last_week_users_json):
        last_week_users_dataframe = last_week_users_dataframe.append(value, ignore_index=True, sort=False)

    last_week_users_dataframe['dAmountInPool'] = last_week_users_dataframe['dAmountInPool'].apply(lambda x: int(x)/10000000000)
    last_week_users_dataframe['ztgTraded'] = last_week_users_dataframe['ztgTraded'].fillna(0).apply(lambda x: int(x)/10000000000)
    last_week_users_dataframe['timestamp'] = last_week_users_dataframe['timestamp'].apply(lambda x: x.split('T')[0]).apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"))

    grouped_df = last_week_users_dataframe[['accountId', 'event']].groupby('accountId').count().reset_index().rename(columns={'event':'Interactions'})
    grouped_df_2 = last_week_users_dataframe.groupby('accountId')['dAmountInPool'].mean().reset_index().rename(columns={'dAmountInPool':'PoolAmountIn_mean'})
    grouped_df_3 = last_week_users_dataframe.groupby('accountId', dropna=True)['ztgTraded'].mean().reset_index().rename(columns={'ztgTraded':'ztgTraded_mean'})
    
    

    merged_df = grouped_df.merge(grouped_df_2, on = 'accountId', how= 'inner').merge(grouped_df_3, on = 'accountId', how= 'inner')
    merged_df = merged_df.sort_values(by='Interactions', ascending=False)

    return merged_df


def get_dataframe_grouped_by_day(time_delta):
    today = datetime.date.today()
    today_minus_delta = today - datetime.timedelta(days=time_delta)

    last_week_users_query = run_query(zeitgeist_uri, queries.active_users_per_period(str(today_minus_delta)), status_code)
    last_week_users_json = last_week_users_query['data']['historicalAssets']
    
    last_week_users_dataframe = pd.DataFrame([])
    for key, value in enumerate(last_week_users_json):
        last_week_users_dataframe = last_week_users_dataframe.append(value, ignore_index=True, sort=False)

    last_week_users_dataframe['dAmountInPool'] = last_week_users_dataframe['dAmountInPool'].apply(lambda x: int(x)/10000000000)
    last_week_users_dataframe['ztgTraded'] = last_week_users_dataframe['ztgTraded'].fillna(0).apply(lambda x: int(x)/10000000000)
    last_week_users_dataframe['timestamp'] = last_week_users_dataframe['timestamp'].apply(lambda x: x.split('T')[0]).apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"))

    grouped_by_date = last_week_users_dataframe[['timestamp', 'dAmountInPool', 'ztgTraded']].groupby('timestamp')['ztgTraded'].sum()
    grouped_by_date_2 = last_week_users_dataframe[['timestamp', 'dAmountInPool', 'ztgTraded']].groupby('timestamp')['dAmountInPool'].sum()
    grouped_by_date_concat = pd.concat([grouped_by_date, grouped_by_date_2], axis = 1)
    grouped_by_date_concat = grouped_by_date_concat.reset_index() 

    return grouped_by_date_concat

