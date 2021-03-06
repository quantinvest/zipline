# -*- coding: utf-8 -*-
"""
Created on Sun Oct 23 15:42:00 2016

@author: Toby
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Oct 09 16:58:16 2016

@author: Toby
"""
import sys
sys.path.insert(0, r"E:")
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
import pytz
#from zipline.finance.slippage import VolumeShareSlippage
from zipline.finance.slippage import FreeTradeSlippage
from zipline.dailydata import DBProxy
dbProxy = DBProxy.DBProxy()

#basic_eps = dbProxy._get_fundamentals({'BASICEPS':float}, 'TQ_FIN_PROINCSTATEMENTNEW')
#revenue = dbProxy._get_fundamentals({'BIZINCO':float}, 'TQ_FIN_PROINCSTATEMENTNEW')
factor = dbProxy._get_fundamentals({'PARENETP':float}, 'TQ_FIN_PROINCSTATEMENTNEW')
period_start = '20140101'
period_end = '20160630'  
#basic_eps = pd.read_pickle(r"D:\Data\basic_eps")
#revenue = pd.read_pickle(r"D:\Data\revenue")
#factor = pd.read_pickle(r"D:\Data\factor")
from zipline.api import(
get_fundamentals,
history,
add_history,
set_long_only,
get_datetime,
get_universe,
cancel_order,
order_target_percent,
order_target_value,
record,
get_open_orders,
set_slippage,
)
import zipline as zp
from zipline.analysis import resolve_orders
from zipline.analysis import plot

def initialize(context):
    set_slippage(FreeTradeSlippage())
    context.timer=0
    add_history(1, '1d', 'volume')
    #set_slippage(FreeTradeSlippage())

def handle_data(context, data):
    today = get_datetime()
    if schedule(today):
        month = today.month
        year = today.year
        factor = get_fundamentals('PARENETP')
        sid_to_drop = factor.isnull().all(axis=1)
        sid_to_drop = list(sid_to_drop[sid_to_drop==True].index)
        factor = factor.drop(sid_to_drop)
        sids = factor.index
        if month in (1,2,3,4):
            rprtdate11,rprtdate12 = str(year-1)+'0930', str(year-2)+'0930'

        elif month in (5,6,7,8):
            rprtdate11,rprtdate12 = str(year)+'0331', str(year-1)+'0331'

        elif month in (9,10):
            rprtdate11,rprtdate12 = str(year)+'0630', str(year-1)+'0630'
 
        elif month in (11,12):
            rprtdate11,rprtdate12 = str(year)+'0930', str(year-1)+'0930'
        
        #factor = (factor[rprtdate11].astype(float).values - factor[rprtdate12].astype(float).values)/factor[rprtdate12].astype(float).values

        factor_score = (factor - np.nanmean(factor))/np.nanstd(factor)
        total_score = pd.DataFrame(factor_score, columns = ['score'], index = sids)     

        active_sids = get_universe()
        total_score = total_score.ix[active_sids,:]
        total_score.sort(inplace = True, columns = 'score')
        total_score.dropna(axis = 0,subset = ['score'],inplace = True)
        low = total_score.ix[:len(total_score)/5,:]
        high = total_score.ix[-len(total_score)/5:,:]
        long_stocks = set(high.index)
        short_stocks = set(low.index)
    
        N1 = len(short_stocks)
        N2 = len(long_stocks)
        for sid in short_stocks:
            order_target_percent(sid, -1.0/N1) 
        for sid in long_stocks:
            order_target_percent(sid, 1.0/N2)
def schedule(date):
    if date.weekday() == 0 and (15<=date.day<=21):
        return True
    else:
        return False
         
period_start = '20050101'
period_end = '20160330'            
TradingDictionary = {'initialize' : initialize,
                     'handle_data' : handle_data,
                     'period_start': period_start,
                     'period_end': period_end,
                     'benchmark': '2070000060',
                     'warming_period':20,
                     'capital_base': 100000000.0,
                     'security_type': 'stock'
                     }           
algo = zp.TradingAlgorithm(**TradingDictionary, fundamental_data = [factor])
results = algo.run(False) 

import zipline.analysis.show_results as show
results_count = show.count(results,list(algo.perf_tracker.cumulative_risk_metrics.benchmark_returns))
show.plot_results(results_count