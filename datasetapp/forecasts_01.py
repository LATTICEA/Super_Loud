from django.conf import settings

# import os ### manage file path
import pandas as pd ### dataframe management and manipulation
import numpy as np ### numeric functions such as averages and sums
# from time import time ### clock to time sections of the code
# from datetime import datetime ### getting years and other date parts
# from statsmodels.tsa.arima.model import ARIMA ### ARIMA model

from statsmodels.tsa.holtwinters import ExponentialSmoothing
# from statsmodels.tsa.holtwinters import Holt

# from sklearn.metrics import mean_squared_error ### Error function to compare forecasting models
# import random ### Get random samples
import warnings
# from multiprocessing import Pool
# from sklearn.preprocessing import MinMaxScaler
from functools import reduce
import psycopg2
# import json
from math import isnan
# import argparse

# pd.set_option('max_columns', None)
import sys
# import subprocess
# subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'line_profiler'])
warnings.filterwarnings('ignore')

### plots show in Jupyter Notebook
# import matplotlib.pylab as plt ### Visuals
# %matplotlib inline

# https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits/23728630#23728630
import string
import random

# %load_ext line_profiler

def query(_host_, _user_, _password_, _db_, _query_):
    conn = psycopg2.connect(host=_host_, database=_db_, user=_user_, password=_password_)
    cursor = conn.cursor()
    cursor.execute(_query_)
    return cursor.fetchall()
    conn.close() 
    
def execute_query(_host_, _user_, _password_, _db_, _query_):
    conn = psycopg2.connect(host=_host_, database=_db_, user=_user_, password=_password_)
    cursor = conn.cursor()
    cursor.execute(_query_)
    conn.close() 
    
def mse_pct_2(predictions, actuals):
    summation = 0  #variable to store the summation of differences
    n = len(predictions) #finding total number of items in list
    for i in range (0,n):  #looping through each element of the list
        difference = np.square((actuals[i] - predictions[i]) / actuals[i])
        summation = round(summation + difference, 6)  #taking a sum of all the differences
    mse = np.sqrt(summation/n)  #dividing summation by total values to obtain average
    return mse

def bollinger_strat_pct(df, window, no_of_std):
    target_column = df.columns[0]
    df[target_column + 'sd_diff'] = df[target_column].pct_change()
    
    rolling_mean = df[target_column + 'sd_diff'].shift(4).rolling(window).mean()
    rolling_std = df[target_column + 'sd_diff'].shift(4).rolling(window).std()

    sd_high = rolling_mean + (rolling_std * no_of_std)
    sd_low = rolling_mean - (rolling_std * no_of_std)
    
    df.drop(columns=[target_column + 'sd_diff'], inplace=True)
    return [sd_high, sd_low]

def bollinger_strat(df, window, no_of_std, target_column):
    rolling_mean = df[target_column].shift(4).rolling(window).mean()
    rolling_std = df[target_column].shift(4).rolling(window).std()

    sd_high = rolling_mean + (rolling_std * no_of_std)
    sd_low = rolling_mean - (rolling_std * no_of_std)
    return [sd_high, sd_low]

_host_ = settings.DATABASES['default']['HOST']
_user_ = settings.DATABASES['default']['USER']
_password_ = settings.DATABASES['default']['PASSWORD']
_db_ = settings.DATABASES['default']['NAME']

