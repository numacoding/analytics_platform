from multiprocessing import connection
from flask import Flask, jsonify
import datetime
import database.queries as queries
from database.connection import run_query, zeitgeist_uri, status_code
import auxfunctions as aux_func
import pandas as pd
import numpy as np
from flask_jsonpify import jsonpify


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.route('/docs')
def ping():
    return jsonify({"message": "Pong"})

@app.route('/general-stats', methods=['GET'])
def general_stats():
    total_markets = run_query(zeitgeist_uri, queries.total_markets, status_code)
    total_markets_value = int(total_markets['data']['marketsConnection']['totalCount'])

    historical_users_query = run_query(zeitgeist_uri, queries.historical_users, status_code)
    historical_users = historical_users_query['data']['accountBalancesConnection']['totalCount']

    total_markets_with_liquidity = run_query(zeitgeist_uri, queries.total_markets_with_liquidity, status_code)
    total_markets_with_liquidity_value = int(total_markets_with_liquidity['data']['poolsConnection']['totalCount'])

    total_volume_per_market_json = run_query(zeitgeist_uri, queries.total_volume_per_market, status_code)

    total_volume = 0
    for dic in total_volume_per_market_json['data']['pools']:
        total_volume += int(dic['volume'])/10000000000

    return jsonify({
            'Total markets created in the app': total_markets_value,
            'Total markets created in the app with trades/liquidity in it': total_markets_with_liquidity_value,
            'Total ZTG volume (ever)': total_volume,
            'Total number of users (ever)': historical_users
        })

@app.route('/general-stats/user-participation/<int:time_delta>', methods=['GET'])
def get_stats_with_time(time_delta):
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
    
    aggregated_json = {
        'Total Distinct Users': len(grouped_df),
        'Mean user interaction': grouped_df['Interactions'].mean(),
        'Median user interaction': grouped_df['Interactions'].median(),
        'Mean ZTG traded by users': grouped_df_3['ztgTraded_mean'].mean(),
        'Median Ztg traded by users': grouped_df_3['ztgTraded_mean'].median()
    }

    return jsonify(aggregated_json)


@app.route('/general-stats/user-participation/<int:time_delta>/user-dataframe', methods=['GET'])
def get_user_stats_with_time(time_delta):
    df = aux_func.get_dataframe_to_analyze(time_delta)

    return jsonify(df.to_dict(orient='records'))


@app.route('/general-stats/user-participation/<int:time_delta>/daily-values', methods=['GET'])
def get_daily_volume_with_time(time_delta):
    date_df = aux_func.get_dataframe_grouped_by_day(time_delta)
    return jsonify(date_df.to_dict(orient='records'))


@app.route('/market-stats/top-10-markets', methods=['GET'])
def get_market_stats():
    top_10_pools_query = run_query(queries.top_ten_volume_mkts, zeitgeist_uri, status_code)
    # top_10_pools_observations = top_10_pools_query['data']['markets']

    # top_ten_markets= {}
    # for rank, i in enumerate(top_10_pools_observations, start=1):
    #     pool_volume = i['pool']['volume']
    #     market_question = run_query(queries.market_question_per_pool_id(str(i['poolId'])), zeitgeist_uri, status_code)
    #     market_data = market_question['data']['markets']
    #     question = market_data['question']

    #     asset_ticker = run_query(queries.assets_ticker_market_id(market_data['marketId']), zeitgeist_uri, status_code)
    #     assets = {}
    #     asset_indexes = asset_ticker['data']['markets']['outcomeAssets']
    #     for num, i in enumerate(asset_ticker['data']['markets']['categories'], start=0):
    #         asset_name = i['name']
    #         assets[asset_name] = asset_indexes[num]

    #     market_prices_query = queries.get_market_prices(str(market_data['marketId']))
    #     market_prices = market_prices_query['data']['assets']

    #     for key0,value0 in enumerate(assets):
    #         for i in market_prices:
    #             if value0 == i['assetId']:
    #                 assets[key0] = i['price']


    #     #a este punto, me debería quedar un diccionario del estilo *nombre del activo*: *nombre tecnico del archivo*
    #     #luego, necesito reemplazar esa key por el precio del activo

    #     market_json = {}
    #     market_json['question'] = question
    #     market_json['volume'] = pool_volume
    #     market_json['assets'] = assets
    #     top_ten_markets[rank] = market_json
        
    
    # return top_ten_markets
    return top_10_pools_query




if __name__ == '__main__':
    app.run(debug=True)