number_of_pools = '''
    query MyQuery {
        poolsConnection(orderBy: id_ASC) {
            totalCount
        }
    }    
'''

total_markets = '''
    query MyQuery {
        marketsConnection(orderBy: id_ASC) {
            totalCount
        }
    }

'''

total_markets_with_liquidity = '''
    query MarketPoolCount { 
        poolsConnection(orderBy: id_ASC) { totalCount }
    }
'''

total_volume_per_market = '''
    query VolumePerMarket { 
        pools(orderBy: marketId_ASC) { marketId volume }
    } 
'''

historical_users = '''
    query MyQuery {
        accountBalancesConnection(orderBy: id_ASC) {
            totalCount
        }
    }
'''

def active_users_per_period(time):
    query = '''
        query MyQuery {
            historicalAssets(where: {timestamp_gte: "'''+time+'''T00:00:00Z", AND: {accountId_not_contains: "null"}}) {
                accountId
                timestamp
                dAmountInPool
                ztgTraded
                event
            }
        }

    '''
    return query

def pool_volume(pool_id):
    '''
    Function Description
    '''
    query = '''
        query MyQuery {
            historicalPools(where: {volume_gt: "0", poolId_eq: '''+pool_id+'''}) {
                volume
                ztgQty
                timestamp
            }
        }
    '''

    return query

def historical_assets(timestamp_min = None, timestamp_max = None):
    '''
    Returns a JSON file with all the transactions made in that timestamp interval
    '''
    if (timestamp_min == None) & (timestamp_max == None):
        query = '''
                query MyQuery {
                    historicalAssets(orderBy: blockNumber_DESC) {
                        id
                        ztgTraded
                        dPrice
                        newAmountInPool
                        newPrice
                        timestamp
                        assetId
                    }
                }
            '''
    elif (timestamp_min == None):
        query = '''
            query MyQuery {
                historicalAssets(orderBy: blockNumber_DESC, where: {timestamp_lte: "'''+timestamp_max+'''"}) {
                    id
                    ztgTraded
                    dPrice
                    newAmountInPool
                    newPrice
                    timestamp
                    assetId
                }
            }
        '''
    elif (timestamp_max == None):
        query = '''
            query MyQuery {
                historicalAssets(orderBy: blockNumber_DESC, where: {timestamp_gte: "'''+timestamp_min+'''"}) {
                    id
                    ztgTraded
                    dPrice
                    newAmountInPool
                    newPrice
                    timestamp
                    assetId
                }
            }
        '''
    else:
        query= '''
            query MyQuery {
                historicalAssets(orderBy: blockNumber_DESC, where: {timestamp_gte: "'''+timestamp_min+'''", timestamp_lte: "'''+timestamp_max+'''"}) {
                    id
                    ztgTraded
                    dPrice
                    newAmountInPool
                    newPrice
                    timestamp
                    assetId
                }
            }
        '''
    
    return query



def real_time_volume(pool_id = None):
    '''
    Returns the volume of every pool (or a particular one), and the current amount of ZTG in each
    '''
    if pool_id == None:
        query = '''
            query MyQuery {
                pools(orderBy: volume_DESC) {
                    volume
                    ztgQty
                    poolId
                }
            }
            '''
    else:
        query = '''query MyQuery {
            pools(where: {poolId_eq: '''+pool_id+'''}) {
                poolId
                ztgQty
                volume
            }
        }
        '''

    return query

def trades_made_by_pm(market_id):
    '''
    Returns the trades of a specific market with related info
    '''
    query = '''query MyQuery {
            historicalAssets(where: {assetId_contains: "['''+market_id+''',", ztgTraded_gt: "0"}, orderBy: timestamp_DESC) {
                assetId
                ztgTraded
                dPrice
                newAmountInPool
                newPrice
                timestamp
            }
        }'''
    return query

def trades_made_by_pm_count(market_id):
    '''
    Counts the amount of trades made on a specific PM
    '''
    query = '''
        query MyQuery {
            historicalAssetsConnection(orderBy: id_ASC, where: {assetId_contains: "['''+market_id+''',", ztgTraded_gt: "0"}) {
                totalCount
            }
        }
    '''

    return query


def market_status(market_id):
    '''
    Returns information about the status of the market:
    - Market question
    - Resolved outcome (in case that the market is resolved)
    - Market status
    '''
    query = '''
        query MyQuery {
            markets(where: {marketId_eq: '''+market_id+'''}) {
                question
                resolvedOutcome
                status
            }
        }
    '''

    return query



def lp_history(market_id):
    '''
    PoolExit (pool shares burned)
    PoolJoin (pool shares minted)
    PoolCreate (pool shares minted)
    '''

    query = '''
        query MyQuery {
            historicalAssets(where: {event_contains: "Pool", assetId_contains: "['''+market_id+''',"}) {
                accountId
                assetId
                event
                dAmountInPool
                dPrice
                newPrice
                newAmountInPool
                timestamp
            }
        }
    '''

    return query


def market_question_per_pool_id(pool_id):
    all_time_market_join_query = '''
        query TopTenPoolVolume {
            markets(where: {poolId_eq: '''+pool_id+'''}) {
                question
                status
                marketId
                poolId
            }
        }
    '''
    return all_time_market_join_query

def assets_ticker_market_id(market_id):
    assets_ticker = '''
        query MyQuery {
            markets(where: {marketId_eq: '''+market_id+'''}) {
                categories {
                    name
                    ticker
                }
                outcomeAssets
            }
        }
    '''
    return assets_ticker

def get_market_prices(market_id):
    query = '''
        query MarketAssetPrices {
            assets(where: {assetId_contains: "['''+market_id+''',"}) {
                assetId
                price
            }
        }
    '''
    return query

top_ten_volume_mkts = '''
    query TopTenPoolVolume {
        markets(where: {status_contains: "Active", pool_isNull: false}, orderBy: pool_volume_DESC, limit: 10) {
            marketId
            question
            pool {
                volume
            }
        }
    }
'''