def queryer(skills_list, msa_code, user_id, schema):
    sql = "with "
    sql += "cte_stage as ( "
    sql += "select  "
    sql += "mos.occ_code "
    sql += ", mos.tech_skills "
    sql += ", o.reporting_year "
    sql += ", o.tot_emp "
    sql += ", a_mean "
    sql += ", a_pct10 "
    sql += ", a_pct25 "
    sql += ", a_median "
    sql += ", a_pct75 "
    sql += ", a_pct90 "
    sql += "from  "
    sql += "prod.oews o "
    sql += "join ( "
    sql += "select "
    sql += "mos.occ_code "
    sql += ", mos.tech_skills "
    sql += ", mos.msa_code "
    sql += "from  "
    sql += "{}.msa_occ_skills_v1 mos ".format(schema)
    sql += "where  "
    sql += "mos.tech_skills = any (array" + skills_list + ") "
    sql += "and mos.msa_code = '" + msa_code + "' "
    sql += ") mos  "
    sql += "on mos.msa_code = o.area_code "
    sql += "and mos.occ_code = o.occ_code "
    sql += "where  "
    sql += "o.tot_emp is not null and o.tot_emp >= 0 "
    sql += "and o.a_mean is not null and o.a_mean >= 0 "
    sql += "and o.a_pct10 is not null and o.a_pct10 >= 0 "
    sql += "and o.a_pct25 is not null and o.a_pct25 >= 0 "
    sql += "and o.a_median is not null and o.a_median >= 0 "
    sql += "and o.a_pct75 is not null and o.a_pct75 >= 0 "
    sql += "and o.a_pct90 is not null and o.a_pct90 >= 0 "
    sql += ") "
    sql += ", industry_filter_stage_cte as ( "
    sql += "select "
    sql += "left(occ_code, 2) as industry "
    sql += ", tech_skills "
    sql += ", reporting_year "
    sql += ", count(left(occ_code, 2)) as occ_count_by_code "
    sql += ", count(left(occ_code, 2)) over (partition by reporting_year, tech_skills) as occ_count_by_skill "
    sql += "from "
    sql += "cte_stage "
    sql += "group by "
    sql += "left(occ_code, 2) "
    sql += ", tech_skills "
    sql += ", reporting_year "
    sql += ") "
    sql += ", industry_filter_cte as ( "
    sql += "select "
    sql += "* "
    sql += ", rank() over (partition by reporting_year, tech_skills order by occ_count_by_code desc) as ind_filter "
    sql += "from "
    sql += "industry_filter_stage_cte "
    sql += ") "
    sql += ", cte as ( "
    sql += "select "
    sql += "c.occ_code "
    sql += ", c.tech_skills "
    sql += ", c.reporting_year "
    sql += ", c.tot_emp "
    sql += ", c.tot_emp::numeric / sum(c.tot_emp) over (partition by c.reporting_year) as yearly_emp "
    sql += ", round(a_mean * (c.tot_emp::numeric / sum(c.tot_emp) over (partition by c.reporting_year)), 0) as a_mean_seg "
    sql += ", round(a_pct10 * (c.tot_emp::numeric / sum(c.tot_emp) over (partition by c.reporting_year)), 0) as a_pct10_seg "
    sql += ", round(a_pct25 * (c.tot_emp::numeric / sum(c.tot_emp) over (partition by c.reporting_year)), 0) as a_pct25_seg "
    sql += ", round(a_median * (c.tot_emp::numeric / sum(c.tot_emp) over (partition by c.reporting_year)), 0) as a_median_seg "
    sql += ", round(a_pct75 * (c.tot_emp::numeric / sum(c.tot_emp) over (partition by c.reporting_year)), 0) as a_pct75_seg "
    sql += ", round(a_pct90 * (c.tot_emp::numeric / sum(c.tot_emp) over (partition by c.reporting_year)), 0) as a_pct90_seg "
    sql += ", round(a_mean * (c.tot_emp::numeric / sum(c.tot_emp) over (partition by c.reporting_year, c.tech_skills)), 0) as a_mean_seg3 "
    sql += ", round(a_pct10 * (c.tot_emp::numeric / sum(c.tot_emp) over (partition by c.reporting_year, c.tech_skills)), 0) as a_pct10_seg3 "
    sql += ", round(a_pct25 * (c.tot_emp::numeric / sum(c.tot_emp) over (partition by c.reporting_year, c.tech_skills)), 0) as a_pct25_seg3 "
    sql += ", round(a_median * (c.tot_emp::numeric / sum(c.tot_emp) over (partition by c.reporting_year, c.tech_skills)), 0) as a_median_seg3 "
    sql += ", round(a_pct75 * (c.tot_emp::numeric / sum(c.tot_emp) over (partition by c.reporting_year, c.tech_skills)), 0) as a_pct75_seg3 "
    sql += ", round(a_pct90 * (c.tot_emp::numeric / sum(c.tot_emp) over (partition by c.reporting_year, c.tech_skills)), 0) as a_pct90_seg3  "
    sql += "from "
    sql += "cte_stage c "
    sql += "join industry_filter_cte ifc "
    sql += "on ifc.industry = left(c.occ_code, 2) "
    sql += "and ifc.tech_skills = c.tech_skills "
    sql += "and ifc.reporting_year = c.reporting_year "
    sql += "where "
    sql += "ifc.ind_filter <= 3 "
    sql += ") "
    sql += ", cte2 as ( "
    sql += "select distinct "
    sql += "reporting_year "
    sql += ", dense_rank() over (order by reporting_year desc)+1 as year_count from cte ) "
    sql += ", cte_sum1 as ( select cte2.year_count "
    sql += ", cte.tech_skills "
    sql += ", sum(a_mean_seg) as a_mean_seg "
    sql += ", sum(a_pct10_seg) as a_pct10_seg "
    sql += ", sum(a_pct25_seg) as a_pct25_seg "
    sql += ", sum(a_median_seg) as a_median_seg "
    sql += ", sum(a_pct75_seg) as a_pct75_seg "
    sql += ", sum(a_pct90_seg) as a_pct90_seg "
    sql += ", sum(a_mean_seg3) as a_mean_seg3 "
    sql += ", sum(a_pct10_seg3) as a_pct10_seg3 "
    sql += ", sum(a_pct25_seg3) as a_pct25_seg3 "
    sql += ", sum(a_median_seg3) as a_median_seg3 "
    sql += ", sum(a_pct75_seg3) as a_pct75_seg3 "
    sql += ", sum(a_pct90_seg3) as a_pct90_seg3 "
    sql += "from "
    sql += "cte "
    sql += "left join cte2 "
    sql += "using (reporting_year) "
    sql += "where "
    sql += "cte.reporting_year is not null "
    sql += "group by "
    sql += "1, 2 "
    sql += ") "
    sql += ", cte_sum as ( "
    sql += "select "
    sql += "year_count "
    sql += ", tech_skills "
    sql += ", dense_rank() over (partition by year_count order by tech_skills) + a_mean_seg as a_mean_seg "
    sql += ", dense_rank() over (partition by year_count order by tech_skills) + a_pct10_seg as a_pct10_seg "
    sql += ", dense_rank() over (partition by year_count order by tech_skills) + a_pct25_seg as a_pct25_seg "
    sql += ", dense_rank() over (partition by year_count order by tech_skills) + a_median_seg as a_median_seg "
    sql += ", dense_rank() over (partition by year_count order by tech_skills) + a_pct75_seg as a_pct75_seg "
    sql += ", dense_rank() over (partition by year_count order by tech_skills) + a_pct90_seg as a_pct90_seg "
    sql += ", dense_rank() over (partition by year_count order by tech_skills) + a_mean_seg3 as a_mean_seg3 "
    sql += ", dense_rank() over (partition by year_count order by tech_skills) + a_pct10_seg3 as a_pct10_seg3 "
    sql += ", dense_rank() over (partition by year_count order by tech_skills) + a_pct25_seg3 as a_pct25_seg3 "
    sql += ", dense_rank() over (partition by year_count order by tech_skills) + a_median_seg3 as a_median_seg3 "
    sql += ", dense_rank() over (partition by year_count order by tech_skills) + a_pct75_seg3 as a_pct75_seg3 "
    sql += ", dense_rank() over (partition by year_count order by tech_skills) + a_pct90_seg3 as a_pct90_seg3  "
    sql += "from "
    sql += "cte_sum1 "
    sql += ") "
    sql += ", cte_max as ( "
    sql += "select "
    sql += "cs.year_count "
    sql += ", max(cs.a_mean_seg3) as a_mean_max "
    sql += ", max(cs.a_pct10_seg3) as a_pct10_max "
    sql += ", max(cs.a_pct25_seg3) as a_pct25_max "
    sql += ", max(cs.a_median_seg3) as a_median_max "
    sql += ", max(cs.a_pct75_seg3) as a_pct75_max "
    sql += ", max(cs.a_pct90_seg3) as a_pct90_max "
    sql += "from "
    sql += "cte_sum cs "
    sql += "group by "
    sql += "1 "
    sql += ") "
    sql += ", cte_pre_final as ( "
    sql += "select "
    sql += "cm.year_count "
    sql += ", cm.a_mean_max as dollar_sum_avg_a "
    sql += ", cm.a_pct10_max as dollar_sum_10_a "
    sql += ", cm.a_pct25_max as dollar_sum_25_a "
    sql += ", cm.a_median_max as dollar_sum_med_a "
    sql += ", cm.a_pct75_max as dollar_sum_75_a "
    sql += ", cm.a_pct90_max as dollar_sum_90_a from cte_max cm union all select cs.year_count "
    sql += ", sum(case when cm.a_mean_max = cs.a_mean_seg3 then 0 else cs.a_mean_seg * 0.10 end) as dollar_sum_avg_a "
    sql += ", sum(case when cm.a_pct10_max = cs.a_pct10_seg3 then 0 else cs.a_pct10_seg * 0.10 end) as dollar_sum_10_a "
    sql += ", sum(case when cm.a_pct25_max = cs.a_pct25_seg3 then 0 else cs.a_pct25_seg * 0.10 end) as dollar_sum_25_a "
    sql += ", sum(case when cm.a_median_max = cs.a_median_seg3 then 0 else cs.a_median_seg * 0.10 end) as dollar_sum_med_a "
    sql += ", sum(case when cm.a_pct75_max = cs.a_pct75_seg3 then 0 else cs.a_pct75_seg * 0.10 end) as dollar_sum_75_a "
    sql += ", sum(case when cm.a_pct90_max = cs.a_pct90_seg3 then 0 else cs.a_pct90_seg * 0.10 end) as dollar_sum_90_a "
    sql += "from "
    sql += "cte_sum cs "
    sql += "left join cte_max cm "
    sql += "using (year_count) "
    sql += "group by 1 "
    sql += ") "
    sql += ", cte_final as ( "
    sql += "select "
    sql += "year_count "
    sql += ", round(sum(dollar_sum_avg_a), 0) as dollar_sum_avg_a "
    sql += ", round(sum(dollar_sum_10_a), 0) as dollar_sum_10_a "
    sql += ", round(sum(dollar_sum_25_a), 0) as dollar_sum_25_a "
    sql += ", round(sum(dollar_sum_med_a), 0) as dollar_sum_med_a "
    sql += ", round(sum(dollar_sum_75_a), 0) as dollar_sum_75_a "
    sql += ", round(sum(dollar_sum_90_a), 0) as dollar_sum_90_a from cte_pre_final group by 1 ) "
    sql += "select "
    sql += "'" + msa_code + "' as area_title "
    sql += ", array" + skills_list + " as skills_list "
    sql += ", '" + str(user_id) + "' as user_id "
    sql += ", 'skills' AS placeholder "
    sql += ", dollar_sum_10_a_0.dollar_sum_10_a::int as dollar_sum_10_a_0 "
    sql += ", dollar_sum_10_a_1.dollar_sum_10_a::int as dollar_sum_10_a_1 "
    sql += ", dollar_sum_10_a_2.dollar_sum_10_a::int as dollar_sum_10_a_2 "
    sql += ", dollar_sum_10_a_3.dollar_sum_10_a::int as dollar_sum_10_a_3 "
    sql += ", dollar_sum_10_a_4.dollar_sum_10_a::int as dollar_sum_10_a_4 "
    sql += ", dollar_sum_10_a_5.dollar_sum_10_a::int as dollar_sum_10_a_5 "
    sql += ", dollar_sum_10_a_6.dollar_sum_10_a::int as dollar_sum_10_a_6 "
    sql += ", dollar_sum_10_a_7.dollar_sum_10_a::int as dollar_sum_10_a_7 "
    sql += ", dollar_sum_10_a_8.dollar_sum_10_a::int as dollar_sum_10_a_8 "
    sql += ", dollar_sum_10_a_9.dollar_sum_10_a::int as dollar_sum_10_a_9 "
    sql += ", dollar_sum_10_a_10.dollar_sum_10_a::int as dollar_sum_10_a_10 "
    sql += ", dollar_sum_10_a_11.dollar_sum_10_a::int as dollar_sum_10_a_11 "
    sql += ", dollar_sum_10_a_12.dollar_sum_10_a::int as dollar_sum_10_a_12 "
    sql += ", dollar_sum_25_a_0.dollar_sum_25_a::int as dollar_sum_25_a_0 "
    sql += ", dollar_sum_25_a_1.dollar_sum_25_a::int as dollar_sum_25_a_1 "
    sql += ", dollar_sum_25_a_2.dollar_sum_25_a::int as dollar_sum_25_a_2 "
    sql += ", dollar_sum_25_a_3.dollar_sum_25_a::int as dollar_sum_25_a_3 "
    sql += ", dollar_sum_25_a_4.dollar_sum_25_a::int as dollar_sum_25_a_4 "
    sql += ", dollar_sum_25_a_5.dollar_sum_25_a::int as dollar_sum_25_a_5 "
    sql += ", dollar_sum_25_a_6.dollar_sum_25_a::int as dollar_sum_25_a_6 "
    sql += ", dollar_sum_25_a_7.dollar_sum_25_a::int as dollar_sum_25_a_7 "
    sql += ", dollar_sum_25_a_8.dollar_sum_25_a::int as dollar_sum_25_a_8 "
    sql += ", dollar_sum_25_a_9.dollar_sum_25_a::int as dollar_sum_25_a_9 "
    sql += ", dollar_sum_25_a_10.dollar_sum_25_a::int as dollar_sum_25_a_10 "
    sql += ", dollar_sum_25_a_11.dollar_sum_25_a::int as dollar_sum_25_a_11 "
    sql += ", dollar_sum_25_a_12.dollar_sum_25_a::int as dollar_sum_25_a_12 "
    sql += ", dollar_sum_median_a_0.dollar_sum_med_a::int as dollar_sum_median_a_0 "
    sql += ", dollar_sum_median_a_1.dollar_sum_med_a::int as dollar_sum_median_a_1 "
    sql += ", dollar_sum_median_a_2.dollar_sum_med_a::int as dollar_sum_median_a_2 "
    sql += ", dollar_sum_median_a_3.dollar_sum_med_a::int as dollar_sum_median_a_3 "
    sql += ", dollar_sum_median_a_4.dollar_sum_med_a::int as dollar_sum_median_a_4 "
    sql += ", dollar_sum_median_a_5.dollar_sum_med_a::int as dollar_sum_median_a_5 "
    sql += ", dollar_sum_median_a_6.dollar_sum_med_a::int as dollar_sum_median_a_6 "
    sql += ", dollar_sum_median_a_7.dollar_sum_med_a::int as dollar_sum_median_a_7 "
    sql += ", dollar_sum_median_a_8.dollar_sum_med_a::int as dollar_sum_median_a_8 "
    sql += ", dollar_sum_median_a_9.dollar_sum_med_a::int as dollar_sum_median_a_9 "
    sql += ", dollar_sum_median_a_10.dollar_sum_med_a::int as dollar_sum_median_a_10 "
    sql += ", dollar_sum_median_a_11.dollar_sum_med_a::int as dollar_sum_median_a_11 "
    sql += ", dollar_sum_median_a_12.dollar_sum_med_a::int as dollar_sum_median_a_12 "
    sql += ", dollar_sum_75_a_0.dollar_sum_75_a::int as dollar_sum_75_a_0 "
    sql += ", dollar_sum_75_a_1.dollar_sum_75_a::int as dollar_sum_75_a_1 "
    sql += ", dollar_sum_75_a_2.dollar_sum_75_a::int as dollar_sum_75_a_2 "
    sql += ", dollar_sum_75_a_3.dollar_sum_75_a::int as dollar_sum_75_a_3 "
    sql += ", dollar_sum_75_a_4.dollar_sum_75_a::int as dollar_sum_75_a_4 "
    sql += ", dollar_sum_75_a_5.dollar_sum_75_a::int as dollar_sum_75_a_5 "
    sql += ", dollar_sum_75_a_6.dollar_sum_75_a::int as dollar_sum_75_a_6 "
    sql += ", dollar_sum_75_a_7.dollar_sum_75_a::int as dollar_sum_75_a_7 "
    sql += ", dollar_sum_75_a_8.dollar_sum_75_a::int as dollar_sum_75_a_8 "
    sql += ", dollar_sum_75_a_9.dollar_sum_75_a::int as dollar_sum_75_a_9 "
    sql += ", dollar_sum_75_a_10.dollar_sum_75_a::int as dollar_sum_75_a_10 "
    sql += ", dollar_sum_75_a_11.dollar_sum_75_a::int as dollar_sum_75_a_11 "
    sql += ", dollar_sum_75_a_12.dollar_sum_75_a::int as dollar_sum_75_a_12 "
    sql += ", dollar_sum_90_a_0.dollar_sum_90_a::int as dollar_sum_90_a_0 "
    sql += ", dollar_sum_90_a_1.dollar_sum_90_a::int as dollar_sum_90_a_1 "
    sql += ", dollar_sum_90_a_2.dollar_sum_90_a::int as dollar_sum_90_a_2 "
    sql += ", dollar_sum_90_a_3.dollar_sum_90_a::int as dollar_sum_90_a_3 "
    sql += ", dollar_sum_90_a_4.dollar_sum_90_a::int as dollar_sum_90_a_4 "
    sql += ", dollar_sum_90_a_5.dollar_sum_90_a::int as dollar_sum_90_a_5 "
    sql += ", dollar_sum_90_a_6.dollar_sum_90_a::int as dollar_sum_90_a_6 "
    sql += ", dollar_sum_90_a_7.dollar_sum_90_a::int as dollar_sum_90_a_7 "
    sql += ", dollar_sum_90_a_8.dollar_sum_90_a::int as dollar_sum_90_a_8 "
    sql += ", dollar_sum_90_a_9.dollar_sum_90_a::int as dollar_sum_90_a_9 "
    sql += ", dollar_sum_90_a_10.dollar_sum_90_a::int as dollar_sum_90_a_10 "
    sql += ", dollar_sum_90_a_11.dollar_sum_90_a::int as dollar_sum_90_a_11 "
    sql += ", dollar_sum_90_a_12.dollar_sum_90_a::int as dollar_sum_90_a_12 "
    sql += ", dollar_sum_avg_a_0.dollar_sum_avg_a::int as dollar_sum_avg_a_0 "
    sql += ", dollar_sum_avg_a_1.dollar_sum_avg_a::int as dollar_sum_avg_a_1 "
    sql += ", dollar_sum_avg_a_2.dollar_sum_avg_a::int as dollar_sum_avg_a_2 "
    sql += ", dollar_sum_avg_a_3.dollar_sum_avg_a::int as dollar_sum_avg_a_3 "
    sql += ", dollar_sum_avg_a_4.dollar_sum_avg_a::int as dollar_sum_avg_a_4 "
    sql += ", dollar_sum_avg_a_5.dollar_sum_avg_a::int as dollar_sum_avg_a_5 "
    sql += ", dollar_sum_avg_a_6.dollar_sum_avg_a::int as dollar_sum_avg_a_6 "
    sql += ", dollar_sum_avg_a_7.dollar_sum_avg_a::int as dollar_sum_avg_a_7 "
    sql += ", dollar_sum_avg_a_8.dollar_sum_avg_a::int as dollar_sum_avg_a_8 "
    sql += ", dollar_sum_avg_a_9.dollar_sum_avg_a::int as dollar_sum_avg_a_9 "
    sql += ", dollar_sum_avg_a_10.dollar_sum_avg_a::int as dollar_sum_avg_a_10 "
    sql += ", dollar_sum_avg_a_11.dollar_sum_avg_a::int as dollar_sum_avg_a_11 "
    sql += ", dollar_sum_avg_a_12.dollar_sum_avg_a::int as dollar_sum_avg_a_12 "
    sql += ", round(dollar_sum_10_a_0.dollar_sum_10_a / 2080, 2) as dollar_sum_10_h_0 "
    sql += ", round(dollar_sum_10_a_1.dollar_sum_10_a / 2080, 2) as dollar_sum_10_h_1 "
    sql += ", round(dollar_sum_10_a_2.dollar_sum_10_a / 2080, 2) as dollar_sum_10_h_2 "
    sql += ", round(dollar_sum_10_a_3.dollar_sum_10_a / 2080, 2) as dollar_sum_10_h_3 "
    sql += ", round(dollar_sum_10_a_4.dollar_sum_10_a / 2080, 2) as dollar_sum_10_h_4 "
    sql += ", round(dollar_sum_10_a_5.dollar_sum_10_a / 2080, 2) as dollar_sum_10_h_5 "
    sql += ", round(dollar_sum_10_a_6.dollar_sum_10_a / 2080, 2) as dollar_sum_10_h_6 "
    sql += ", round(dollar_sum_10_a_7.dollar_sum_10_a / 2080, 2) as dollar_sum_10_h_7 "
    sql += ", round(dollar_sum_10_a_8.dollar_sum_10_a / 2080, 2) as dollar_sum_10_h_8 "
    sql += ", round(dollar_sum_10_a_9.dollar_sum_10_a / 2080, 2) as dollar_sum_10_h_9 "
    sql += ", round(dollar_sum_10_a_10.dollar_sum_10_a / 2080, 2) as dollar_sum_10_h_10 "
    sql += ", round(dollar_sum_10_a_11.dollar_sum_10_a / 2080, 2) as dollar_sum_10_h_11 "
    sql += ", round(dollar_sum_10_a_12.dollar_sum_10_a / 2080, 2) as dollar_sum_10_h_12 "
    sql += ", round(dollar_sum_25_a_0.dollar_sum_25_a / 2080, 2) as dollar_sum_25_h_0 "
    sql += ", round(dollar_sum_25_a_1.dollar_sum_25_a / 2080, 2) as dollar_sum_25_h_1 "
    sql += ", round(dollar_sum_25_a_2.dollar_sum_25_a / 2080, 2) as dollar_sum_25_h_2 "
    sql += ", round(dollar_sum_25_a_3.dollar_sum_25_a / 2080, 2) as dollar_sum_25_h_3 "
    sql += ", round(dollar_sum_25_a_4.dollar_sum_25_a / 2080, 2) as dollar_sum_25_h_4 "
    sql += ", round(dollar_sum_25_a_5.dollar_sum_25_a / 2080, 2) as dollar_sum_25_h_5 "
    sql += ", round(dollar_sum_25_a_6.dollar_sum_25_a / 2080, 2) as dollar_sum_25_h_6 "
    sql += ", round(dollar_sum_25_a_7.dollar_sum_25_a / 2080, 2) as dollar_sum_25_h_7 "
    sql += ", round(dollar_sum_25_a_8.dollar_sum_25_a / 2080, 2) as dollar_sum_25_h_8 "
    sql += ", round(dollar_sum_25_a_9.dollar_sum_25_a / 2080, 2) as dollar_sum_25_h_9 "
    sql += ", round(dollar_sum_25_a_10.dollar_sum_25_a / 2080, 2) as dollar_sum_25_h_10 "
    sql += ", round(dollar_sum_25_a_11.dollar_sum_25_a / 2080, 2) as dollar_sum_25_h_11 "
    sql += ", round(dollar_sum_25_a_12.dollar_sum_25_a / 2080, 2) as dollar_sum_25_h_12 "
    sql += ", round(dollar_sum_median_a_0.dollar_sum_med_a / 2080, 2) as dollar_sum_median_h_0 "
    sql += ", round(dollar_sum_median_a_1.dollar_sum_med_a / 2080, 2) as dollar_sum_median_h_1 "
    sql += ", round(dollar_sum_median_a_2.dollar_sum_med_a / 2080, 2) as dollar_sum_median_h_2 "
    sql += ", round(dollar_sum_median_a_3.dollar_sum_med_a / 2080, 2) as dollar_sum_median_h_3 "
    sql += ", round(dollar_sum_median_a_4.dollar_sum_med_a / 2080, 2) as dollar_sum_median_h_4 "
    sql += ", round(dollar_sum_median_a_5.dollar_sum_med_a / 2080, 2) as dollar_sum_median_h_5 "
    sql += ", round(dollar_sum_median_a_6.dollar_sum_med_a / 2080, 2) as dollar_sum_median_h_6 "
    sql += ", round(dollar_sum_median_a_7.dollar_sum_med_a / 2080, 2) as dollar_sum_median_h_7 "
    sql += ", round(dollar_sum_median_a_8.dollar_sum_med_a / 2080, 2) as dollar_sum_median_h_8 "
    sql += ", round(dollar_sum_median_a_9.dollar_sum_med_a / 2080, 2) as dollar_sum_median_h_9 "
    sql += ", round(dollar_sum_median_a_10.dollar_sum_med_a / 2080, 2) as dollar_sum_median_h_10 "
    sql += ", round(dollar_sum_median_a_11.dollar_sum_med_a / 2080, 2) as dollar_sum_median_h_11 "
    sql += ", round(dollar_sum_median_a_12.dollar_sum_med_a / 2080, 2) as dollar_sum_median_h_12 "
    sql += ", round(dollar_sum_75_a_0.dollar_sum_75_a / 2080, 2) as dollar_sum_75_h_0 "
    sql += ", round(dollar_sum_75_a_1.dollar_sum_75_a / 2080, 2) as dollar_sum_75_h_1 "
    sql += ", round(dollar_sum_75_a_2.dollar_sum_75_a / 2080, 2) as dollar_sum_75_h_2 "
    sql += ", round(dollar_sum_75_a_3.dollar_sum_75_a / 2080, 2) as dollar_sum_75_h_3 "
    sql += ", round(dollar_sum_75_a_4.dollar_sum_75_a / 2080, 2) as dollar_sum_75_h_4 "
    sql += ", round(dollar_sum_75_a_5.dollar_sum_75_a / 2080, 2) as dollar_sum_75_h_5 "
    sql += ", round(dollar_sum_75_a_6.dollar_sum_75_a / 2080, 2) as dollar_sum_75_h_6 "
    sql += ", round(dollar_sum_75_a_7.dollar_sum_75_a / 2080, 2) as dollar_sum_75_h_7 "
    sql += ", round(dollar_sum_75_a_8.dollar_sum_75_a / 2080, 2) as dollar_sum_75_h_8 "
    sql += ", round(dollar_sum_75_a_9.dollar_sum_75_a / 2080, 2) as dollar_sum_75_h_9 "
    sql += ", round(dollar_sum_75_a_10.dollar_sum_75_a / 2080, 2) as dollar_sum_75_h_10 "
    sql += ", round(dollar_sum_75_a_11.dollar_sum_75_a / 2080, 2) as dollar_sum_75_h_11 "
    sql += ", round(dollar_sum_75_a_12.dollar_sum_75_a / 2080, 2) as dollar_sum_75_h_12 "
    sql += ", round(dollar_sum_90_a_0.dollar_sum_90_a / 2080, 2) as dollar_sum_90_h_0 "
    sql += ", round(dollar_sum_90_a_1.dollar_sum_90_a / 2080, 2) as dollar_sum_90_h_1 "
    sql += ", round(dollar_sum_90_a_2.dollar_sum_90_a / 2080, 2) as dollar_sum_90_h_2 "
    sql += ", round(dollar_sum_90_a_3.dollar_sum_90_a / 2080, 2) as dollar_sum_90_h_3 "
    sql += ", round(dollar_sum_90_a_4.dollar_sum_90_a / 2080, 2) as dollar_sum_90_h_4 "
    sql += ", round(dollar_sum_90_a_5.dollar_sum_90_a / 2080, 2) as dollar_sum_90_h_5 "
    sql += ", round(dollar_sum_90_a_6.dollar_sum_90_a / 2080, 2) as dollar_sum_90_h_6 "
    sql += ", round(dollar_sum_90_a_7.dollar_sum_90_a / 2080, 2) as dollar_sum_90_h_7 "
    sql += ", round(dollar_sum_90_a_8.dollar_sum_90_a / 2080, 2) as dollar_sum_90_h_8 "
    sql += ", round(dollar_sum_90_a_9.dollar_sum_90_a / 2080, 2) as dollar_sum_90_h_9 "
    sql += ", round(dollar_sum_90_a_10.dollar_sum_90_a / 2080, 2) as dollar_sum_90_h_10 "
    sql += ", round(dollar_sum_90_a_11.dollar_sum_90_a / 2080, 2) as dollar_sum_90_h_11 "
    sql += ", round(dollar_sum_90_a_12.dollar_sum_90_a / 2080, 2) as dollar_sum_90_h_12 "
    sql += ", round(dollar_sum_avg_a_0.dollar_sum_avg_a / 2080, 2) as dollar_sum_avg_h_0 "
    sql += ", round(dollar_sum_avg_a_1.dollar_sum_avg_a / 2080, 2) as dollar_sum_avg_h_1 "
    sql += ", round(dollar_sum_avg_a_2.dollar_sum_avg_a / 2080, 2) as dollar_sum_avg_h_2 "
    sql += ", round(dollar_sum_avg_a_3.dollar_sum_avg_a / 2080, 2) as dollar_sum_avg_h_3 "
    sql += ", round(dollar_sum_avg_a_4.dollar_sum_avg_a / 2080, 2) as dollar_sum_avg_h_4 "
    sql += ", round(dollar_sum_avg_a_5.dollar_sum_avg_a / 2080, 2) as dollar_sum_avg_h_5 "
    sql += ", round(dollar_sum_avg_a_6.dollar_sum_avg_a / 2080, 2) as dollar_sum_avg_h_6 "
    sql += ", round(dollar_sum_avg_a_7.dollar_sum_avg_a / 2080, 2) as dollar_sum_avg_h_7 "
    sql += ", round(dollar_sum_avg_a_8.dollar_sum_avg_a / 2080, 2) as dollar_sum_avg_h_8 "
    sql += ", round(dollar_sum_avg_a_9.dollar_sum_avg_a / 2080, 2) as dollar_sum_avg_h_9 "
    sql += ", round(dollar_sum_avg_a_10.dollar_sum_avg_a / 2080, 2) as dollar_sum_avg_h_10 "
    sql += ", round(dollar_sum_avg_a_11.dollar_sum_avg_a / 2080, 2) as dollar_sum_avg_h_11 "
    sql += ", round(dollar_sum_avg_a_12.dollar_sum_avg_a / 2080, 2) as dollar_sum_avg_h_12 "
    sql += "from "
    sql += "(select dollar_sum_avg_a from cte_final where year_count = 2) dollar_sum_avg_a_2 "
    sql += "left join (select dollar_sum_avg_a from cte_final where year_count = 3) dollar_sum_avg_a_3 on 1=1 "
    sql += "left join (select dollar_sum_avg_a from cte_final where year_count = 4) dollar_sum_avg_a_4 on 1=1 "
    sql += "left join (select dollar_sum_avg_a from cte_final where year_count = 5) dollar_sum_avg_a_5 on 1=1 "
    sql += "left join (select dollar_sum_avg_a from cte_final where year_count = 6) dollar_sum_avg_a_6 on 1=1 "
    sql += "left join (select dollar_sum_avg_a from cte_final where year_count = 7) dollar_sum_avg_a_7 on 1=1 "
    sql += "left join (select dollar_sum_avg_a from cte_final where year_count = 8) dollar_sum_avg_a_8 on 1=1 "
    sql += "left join (select dollar_sum_avg_a from cte_final where year_count = 9) dollar_sum_avg_a_9 on 1=1 "
    sql += "left join (select dollar_sum_avg_a from cte_final where year_count = 10) dollar_sum_avg_a_10 on 1=1 "
    sql += "left join (select dollar_sum_avg_a from cte_final where year_count = 11) dollar_sum_avg_a_11 on 1=1 "
    sql += "left join (select dollar_sum_avg_a from cte_final where year_count = 12) dollar_sum_avg_a_12 on 1=1 "
    sql += "left join (select dollar_sum_10_a from cte_final where year_count = 2) dollar_sum_10_a_2 on 1=1 "
    sql += "left join (select dollar_sum_10_a from cte_final where year_count = 3) dollar_sum_10_a_3 on 1=1 "
    sql += "left join (select dollar_sum_10_a from cte_final where year_count = 4) dollar_sum_10_a_4 on 1=1 "
    sql += "left join (select dollar_sum_10_a from cte_final where year_count = 5) dollar_sum_10_a_5 on 1=1 "
    sql += "left join (select dollar_sum_10_a from cte_final where year_count = 6) dollar_sum_10_a_6 on 1=1 "
    sql += "left join (select dollar_sum_10_a from cte_final where year_count = 7) dollar_sum_10_a_7 on 1=1 "
    sql += "left join (select dollar_sum_10_a from cte_final where year_count = 8) dollar_sum_10_a_8 on 1=1 "
    sql += "left join (select dollar_sum_10_a from cte_final where year_count = 9) dollar_sum_10_a_9 on 1=1 "
    sql += "left join (select dollar_sum_10_a from cte_final where year_count = 10) dollar_sum_10_a_10 on 1=1 "
    sql += "left join (select dollar_sum_10_a from cte_final where year_count = 11) dollar_sum_10_a_11 on 1=1 "
    sql += "left join (select dollar_sum_10_a from cte_final where year_count = 12) dollar_sum_10_a_12 on 1=1 "
    sql += "left join (select dollar_sum_25_a from cte_final where year_count = 2) dollar_sum_25_a_2 on 1=1 "
    sql += "left join (select dollar_sum_25_a from cte_final where year_count = 3) dollar_sum_25_a_3 on 1=1 "
    sql += "left join (select dollar_sum_25_a from cte_final where year_count = 4) dollar_sum_25_a_4 on 1=1 "
    sql += "left join (select dollar_sum_25_a from cte_final where year_count = 5) dollar_sum_25_a_5 on 1=1 "
    sql += "left join (select dollar_sum_25_a from cte_final where year_count = 6) dollar_sum_25_a_6 on 1=1 "
    sql += "left join (select dollar_sum_25_a from cte_final where year_count = 7) dollar_sum_25_a_7 on 1=1 "
    sql += "left join (select dollar_sum_25_a from cte_final where year_count = 8) dollar_sum_25_a_8 on 1=1 "
    sql += "left join (select dollar_sum_25_a from cte_final where year_count = 9) dollar_sum_25_a_9 on 1=1 "
    sql += "left join (select dollar_sum_25_a from cte_final where year_count = 10) dollar_sum_25_a_10 on 1=1 "
    sql += "left join (select dollar_sum_25_a from cte_final where year_count = 11) dollar_sum_25_a_11 on 1=1 "
    sql += "left join (select dollar_sum_25_a from cte_final where year_count = 12) dollar_sum_25_a_12 on 1=1 "
    sql += "left join (select dollar_sum_med_a from cte_final where year_count = 2) dollar_sum_median_a_2 on 1=1 "
    sql += "left join (select dollar_sum_med_a from cte_final where year_count = 3) dollar_sum_median_a_3 on 1=1 "
    sql += "left join (select dollar_sum_med_a from cte_final where year_count = 4) dollar_sum_median_a_4 on 1=1 "
    sql += "left join (select dollar_sum_med_a from cte_final where year_count = 5) dollar_sum_median_a_5 on 1=1 "
    sql += "left join (select dollar_sum_med_a from cte_final where year_count = 6) dollar_sum_median_a_6 on 1=1 "
    sql += "left join (select dollar_sum_med_a from cte_final where year_count = 7) dollar_sum_median_a_7 on 1=1 "
    sql += "left join (select dollar_sum_med_a from cte_final where year_count = 8) dollar_sum_median_a_8 on 1=1 "
    sql += "left join (select dollar_sum_med_a from cte_final where year_count = 9) dollar_sum_median_a_9 on 1=1 "
    sql += "left join (select dollar_sum_med_a from cte_final where year_count = 10) dollar_sum_median_a_10 on 1=1 "
    sql += "left join (select dollar_sum_med_a from cte_final where year_count = 11) dollar_sum_median_a_11 on 1=1 "
    sql += "left join (select dollar_sum_med_a from cte_final where year_count = 12) dollar_sum_median_a_12 on 1=1 "
    sql += "left join (select dollar_sum_75_a from cte_final where year_count = 2) dollar_sum_75_a_2 on 1=1 "
    sql += "left join (select dollar_sum_75_a from cte_final where year_count = 3) dollar_sum_75_a_3 on 1=1 "
    sql += "left join (select dollar_sum_75_a from cte_final where year_count = 4) dollar_sum_75_a_4 on 1=1 "
    sql += "left join (select dollar_sum_75_a from cte_final where year_count = 5) dollar_sum_75_a_5 on 1=1 "
    sql += "left join (select dollar_sum_75_a from cte_final where year_count = 6) dollar_sum_75_a_6 on 1=1 "
    sql += "left join (select dollar_sum_75_a from cte_final where year_count = 7) dollar_sum_75_a_7 on 1=1 "
    sql += "left join (select dollar_sum_75_a from cte_final where year_count = 8) dollar_sum_75_a_8 on 1=1 "
    sql += "left join (select dollar_sum_75_a from cte_final where year_count = 9) dollar_sum_75_a_9 on 1=1 "
    sql += "left join (select dollar_sum_75_a from cte_final where year_count = 10) dollar_sum_75_a_10 on 1=1 "
    sql += "left join (select dollar_sum_75_a from cte_final where year_count = 11) dollar_sum_75_a_11 on 1=1 "
    sql += "left join (select dollar_sum_75_a from cte_final where year_count = 12) dollar_sum_75_a_12 on 1=1 "
    sql += "left join (select dollar_sum_90_a from cte_final where year_count = 2) dollar_sum_90_a_2 on 1=1 "
    sql += "left join (select dollar_sum_90_a from cte_final where year_count = 3) dollar_sum_90_a_3 on 1=1 "
    sql += "left join (select dollar_sum_90_a from cte_final where year_count = 4) dollar_sum_90_a_4 on 1=1 "
    sql += "left join (select dollar_sum_90_a from cte_final where year_count = 5) dollar_sum_90_a_5 on 1=1 "
    sql += "left join (select dollar_sum_90_a from cte_final where year_count = 6) dollar_sum_90_a_6 on 1=1 "
    sql += "left join (select dollar_sum_90_a from cte_final where year_count = 7) dollar_sum_90_a_7 on 1=1 "
    sql += "left join (select dollar_sum_90_a from cte_final where year_count = 8) dollar_sum_90_a_8 on 1=1 "
    sql += "left join (select dollar_sum_90_a from cte_final where year_count = 9) dollar_sum_90_a_9 on 1=1 "
    sql += "left join (select dollar_sum_90_a from cte_final where year_count = 10) dollar_sum_90_a_10 on 1=1 "
    sql += "left join (select dollar_sum_90_a from cte_final where year_count = 11) dollar_sum_90_a_11 on 1=1 "
    sql += "left join (select dollar_sum_90_a from cte_final where year_count = 12) dollar_sum_90_a_12 on 1=1 "
    sql += "left join (select case when (select count(dollar_sum_avg_a) from cte_final where year_count = 0) > 0 then (select dollar_sum_avg_a from cte_final where year_count = 0) else (select 0 as dollar_sum_avg_a) end) dollar_sum_avg_a_0 on 1=1 "
    sql += "left join (select case when (select count(dollar_sum_avg_a) from cte_final where year_count = 1) > 0 then (select dollar_sum_avg_a from cte_final where year_count = 1) else (select 0 as dollar_sum_avg_a) end) dollar_sum_avg_a_1 on 1=1 "
    sql += "left join (select case when (select count(dollar_sum_10_a) from cte_final where year_count = 0) > 0 then (select dollar_sum_10_a from cte_final where year_count = 0) else (select 0 as dollar_sum_10_a) end) dollar_sum_10_a_0 on 1=1 "
    sql += "left join (select case when (select count(dollar_sum_10_a) from cte_final where year_count = 1) > 0 then (select dollar_sum_10_a from cte_final where year_count = 1) else (select 0 as dollar_sum_10_a) end) dollar_sum_10_a_1 on 1=1 "
    sql += "left join (select case when (select count(dollar_sum_25_a) from cte_final where year_count = 0) > 0 then (select dollar_sum_25_a from cte_final where year_count = 0) else (select 0 as dollar_sum_25_a) end) dollar_sum_25_a_0 on 1=1 "
    sql += "left join (select case when (select count(dollar_sum_25_a) from cte_final where year_count = 1) > 0 then (select dollar_sum_25_a from cte_final where year_count = 1) else (select 0 as dollar_sum_25_a) end) dollar_sum_25_a_1 on 1=1 "
    sql += "left join (select case when (select count(dollar_sum_med_a) from cte_final where year_count = 0) > 0 then (select dollar_sum_med_a from cte_final where year_count = 0) else (select 0 as dollar_sum_med_a) end) dollar_sum_median_a_0 on 1=1 "
    sql += "left join (select case when (select count(dollar_sum_med_a) from cte_final where year_count = 1) > 0 then (select dollar_sum_med_a from cte_final where year_count = 1) else (select 0 as dollar_sum_med_a) end) dollar_sum_median_a_1 on 1=1 "
    sql += "left join (select case when (select count(dollar_sum_75_a) from cte_final where year_count = 0) > 0 then (select dollar_sum_75_a from cte_final where year_count = 0) else (select 0 as dollar_sum_75_a) end) dollar_sum_75_a_0 on 1=1 "
    sql += "left join (select case when (select count(dollar_sum_75_a) from cte_final where year_count = 1) > 0 then (select dollar_sum_75_a from cte_final where year_count = 1) else (select 0 as dollar_sum_75_a) end) dollar_sum_75_a_1 on 1=1 "
    sql += "left join (select case when (select count(dollar_sum_90_a) from cte_final where year_count = 0) > 0 then (select dollar_sum_90_a from cte_final where year_count = 0) else (select 0 as dollar_sum_90_a) end) dollar_sum_90_a_0 on 1=1 "
    sql += "left join (select case when (select count(dollar_sum_90_a) from cte_final where year_count = 1) > 0 then (select dollar_sum_90_a from cte_final where year_count = 1) else (select 0 as dollar_sum_90_a) end) dollar_sum_90_a_1 on 1=1 "

    # print(sql)
    return query(_host_, _user_, _password_, _db_, sql)

def exponential_smoothing(df, date_range):
    window = 2
    sd = 2
    # split = 2
    split = 3
    df_len = len(df)
    metric = df.columns[0]
    ### IF BOUNDARY IS MORE THAN DOUBLE SD, THEN EQUAL 2*SD ###
    ### bollinger_strat(df, window, number_of_sd, target_column)
    pred_bounds_pct = [bollinger_strat_pct(df, window, sd)[1][-1] * 2, bollinger_strat_pct(df, window, sd)[0][-1] * 2] ### [low SD, high SD]
    
    df['akima_' + metric] = df.interpolate(method='akima')[metric]
    df_akima_sd = bollinger_strat(pd.DataFrame(df), window, sd, 'akima_' + metric)
    df['akima_sd_low'] = df_akima_sd[1]
    df['akima_sd_high'] = df_akima_sd[0]
    # print(1000, df)

    df['akima_' + metric + '_outlier'] = df['akima_' + metric]
    outliers = np.where((df['akima_' + metric + '']<df['akima_sd_low']) | (df['akima_' + metric]>df['akima_sd_high'])) 
    df.iloc[outliers[0],-1] = None
    # print(1010, df)
    
    df['akima_' + metric + '_outlier'] = df.interpolate(method='akima')['akima_' + metric + '_outlier']
    
    conditions = [
        (df['akima_' + metric + '_outlier'] > 0)
        , (df['akima_' + metric] > 0)
        , (df[metric] > 0)
    ]
    # print(1020, conditions)
    choices = [df['akima_' + metric + '_outlier'], df['akima_' + metric], df[metric]]
    df[metric + '_norm'] = np.select(conditions, choices, default=np.nan)
    df[metric + '_norm_flag'] = np.select([df[metric + '_norm'] != df[metric]], [1], default=0)
    # print(1030, df)
    normalized = df[df[metric + '_norm_flag'] == 1].index.tolist()
    # print(1040, normalized)

    train, test = pd.DataFrame(df.iloc[:df_len-split,-2]), pd.DataFrame(df.iloc[df_len-split:,-2]) ### -2 = metric + '_norm'
    # print(1050, train, test)
    pred_test = []
    error_test = []
    
    for z in range(len(date_range)): 
        model = ExponentialSmoothing(train, trend='add').fit() ##“add”, “mul”, “additive”, “multiplicative”, None
        pred_test.append(model.predict(start=test.index[z], end=test.index[z]))
        error_test.append(mse_pct_2([pred_test[z]], [test.iloc[z,0]])[0])
        
        if error_test[z] < 0.12 and pred_test[z][0] > 0 and pred_test[z][0] < 500000:    
            train.loc[test.index[z]] = int(pred_test[z]) ### Add the prediction to the training set so that will loop into the next model
        else:
     
            break
    # print(1060, pred_test, error_test)

    if max(train.index) == max(test.index):
        ### Join together the training and testing data. Replaces the training predictions with the testing actuals
        for x in range(len(test)):
            train.loc[test.index[x]] = test.iloc[x,0]
        
        pred = []
        for y in range(len(date_range)): 
            model = ExponentialSmoothing(train, trend='add').fit() ##“add”, “mul”, “additive”, “multiplicative”, None
            pred.append(model.predict(start=date_range[y], end=date_range[y]))

            if pred[y][0] > 0 and pred[y][0] < 500000:
                
#                 print(
#                     pred[y]
#                     , 'lower', (pred_bounds_pct[0]+1) * pred[y][0]
#                     , 'upper', (pred_bounds_pct[1]+1) * pred[y][0]
#                     , 'in bounds', (pred_bounds_pct[0]+1) * pred[y][0] <= pred[y][0] <= (pred_bounds_pct[1]+1) * pred[y][0]
#                 )
                
                if pred[y][0] <= (1 + pred_bounds_pct[0]) * pred[y][0]:
                    train.loc[date_range[y]] =  int(round((1 + pred_bounds_pct[0]) * pred[y][0], 0))
                elif pred[y][0] >= (1 + pred_bounds_pct[1]) * pred[y][0]:
                    train.loc[date_range[y]] =  int(round((1 + pred_bounds_pct[1]) * pred[y][0], 0))
                else:
                    train.loc[date_range[y]] = int(pred[y]) ### Add the prediction to the testing set so that it will concat at the end and loop into the next model
            else:
                break
        # print(1070, {
        #     'pred_test':pred_test
        #     , 'pred':pred
        #     , 'error':error_test
        #     , 'normalized_index':normalized
        #     , 'normalized_data':df[metric + '_norm']
        # }) 


        return {
            'pred_test':pred_test
            , 'pred':pred
            , 'error':error_test
            , 'normalized_index':normalized
            , 'normalized_data':df[metric + '_norm']
        }
        
def percentile_boundaries(df, metrics, mapping):
    for metric in metrics:
        if mapping[metric]['bottom_value'] is not None:
            ### Bottom Bottom
            df[metric] = np.where(
                (df[metric] <= df[mapping[metric]['bottom_metric']])
                , df[mapping[metric]['bottom_metric']] - mapping[metric]['bottom_value']
                , df[metric]
            )
            
            ### Bottom Top
            df[mapping[metric]['bottom_metric']] = np.where(
                (df[mapping[metric]['bottom_metric']] >= df[metric])
                , df[metric] - mapping[mapping[metric]['bottom_metric']]['top_value']
                , df[mapping[metric]['bottom_metric']]
            )
        
        if mapping[metric]['top_value'] is not None:
            ### Top Bottom
            df[metric] = np.where(
                (df[metric] >= df[mapping[metric]['top_metric']])
                , df[mapping[metric]['top_metric']] - mapping[mapping[metric]['top_metric']]['bottom_value']
                , df[metric]
            )
            
            ### Top Top
            df[mapping[metric]['top_metric']] = np.where(
                (df[mapping[metric]['top_metric']] <= df[metric])
                , df[metric] - mapping[metric]['top_value']
                , df[mapping[metric]['top_metric']]
            )
    return df

def incremental_forecast(skills_list, msa_code, user_id, schema):
    # print(1080, skills_list, msa_code, user_id, schema)

    sample = queryer(skills_list, msa_code, user_id, schema)
    # print(1090, sample)
    
    column_headers = [
        'area_title','skills_list','user_id','placeholder'
        
        ,'dollar_sum_10_a_0','dollar_sum_10_a_1','dollar_sum_10_a_2','dollar_sum_10_a_3','dollar_sum_10_a_4'
        ,'dollar_sum_10_a_5','dollar_sum_10_a_6','dollar_sum_10_a_7','dollar_sum_10_a_8','dollar_sum_10_a_9'
        ,'dollar_sum_10_a_10','dollar_sum_10_a_11','dollar_sum_10_a_12'
        
        ,'dollar_sum_25_a_0','dollar_sum_25_a_1','dollar_sum_25_a_2','dollar_sum_25_a_3','dollar_sum_25_a_4'
        ,'dollar_sum_25_a_5','dollar_sum_25_a_6','dollar_sum_25_a_7','dollar_sum_25_a_8','dollar_sum_25_a_9'
        ,'dollar_sum_25_a_10','dollar_sum_25_a_11','dollar_sum_25_a_12'
        
        ,'dollar_sum_median_a_0','dollar_sum_median_a_1','dollar_sum_median_a_2','dollar_sum_median_a_3','dollar_sum_median_a_4'
        ,'dollar_sum_median_a_5','dollar_sum_median_a_6','dollar_sum_median_a_7','dollar_sum_median_a_8','dollar_sum_median_a_9'
        ,'dollar_sum_median_a_10','dollar_sum_median_a_11','dollar_sum_median_a_12'
        
        ,'dollar_sum_75_a_0','dollar_sum_75_a_1','dollar_sum_75_a_2','dollar_sum_75_a_3','dollar_sum_75_a_4'
        ,'dollar_sum_75_a_5','dollar_sum_75_a_6','dollar_sum_75_a_7','dollar_sum_75_a_8','dollar_sum_75_a_9'
        ,'dollar_sum_75_a_10','dollar_sum_75_a_11','dollar_sum_75_a_12'
        
        ,'dollar_sum_90_a_0','dollar_sum_90_a_1','dollar_sum_90_a_2','dollar_sum_90_a_3','dollar_sum_90_a_4'
        ,'dollar_sum_90_a_5','dollar_sum_90_a_6','dollar_sum_90_a_7','dollar_sum_90_a_8','dollar_sum_90_a_9'
        ,'dollar_sum_90_a_10','dollar_sum_90_a_11','dollar_sum_90_a_12'
        
        ,'dollar_sum_avg_a_0','dollar_sum_avg_a_1','dollar_sum_avg_a_2','dollar_sum_avg_a_3','dollar_sum_avg_a_4'
        ,'dollar_sum_avg_a_5','dollar_sum_avg_a_6','dollar_sum_avg_a_7','dollar_sum_avg_a_8','dollar_sum_avg_a_9'
        ,'dollar_sum_avg_a_10','dollar_sum_avg_a_11','dollar_sum_avg_a_12'
        
        ,'dollar_sum_10_h_0','dollar_sum_10_h_1','dollar_sum_10_h_2','dollar_sum_10_h_3','dollar_sum_10_h_4'
        ,'dollar_sum_10_h_5','dollar_sum_10_h_6','dollar_sum_10_h_7','dollar_sum_10_h_8','dollar_sum_10_h_9'
        ,'dollar_sum_10_h_10','dollar_sum_10_h_11','dollar_sum_10_h_12'
        
        ,'dollar_sum_25_h_0','dollar_sum_25_h_1','dollar_sum_25_h_2','dollar_sum_25_h_3','dollar_sum_25_h_4'
        ,'dollar_sum_25_h_5','dollar_sum_25_h_6','dollar_sum_25_h_7','dollar_sum_25_h_8','dollar_sum_25_h_9'
        ,'dollar_sum_25_h_10','dollar_sum_25_h_11','dollar_sum_25_h_12'
        
        ,'dollar_sum_median_h_0','dollar_sum_median_h_1','dollar_sum_median_h_2','dollar_sum_median_h_3','dollar_sum_median_h_4'
        ,'dollar_sum_median_h_5','dollar_sum_median_h_6','dollar_sum_median_h_7','dollar_sum_median_h_8','dollar_sum_median_h_9'
        ,'dollar_sum_median_h_10','dollar_sum_median_h_11','dollar_sum_median_h_12'
        
        ,'dollar_sum_75_h_0','dollar_sum_75_h_1','dollar_sum_75_h_2','dollar_sum_75_h_3','dollar_sum_75_h_4'
        ,'dollar_sum_75_h_5','dollar_sum_75_h_6','dollar_sum_75_h_7','dollar_sum_75_h_8','dollar_sum_75_h_9'
        ,'dollar_sum_75_h_10','dollar_sum_75_h_11','dollar_sum_75_h_12'
        
        ,'dollar_sum_90_h_0','dollar_sum_90_h_1','dollar_sum_90_h_2','dollar_sum_90_h_3','dollar_sum_90_h_4'
        ,'dollar_sum_90_h_5','dollar_sum_90_h_6','dollar_sum_90_h_7','dollar_sum_90_h_8','dollar_sum_90_h_9'
        ,'dollar_sum_90_h_10','dollar_sum_90_h_11','dollar_sum_90_h_12'
        
        ,'dollar_sum_avg_h_0','dollar_sum_avg_h_1','dollar_sum_avg_h_2','dollar_sum_avg_h_3','dollar_sum_avg_h_4'
        ,'dollar_sum_avg_h_5','dollar_sum_avg_h_6','dollar_sum_avg_h_7','dollar_sum_avg_h_8','dollar_sum_avg_h_9'
        ,'dollar_sum_avg_h_10','dollar_sum_avg_h_11','dollar_sum_avg_h_12'
    ]

    wage_json = pd.DataFrame(sample)
    wage_json.columns = column_headers

    a_10 = wage_json.loc[:,'dollar_sum_10_a_2':'dollar_sum_10_a_12'].T
    a_25 = wage_json.loc[:,'dollar_sum_25_a_2':'dollar_sum_25_a_12'].T
    a_median = wage_json.loc[:,'dollar_sum_median_a_2':'dollar_sum_median_a_12'].T
    a_75 = wage_json.loc[:,'dollar_sum_75_a_2':'dollar_sum_75_a_12'].T
    a_90 = wage_json.loc[:,'dollar_sum_90_a_2':'dollar_sum_90_a_12'].T
    a_avg = wage_json.loc[:,'dollar_sum_avg_a_2':'dollar_sum_avg_a_12'].T

    all_data = []
    
    area_code = msa_code
    skills = '{' + ','.join(str(skills_list).strip('][').replace("'",'').split(',')) + '}'
    user_id = user_id
    dataset_id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(30))

    date_range = [
         '2021-01-01' #2
         , '2020-01-01' #3
         , '2019-01-01' #4
         , '2018-01-01' #5
         , '2017-01-01' #6
         , '2016-01-01' #7
         , '2015-01-01' #8
         , '2014-01-01' #9
         , '2013-01-01' #10
         , '2012-01-01' #11
         , '2011-01-01' #12
    ]

    metrics_names = ['a_10', 'a_25', 'a_median', 'a_75', 'a_90', 'a_avg'] 
    metrics = {'a_10':a_10, 'a_25':a_25, 'a_median':a_median, 'a_75':a_75, 'a_90':a_90, 'a_avg':a_avg}
    # print(1100, metrics)


    df_diff = pd.DataFrame([
        date_range
        , a_10.iloc[:,0].tolist()
        , a_25.iloc[:,0].tolist()
        , a_median.iloc[:,0].tolist()
        , a_75.iloc[:,0].tolist()
        , a_90.iloc[:,0].tolist()
        , a_avg.iloc[:,0].tolist()
        ]).T.set_index(0).sort_index()
    df_diff.columns = metrics_names
    df_diff.index = pd.to_datetime(df_diff.index)

    periods = 3
    
    date_list = pd.date_range(date_range[0], freq='Y', periods=periods) #pulls the max date and adds 2 periods
    date_list = [f + pd.DateOffset(days=1) for f in date_list]

    ########################################################################################## No lower bound limit for 10th percentile (there should be...)
    diff_10_25  = list(metrics['a_25'] - metrics['a_10'].rolling(4).mean())[-1] ### 10th percentile cannot be higher than this

    diff_25_10  = list(metrics['a_10'] - metrics['a_25'].rolling(4).mean())[-1] ### 25th percentile cannot be lower than this
    diff_25_med = list(metrics['a_median'] - metrics['a_25'].rolling(4).mean())[-1] ### 25th percentile cannot be higher than this

    diff_med_25 = list(metrics['a_25'] - metrics['a_median'].rolling(4).mean())[-1] ### 50th percentile cannot be lower than this
    diff_med_75 = list(metrics['a_75'] - metrics['a_median'].rolling(4).mean())[-1] ### 50th percentile cannot be higher than this

    diff_75_med = list(metrics['a_median'] - metrics['a_75'].rolling(4).mean())[-1] ### 75th percentile cannot be lower than this
    diff_75_90  = list(metrics['a_90'] - metrics['a_75'].rolling(4).mean())[-1] ### 75th percentile cannot be higher than this

    diff_90_75  = list(metrics['a_75'] - metrics['a_90'].rolling(4).mean())[-1] ### 90th percentile cannot be lower than this
    diff = [diff_10_25, diff_25_10, diff_25_med, diff_med_25, diff_med_75, diff_75_med, diff_75_90, diff_90_75]
    # print(1110, diff)
    ########################################################################################## No upper bound limit for 90th percentile (there kind of should be...)

    boundary_mapping = {
        'a_10': {'top_metric':'a_25', 'top_value': diff_10_25, 'bottom_metric':None, 'bottom_value': None}
        , 'a_25': {'top_metric':'a_median', 'top_value': diff_25_med, 'bottom_metric':'a_10', 'bottom_value': diff_25_10}
        , 'a_median': {'top_metric':'a_75', 'top_value': diff_med_75, 'bottom_metric':'a_25', 'bottom_value': diff_med_25}
        , 'a_75': {'top_metric':'a_90', 'top_value': diff_75_90, 'bottom_metric':'a_median', 'bottom_value': diff_75_med}
        , 'a_90': {'top_metric':None,  'top_value': None, 'bottom_metric':'a_75', 'bottom_value': diff_90_75}
        , 'a_avg': {'top_metric':None,  'top_value': None, 'bottom_metric':None, 'bottom_value': None}
    }
    # print(1120, boundary_mapping)

    metric_block = []

    for metric in metrics.keys():
        df = metrics[metric].reset_index(drop=True)
        df['years'] = date_range
        # print(1130, df)
        df = df.set_index('years')
        df.index = pd.to_datetime(df.index)
        df.columns = [metric]
        df[metric] = pd.to_numeric(df[metric], errors='coerce')
        df = df.iloc[::-1]

        window = 2
        sd = 2
        split = 3
        df_len = len(df)
        metric = df.columns[0]
        ### IF BOUNDARY IS MORE THAN DOUBLE SD, THEN EQUAL 2*SD ###
        ### bollinger_strat(df, window, number_of_sd, target_column)
        pred_bounds_pct = [bollinger_strat_pct(df, window, sd)[1][-1] * 2, bollinger_strat_pct(df, window, sd)[0][-1] * 2] ### [low SD, high SD]

        df['akima_' + metric] = df.interpolate(method='akima')[metric]
        df_akima_sd = bollinger_strat(pd.DataFrame(df), window, sd, 'akima_' + metric)
        df['akima_sd_low'] = df_akima_sd[1]
        df['akima_sd_high'] = df_akima_sd[0]

        df['akima_' + metric + '_outlier'] = df['akima_' + metric]
        outliers = np.where((df['akima_' + metric + '']<df['akima_sd_low']) | (df['akima_' + metric]>df['akima_sd_high'])) 
        df.iloc[outliers[0],-1] = None

        df['akima_' + metric + '_outlier'] = df.interpolate(method='akima')['akima_' + metric + '_outlier']

        conditions = [
            (df['akima_' + metric + '_outlier'] > 0)
            , (df['akima_' + metric] > 0)
            , (df[metric] > 0)
        ]
        choices = [df['akima_' + metric + '_outlier'], df['akima_' + metric], df[metric]]
        df[metric + '_norm'] = np.select(conditions, choices, default=np.nan)
        df[metric + '_norm_flag'] = np.select([df[metric + '_norm'] != df[metric]], [1], default=0)
        normalized = df[df[metric + '_norm_flag'] == 1].index.tolist()

        train, test = pd.DataFrame(df.iloc[:df_len-split,-2]), pd.DataFrame(df.iloc[df_len-split:,-2]) ### -2 = metric + '_norm'

        pred_test = []
        error_test = []

        # print(train, test)

        for z in range(len(date_list)): 
            model = ExponentialSmoothing(train, trend='add').fit() ##“add”, “mul”, “additive”, “multiplicative”, None
            pred_test.append(model.predict(start=test.index[z], end=test.index[z]))
            error_test.append(mse_pct_2([pred_test[z]], [test.iloc[z,0]])[0])

            if error_test[z] < 0.12 and pred_test[z][0] > 0 and pred_test[z][0] < 500000:    
                train.loc[test.index[z]] = int(pred_test[z]) ### Add the prediction to the training set so that will loop into the next model
            else:
                break
                
        if max(train.index) == max(test.index):
            ### Join together the training and testing data. Replaces the training predictions with the testing actuals
            for x in range(len(test)):
                train.loc[test.index[x]] = test.iloc[x,0]

            pred = []
            for y in range(len(date_list)): 
                model = ExponentialSmoothing(train, trend='add').fit() ##“add”, “mul”, “additive”, “multiplicative”, None
                pred.append(model.predict(start=date_list[y], end=date_list[y]))

                if pred[y][0] > 0 and pred[y][0] < 500000:

                    # print(
                    #     pred[y],'\n'
                    #     , 'lower', (pred_bounds_pct[0]+1) * pred[y][0],'\n'
                    #     , 'upper', (pred_bounds_pct[1]+1) * pred[y][0],'\n'
                    #     , 'in bounds', (pred_bounds_pct[0]+1) * pred[y][0] <= pred[y][0] <= (pred_bounds_pct[1]+1) * pred[y][0]
                    # )

                    if pred[y][0] <= (1 + pred_bounds_pct[0]) * pred[y][0]:
                        train.loc[date_range[y]] =  int(round((1 + pred_bounds_pct[0]) * pred[y][0], 0))
                    elif pred[y][0] >= (1 + pred_bounds_pct[1]) * pred[y][0]:
                        train.loc[date_range[y]] =  int(round((1 + pred_bounds_pct[1]) * pred[y][0], 0))
                    else:
                        train.loc[date_range[y]] = int(pred[y]) ### Add the prediction to the testing set so that it will concat at the end and loop into the next model
                else:
                    break
        else:
            ### Join together the training and testing data. Replaces the training predictions with the testing actuals
            for x in range(len(test)):
                train.loc[test.index[x]] = test.iloc[x,0]
                
            pred = []
                    
        metric_block.append([metric, {
                'pred_test':pred_test
                , 'pred':pred
                , 'error':error_test
                , 'normalized_index':normalized
                , 'normalized_data':df[metric + '_norm']
            }])

        metric_block_dfs = []
        for i in range(len(metric_block)):
            try:
                df_temp = pd.DataFrame(metric_block[i][1]['pred']).T
                df_temp = df_temp.fillna(0).iloc[:,0] + df_temp.fillna(0).iloc[:,1]
                if len(df_temp) != 0:
                    metric_block_dfs.append(pd.DataFrame(df_temp,columns=[metric_block[i][0]]))
            except Exception as e:
#                 print(1, wage_json[0], wage_json[1], wage_json[2], wage_json[3]['area'], e, '\n')
                pass

    # print(1130, metric_block)
    # print(1131, metric_block_dfs)
        
    try:
        data_merge = reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True), metric_block_dfs) # Merge DataFrames in list
        ### IF THERE ARE NO SUCCESSFUL FORECASTS, THIS WILL FAIL
        # print(1140, data_merge)
        all_df = pd.concat([df_diff, data_merge])
        percentile_df = percentile_boundaries(all_df, metrics, boundary_mapping)
        percentile_df.index = pd.to_datetime(percentile_df.index).astype(str)
        percentile_df.reset_index(inplace=True)
        # print(1150, percentile_df)
        # print(percentile_df)

        insert_pred_query = "INSERT INTO {}.skills_incremental_02 VALUES ".format(schema)
        insert_pred_query += "('" + area_code + "','" + skills + "','" + str(user_id) + "','" + dataset_id + "','"
        try:
            insert_pred_query += percentile_df.to_json(orient='columns')
        except:
            try:
                insert_pred_query += all_df.to_json(orient='columns')
            except:
                pass

        insert_pred_query += "')"
        insert_pred_query += ";COMMIT;"

        # print(insert_pred_query,'\n')
        
        try:
            execute_query(_host_, _user_, _password_, _db_, insert_pred_query)
            return dataset_id
        except Exception as e:
            print("1", e)
            # pass

    except Exception as e:
        print("2", e)
        ### IF THERE ARE NO FORECASTS, JUST RETURN THE ORIGINAL DATASET
        # print(sample[0])
        # return sample[0]
        # pass
        print(3, date_list)

        data_stage = {
            'index':date_list
            , 'a_10':[None] * len(date_list)
            , 'a_25':[None] * len(date_list)
            , 'a_median':[None] * len(date_list)
            , 'a_75':[None] * len(date_list)
            , 'a_90':[None] * len(date_list)
            , 'a_avg':[None] * len(date_list)
        }
        # print(3, data_stage)

        # print(data_stage)
        # print("THERE ARE NO FORECASTS! AHHHH!")
        df_diff = df_diff.reset_index()
        df_diff.columns =  ['index', 'a_10', 'a_25', 'a_median', 'a_75', 'a_90', 'a_avg']

        # print(1, df_diff, pd.DataFrame(data_stage))

        df = pd.concat([df_diff, pd.DataFrame(data_stage)]).reset_index(drop=True)
        # print(2, df)

        try:
            insert_pred_query = "INSERT INTO {}.skills_incremental_02 VALUES ".format(schema)
            insert_pred_query += "('" + area_code + "','" + skills + "','" + str(user_id) + "','" + dataset_id + "','"
            try:
                insert_pred_query += df.to_json(orient='columns')
            except:
                pass
                # try:
                #     insert_pred_query += all_df.to_json(orient='columns')
                # except:
                #     pass

            insert_pred_query += "')"
            insert_pred_query += ";COMMIT;"

            # print(insert_pred_query,'\n')
        
            try:
                execute_query(_host_, _user_, _password_, _db_, insert_pred_query)
                return dataset_id
            except Exception as e:
                print("1", e)
                # pass
        except Exception as e:
            print("3", e)

        # print("2", e)

def queryer2(dataset_id, schema):
    sql = "SELECT "
    sql += "si.msa_code "                                                                                   #0
    sql += ", si.skills "                                                                                   #1
    sql += ", si.user_id "                                                                                  #2
    sql += ", si.dataset_id "                                                                               #3    
    sql += ", CAST(si.json_data -> 'a_10' ->> '0' AS INT) AS a_10_0 "                                       #4                                            
    sql += ", CAST(si.json_data -> 'a_10' ->> '1' AS INT) AS a_10_1 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_10' ->> '2' AS INT) AS a_10_2 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_10' ->> '3' AS INT) AS a_10_3 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_10' ->> '4' AS INT) AS a_10_4 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_10' ->> '5' AS INT) AS a_10_5 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_10' ->> '6' AS INT) AS a_10_6 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_10' ->> '7' AS INT) AS a_10_7 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_10' ->> '8' AS INT) AS a_10_8 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_10' ->> '9' AS INT) AS a_10_9 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_10' ->> '10' AS INT) AS a_10_10 "                                                                               
    sql += ", ROUND(CAST(si.json_data -> 'a_10' ->> '11' AS NUMERIC), 0)::INT AS a_10_11 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_10' ->> '12' AS NUMERIC), 0)::INT AS a_10_12 "                  #16                                                                
    sql += ", CAST(si.json_data -> 'a_25' ->> '0' AS INT) AS a_25_0 "                                       #17                                            
    sql += ", CAST(si.json_data -> 'a_25' ->> '1' AS INT) AS a_25_1 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_25' ->> '2' AS INT) AS a_25_2 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_25' ->> '3' AS INT) AS a_25_3 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_25' ->> '4' AS INT) AS a_25_4 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_25' ->> '5' AS INT) AS a_25_5 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_25' ->> '6' AS INT) AS a_25_6 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_25' ->> '7' AS INT) AS a_25_7 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_25' ->> '8' AS INT) AS a_25_8 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_25' ->> '9' AS INT) AS a_25_9 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_25' ->> '10' AS INT) AS a_25_10 "                                                                                 
    sql += ", ROUND(CAST(si.json_data -> 'a_25' ->> '11' AS NUMERIC), 0)::INT AS a_25_11 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_25' ->> '12' AS NUMERIC), 0)::INT AS a_25_12 "                  #29                                                                
    sql += ", CAST(si.json_data -> 'a_median' ->> '0' AS INT) AS a_median_0 "                               #30                                                    
    sql += ", CAST(si.json_data -> 'a_median' ->> '1' AS INT) AS a_median_1 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_median' ->> '2' AS INT) AS a_median_2 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_median' ->> '3' AS INT) AS a_median_3 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_median' ->> '4' AS INT) AS a_median_4 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_median' ->> '5' AS INT) AS a_median_5 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_median' ->> '6' AS INT) AS a_median_6 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_median' ->> '7' AS INT) AS a_median_7 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_median' ->> '8' AS INT) AS a_median_8 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_median' ->> '9' AS INT) AS a_median_9 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_median' ->> '10' AS INT) AS a_median_10 "                                                                                 
    sql += ", ROUND(CAST(si.json_data -> 'a_median' ->> '11' AS NUMERIC), 0)::INT AS a_median_11 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_median' ->> '12' AS NUMERIC), 0)::INT AS a_median_12 "          #42                                                                        
    sql += ", CAST(si.json_data -> 'a_75' ->> '0' AS INT) AS a_75_0 "                                       #43                                            
    sql += ", CAST(si.json_data -> 'a_75' ->> '1' AS INT) AS a_75_1 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_75' ->> '2' AS INT) AS a_75_2 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_75' ->> '3' AS INT) AS a_75_3 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_75' ->> '4' AS INT) AS a_75_4 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_75' ->> '5' AS INT) AS a_75_5 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_75' ->> '6' AS INT) AS a_75_6 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_75' ->> '7' AS INT) AS a_75_7 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_75' ->> '8' AS INT) AS a_75_8 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_75' ->> '9' AS INT) AS a_75_9 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_75' ->> '10' AS INT) AS a_75_10 "                                                                                 
    sql += ", ROUND(CAST(si.json_data -> 'a_75' ->> '11' AS NUMERIC), 0)::INT AS a_75_11 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_75' ->> '12' AS NUMERIC), 0)::INT AS a_75_12 "                  #55                                                                
    sql += ", CAST(si.json_data -> 'a_90' ->> '0' AS INT) AS a_90_0 "                                       #56                                            
    sql += ", CAST(si.json_data -> 'a_90' ->> '1' AS INT) AS a_90_1 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_90' ->> '2' AS INT) AS a_90_2 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_90' ->> '3' AS INT) AS a_90_3 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_90' ->> '4' AS INT) AS a_90_4 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_90' ->> '5' AS INT) AS a_90_5 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_90' ->> '6' AS INT) AS a_90_6 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_90' ->> '7' AS INT) AS a_90_7 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_90' ->> '8' AS INT) AS a_90_8 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_90' ->> '9' AS INT) AS a_90_9 "                                                                                   
    sql += ", CAST(si.json_data -> 'a_90' ->> '10' AS INT) AS a_90_10 "                                                                                 
    sql += ", ROUND(CAST(si.json_data -> 'a_90' ->> '11' AS NUMERIC), 0)::INT AS a_90_11 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_90' ->> '12' AS NUMERIC), 0)::INT AS a_90_12 "                  #68                                                                
    sql += ", CAST(si.json_data -> 'a_avg' ->> '0' AS INT) AS a_avg_0 "                                     #69                                            
    sql += ", CAST(si.json_data -> 'a_avg' ->> '1' AS INT) AS a_avg_1 "                                                                                 
    sql += ", CAST(si.json_data -> 'a_avg' ->> '2' AS INT) AS a_avg_2 "                                                                                 
    sql += ", CAST(si.json_data -> 'a_avg' ->> '3' AS INT) AS a_avg_3 "                                                                                 
    sql += ", CAST(si.json_data -> 'a_avg' ->> '4' AS INT) AS a_avg_4 "                                                                                 
    sql += ", CAST(si.json_data -> 'a_avg' ->> '5' AS INT) AS a_avg_5 "                                                                                 
    sql += ", CAST(si.json_data -> 'a_avg' ->> '6' AS INT) AS a_avg_6 "                                                                                 
    sql += ", CAST(si.json_data -> 'a_avg' ->> '7' AS INT) AS a_avg_7 "                                                                                 
    sql += ", CAST(si.json_data -> 'a_avg' ->> '8' AS INT) AS a_avg_8 "                                                                                 
    sql += ", CAST(si.json_data -> 'a_avg' ->> '9' AS INT) AS a_avg_9 "                                                                                 
    sql += ", CAST(si.json_data -> 'a_avg' ->> '10' AS INT) AS a_avg_10 "                                                                                   
    sql += ", ROUND(CAST(si.json_data -> 'a_avg' ->> '11' AS NUMERIC), 0)::INT AS a_avg_11 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_avg' ->> '12' AS NUMERIC), 0)::INT AS a_avg_12 "                #81                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_10' ->> '0' AS NUMERIC)/2080, 2) AS h_10_0 "                    #82                                                                
    sql += ", ROUND(CAST(si.json_data -> 'a_10' ->> '1' AS NUMERIC)/2080, 2) AS h_10_1 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_10' ->> '2' AS NUMERIC)/2080, 2) AS h_10_2 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_10' ->> '3' AS NUMERIC)/2080, 2) AS h_10_3 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_10' ->> '4' AS NUMERIC)/2080, 2) AS h_10_4 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_10' ->> '5' AS NUMERIC)/2080, 2) AS h_10_5 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_10' ->> '6' AS NUMERIC)/2080, 2) AS h_10_6 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_10' ->> '7' AS NUMERIC)/2080, 2) AS h_10_7 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_10' ->> '8' AS NUMERIC)/2080, 2) AS h_10_8 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_10' ->> '9' AS NUMERIC)/2080, 2) AS h_10_9 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_10' ->> '10' AS NUMERIC)/2080, 2) AS h_10_10 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_10' ->> '11' AS NUMERIC)/2080, 2) AS h_10_11 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_10' ->> '12' AS NUMERIC)/2080, 2) AS h_10_12 "                  #94                                                                
    sql += ", ROUND(CAST(si.json_data -> 'a_25' ->> '0' AS NUMERIC)/2080, 2) AS h_25_0 "                    #95                                                                
    sql += ", ROUND(CAST(si.json_data -> 'a_25' ->> '1' AS NUMERIC)/2080, 2) AS h_25_1 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_25' ->> '2' AS NUMERIC)/2080, 2) AS h_25_2 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_25' ->> '3' AS NUMERIC)/2080, 2) AS h_25_3 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_25' ->> '4' AS NUMERIC)/2080, 2) AS h_25_4 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_25' ->> '5' AS NUMERIC)/2080, 2) AS h_25_5 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_25' ->> '6' AS NUMERIC)/2080, 2) AS h_25_6 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_25' ->> '7' AS NUMERIC)/2080, 2) AS h_25_7 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_25' ->> '8' AS NUMERIC)/2080, 2) AS h_25_8 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_25' ->> '9' AS NUMERIC)/2080, 2) AS h_25_9 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_25' ->> '10' AS NUMERIC)/2080, 2) AS h_25_10 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_25' ->> '11' AS NUMERIC)/2080, 2) AS h_25_11 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_25' ->> '12' AS NUMERIC)/2080, 2) AS h_25_12 "                  #107                                                                
    sql += ", ROUND(CAST(si.json_data -> 'a_median' ->> '0' AS NUMERIC)/2080, 2) AS h_median_0 "            #108                                                                        
    sql += ", ROUND(CAST(si.json_data -> 'a_median' ->> '1' AS NUMERIC)/2080, 2) AS h_median_1 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_median' ->> '2' AS NUMERIC)/2080, 2) AS h_median_2 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_median' ->> '3' AS NUMERIC)/2080, 2) AS h_median_3 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_median' ->> '4' AS NUMERIC)/2080, 2) AS h_median_4 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_median' ->> '5' AS NUMERIC)/2080, 2) AS h_median_5 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_median' ->> '6' AS NUMERIC)/2080, 2) AS h_median_6 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_median' ->> '7' AS NUMERIC)/2080, 2) AS h_median_7 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_median' ->> '8' AS NUMERIC)/2080, 2) AS h_median_8 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_median' ->> '9' AS NUMERIC)/2080, 2) AS h_median_9 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_median' ->> '10' AS NUMERIC)/2080, 2) AS h_median_10 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_median' ->> '11' AS NUMERIC)/2080, 2) AS h_median_11 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_median' ->> '12' AS NUMERIC)/2080, 2) AS h_median_12 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_75' ->> '0' AS NUMERIC)/2080, 2) AS h_75_0 "                    #120                                                                
    sql += ", ROUND(CAST(si.json_data -> 'a_75' ->> '1' AS NUMERIC)/2080, 2) AS h_75_1 "                    #121                                                                
    sql += ", ROUND(CAST(si.json_data -> 'a_75' ->> '2' AS NUMERIC)/2080, 2) AS h_75_2 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_75' ->> '3' AS NUMERIC)/2080, 2) AS h_75_3 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_75' ->> '4' AS NUMERIC)/2080, 2) AS h_75_4 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_75' ->> '5' AS NUMERIC)/2080, 2) AS h_75_5 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_75' ->> '6' AS NUMERIC)/2080, 2) AS h_75_6 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_75' ->> '7' AS NUMERIC)/2080, 2) AS h_75_7 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_75' ->> '8' AS NUMERIC)/2080, 2) AS h_75_8 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_75' ->> '9' AS NUMERIC)/2080, 2) AS h_75_9 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_75' ->> '10' AS NUMERIC)/2080, 2) AS h_75_10 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_75' ->> '11' AS NUMERIC)/2080, 2) AS h_75_11 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_75' ->> '12' AS NUMERIC)/2080, 2) AS h_75_12 "                  #133                                                                
    sql += ", ROUND(CAST(si.json_data -> 'a_90' ->> '0' AS NUMERIC)/2080, 2) AS h_90_0 "                    #134                                                                
    sql += ", ROUND(CAST(si.json_data -> 'a_90' ->> '1' AS NUMERIC)/2080, 2) AS h_90_1 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_90' ->> '2' AS NUMERIC)/2080, 2) AS h_90_2 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_90' ->> '3' AS NUMERIC)/2080, 2) AS h_90_3 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_90' ->> '4' AS NUMERIC)/2080, 2) AS h_90_4 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_90' ->> '5' AS NUMERIC)/2080, 2) AS h_90_5 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_90' ->> '6' AS NUMERIC)/2080, 2) AS h_90_6 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_90' ->> '7' AS NUMERIC)/2080, 2) AS h_90_7 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_90' ->> '8' AS NUMERIC)/2080, 2) AS h_90_8 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_90' ->> '9' AS NUMERIC)/2080, 2) AS h_90_9 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_90' ->> '10' AS NUMERIC)/2080, 2) AS h_90_10 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_90' ->> '11' AS NUMERIC)/2080, 2) AS h_90_11 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_90' ->> '12' AS NUMERIC)/2080, 2) AS h_90_12 "                  #146                                                                
    sql += ", ROUND(CAST(si.json_data -> 'a_avg' ->> '0' AS NUMERIC)/2080, 2) AS a_avg_0 "                  #147                                                                
    sql += ", ROUND(CAST(si.json_data -> 'a_avg' ->> '1' AS NUMERIC)/2080, 2) AS a_avg_1 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_avg' ->> '2' AS NUMERIC)/2080, 2) AS a_avg_2 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_avg' ->> '3' AS NUMERIC)/2080, 2) AS a_avg_3 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_avg' ->> '4' AS NUMERIC)/2080, 2) AS a_avg_4 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_avg' ->> '5' AS NUMERIC)/2080, 2) AS a_avg_5 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_avg' ->> '6' AS NUMERIC)/2080, 2) AS a_avg_6 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_avg' ->> '7' AS NUMERIC)/2080, 2) AS a_avg_7 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_avg' ->> '8' AS NUMERIC)/2080, 2) AS a_avg_8 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_avg' ->> '9' AS NUMERIC)/2080, 2) AS a_avg_9 "                                                                                  
    sql += ", ROUND(CAST(si.json_data -> 'a_avg' ->> '10' AS NUMERIC)/2080, 2) AS a_avg_10 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_avg' ->> '11' AS NUMERIC)/2080, 2) AS a_avg_11 "                                                                                    
    sql += ", ROUND(CAST(si.json_data -> 'a_avg' ->> '12' AS NUMERIC)/2080, 2) AS a_avg_12 "                #159 
    sql += ", JSON_BUILD_OBJECT( "
    sql += "'employment', JSON_BUILD_OBJECT( "
    sql += "'labor_force', ROW( "
    sql += "labor_force_0 "
    sql += ", labor_force_1 "
    sql += ", labor_force_2 "
    sql += ", labor_force_3 "
    sql += ", labor_force_4 "
    sql += ", labor_force_5 "
    sql += ", labor_force_6 "
    sql += ", labor_force_7 "
    sql += ", labor_force_8 "
    sql += ", labor_force_9 "
    sql += ", labor_force_10 "
    sql += ", labor_force_11 "
    sql += ", labor_force_12 "
    sql += ", labor_force_13 "
    sql += ", labor_force_14 "
    sql += ", labor_force_15 "
    sql += ", labor_force_16 "
    sql += ", labor_force_17 "
    sql += ", labor_force_18 "
    sql += ", labor_force_19 "
    sql += ", labor_force_20 "
    sql += ", labor_force_21 "
    sql += ", labor_force_22 "
    sql += ", labor_force_23 "
    sql += ", labor_force_24 "
    sql += ", labor_force_25 "
    sql += ", labor_force_26 "
    sql += ", labor_force_27 "
    sql += ", labor_force_28 "
    sql += ", labor_force_29 "
    sql += ", labor_force_30 "
    sql += ", labor_force_31 "
    sql += ", labor_force_32 "
    sql += ", labor_force_33 "
    sql += ", labor_force_34 "
    sql += ", labor_force_35 "
    sql += ", labor_force_36 "
    sql += ", labor_force_37 "
    sql += ", labor_force_38 "
    sql += ", labor_force_39 "
    sql += ", labor_force_40 "
    sql += ", labor_force_41 "
    sql += ", labor_force_42 "
    sql += ", labor_force_43 "
    sql += ", labor_force_44 "
    sql += ", labor_force_45 "
    sql += ", labor_force_46 "
    sql += ", labor_force_47 "
    sql += ", labor_force_48 "
    sql += ") "
    sql += ", 'employment', ROW( "
    sql += "employment_0 "
    sql += ", employment_1 "
    sql += ", employment_2 "
    sql += ", employment_3 "
    sql += ", employment_4 "
    sql += ", employment_5 "
    sql += ", employment_6 "
    sql += ", employment_7 "
    sql += ", employment_8 "
    sql += ", employment_9 "
    sql += ", employment_10 "
    sql += ", employment_11 "
    sql += ", employment_12 "
    sql += ", employment_13 "
    sql += ", employment_14 "
    sql += ", employment_15 "
    sql += ", employment_16 "
    sql += ", employment_17 "
    sql += ", employment_18 "
    sql += ", employment_19 "
    sql += ", employment_20 "
    sql += ", employment_21 "
    sql += ", employment_22 "
    sql += ", employment_23 "
    sql += ", employment_24 "
    sql += ", employment_25 "
    sql += ", employment_26 "
    sql += ", employment_27 "
    sql += ", employment_28 "
    sql += ", employment_29 "
    sql += ", employment_30 "
    sql += ", employment_31 "
    sql += ", employment_32 "
    sql += ", employment_33 "
    sql += ", employment_34 "
    sql += ", employment_35 "
    sql += ", employment_36 "
    sql += ", employment_37 "
    sql += ", employment_38 "
    sql += ", employment_39 "
    sql += ", employment_40 "
    sql += ", employment_41 "
    sql += ", employment_42 "
    sql += ", employment_43 "
    sql += ", employment_44 "
    sql += ", employment_45 "
    sql += ", employment_46 "
    sql += ", employment_47 "
    sql += ", employment_48 "
    sql += ") "
    sql += ", 'unemployment', ROW( "
    sql += "unemployment_0 "
    sql += ", unemployment_1 "
    sql += ", unemployment_2 "
    sql += ", unemployment_3 "
    sql += ", unemployment_4 "
    sql += ", unemployment_5 "
    sql += ", unemployment_6 "
    sql += ", unemployment_7 "
    sql += ", unemployment_8 "
    sql += ", unemployment_9 "
    sql += ", unemployment_10 "
    sql += ", unemployment_11 "
    sql += ", unemployment_12 "
    sql += ", unemployment_13 "
    sql += ", unemployment_14 "
    sql += ", unemployment_15 "
    sql += ", unemployment_16 "
    sql += ", unemployment_17 "
    sql += ", unemployment_18 "
    sql += ", unemployment_19 "
    sql += ", unemployment_20 "
    sql += ", unemployment_21 "
    sql += ", unemployment_22 "
    sql += ", unemployment_23 "
    sql += ", unemployment_24 "
    sql += ", unemployment_25 "
    sql += ", unemployment_26 "
    sql += ", unemployment_27 "
    sql += ", unemployment_28 "
    sql += ", unemployment_29 "
    sql += ", unemployment_30 "
    sql += ", unemployment_31 "
    sql += ", unemployment_32 "
    sql += ", unemployment_33 "
    sql += ", unemployment_34 "
    sql += ", unemployment_35 "
    sql += ", unemployment_36 "
    sql += ", unemployment_37 "
    sql += ", unemployment_38 "
    sql += ", unemployment_39 "
    sql += ", unemployment_40 "
    sql += ", unemployment_41 "
    sql += ", unemployment_42 "
    sql += ", unemployment_43 "
    sql += ", unemployment_44 "
    sql += ", unemployment_45 "
    sql += ", unemployment_46 "
    sql += ", unemployment_47 "
    sql += ", unemployment_48 "
    sql += ") "
    sql += ", 'unemployment_rate', ROW( "
    sql += "unemployment_rate_0 "
    sql += ", unemployment_rate_1 "
    sql += ", unemployment_rate_2 "
    sql += ", unemployment_rate_3 "
    sql += ", unemployment_rate_4 "
    sql += ", unemployment_rate_5 "
    sql += ", unemployment_rate_6 "
    sql += ", unemployment_rate_7 "
    sql += ", unemployment_rate_8 "
    sql += ", unemployment_rate_9 "
    sql += ", unemployment_rate_10 "
    sql += ", unemployment_rate_11 "
    sql += ", unemployment_rate_12 "
    sql += ", unemployment_rate_13 "
    sql += ", unemployment_rate_14 "
    sql += ", unemployment_rate_15 "
    sql += ", unemployment_rate_16 "
    sql += ", unemployment_rate_17 "
    sql += ", unemployment_rate_18 "
    sql += ", unemployment_rate_19 "
    sql += ", unemployment_rate_20 "
    sql += ", unemployment_rate_21 "
    sql += ", unemployment_rate_22 "
    sql += ", unemployment_rate_23 "
    sql += ", unemployment_rate_24 "
    sql += ", unemployment_rate_25 "
    sql += ", unemployment_rate_26 "
    sql += ", unemployment_rate_27 "
    sql += ", unemployment_rate_28 "
    sql += ", unemployment_rate_29 "
    sql += ", unemployment_rate_30 "
    sql += ", unemployment_rate_31 "
    sql += ", unemployment_rate_32 "
    sql += ", unemployment_rate_33 "
    sql += ", unemployment_rate_34 "
    sql += ", unemployment_rate_35 "
    sql += ", unemployment_rate_36 "
    sql += ", unemployment_rate_37 "
    sql += ", unemployment_rate_38 "
    sql += ", unemployment_rate_39 "
    sql += ", unemployment_rate_40 "
    sql += ", unemployment_rate_41 "
    sql += ", unemployment_rate_42 "
    sql += ", unemployment_rate_43 "
    sql += ", unemployment_rate_44 "
    sql += ", unemployment_rate_45 "
    sql += ", unemployment_rate_46 "
    sql += ", unemployment_rate_47 "
    sql += ", unemployment_rate_48 "
    sql += ") "
    sql += ")  "
    sql += ") employment "                                                                           #160                                                                   
    sql += ", 'skills' as placeholder "                                                              #161
    sql += "FROM "
    sql += "{}.skills_incremental_02 si ".format(schema)
    sql += "LEFT JOIN {}.unemployment_msa_transpose_20221222 umt ".format(schema)
    sql += "ON si.msa_code = umt.msa_code "
    sql += "WHERE "
    sql += "si.dataset_id = '{}' ".format(dataset_id)

    # print(sql)
    return query(_host_, _user_, _password_, _db_, sql)
