from django.db import connection
from django.conf import settings
from .forecasts_01 import queryer, queryer2, incremental_forecast

def get_date_range(tempno):
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    cur = connection.cursor()
    cur.execute("select years, qtr from {}.s_date_range_20221222 where row_num = {} ".format(schema, tempno))
    a = cur.fetchall()
    # retval = {}
    # for i in a:
    #     retval[i[0]] = i[1]
    return a

def get_date_range_occ():
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    cur = connection.cursor()
    cur.execute("select distinct to_date(cast(years as varchar), 'YYYY-MM-DD') from {}.s_date_range_20221222 order by 1".format(schema))

    a = cur.fetchall()
    # retval = {}
    # for i in a:
    #     retval[i[0]] = i[1]
    return a

def get_area_fips():
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    cur = connection.cursor()
    cur.execute("select distinct area_id, area_title from {}.d_area_v2".format(schema))
    a = cur.fetchall()
    retval = {}
    for i in a:
        retval[i[0]] = i[1]
    return retval

def get_msa():
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'
    cur = connection.cursor()
    cur.execute("select distinct msa_code, msa_title from {}.s_dropdown_state_msa".format(schema))
    a = cur.fetchall()
    retval = {}
    for i in a:
        retval[i[0]] = i[1]
    return retval
    
def get_industry():
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    cur = connection.cursor()
    cur.execute("select distinct industry_id, industry_title from {}.d_industry_v2".format(schema))
    a = cur.fetchall()
    retval = {}
    for i in a:
        retval[i[0]] = i[1]
    return retval

def get_area_title(area_id):
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    cur = connection.cursor()
    cur.execute("select area_title from {}.d_area_v2 where area_id = {}".format(schema, area_id))
    a = cur.fetchone()
    return a

def get_msa_title(msa_id):
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'
    cur = connection.cursor()
    cur.execute("select msa_title from {}.s_dropdown_state_msa where msa_code = '{}'".format(schema, msa_id))
    a = cur.fetchone()
    return a

def get_industry_code(industry_id):
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    cur = connection.cursor()
    cur.execute("select industry_code from {}.d_industry_v2 where industry_id = {}".format(schema, industry_id))
    a = cur.fetchone()
    return a

def get_industry_clean_code(industry_id):
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    cur = connection.cursor()
    cur.execute("select naics from {}.d_industry_naics_clean_20221222 where industry_id = {}".format(schema, industry_id))
    a = cur.fetchone()
    return a

def get_industry_title(industry_id):
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    cur = connection.cursor()
    cur.execute("select industry_title from {}.d_industry_v2 where industry_id = {}".format(schema, industry_id))
    a = cur.fetchone()
    return a

def get_states():
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    cur = connection.cursor()
    cur.execute("select distinct state_id, state_name from {}.s_dropdown_state order by state_name".format(schema))
    a = cur.fetchall()
    retval = {}
    for i in a:
        retval[i[0]] = i[1]
    return retval

def get_area_from_state_from_db(state):
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    cur = connection.cursor()
    cur.execute("select area_id,area_title_clean from {}.s_dropdown_state where state_id={}".format(schema, state))
    a = cur.fetchall()
    retval = []
    for i in a:
        b = {}
        b['id'] = i[0]
        b['name'] = i[1]
        retval.append(b)
    return retval

def get_msa_from_state_from_db(state):
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    cur = connection.cursor()
    cur.execute("select msa_code, msa_title from {}.s_dropdown_state_msa where state_id={}".format(schema, state))
    a = cur.fetchall()
    retval = []
    for i in a:
        b = {}
        b['id'] = i[0]
        b['name'] = i[1]
        retval.append(b)
    return retval

def get_industry_from_area_from_db(area):
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    cur = connection.cursor()

    sql = "select div.industry_id, div.industry_title, sdi.is_forecastable_null_flag, sdi.is_cross_data_null_flag "
    sql += "from {}.s_dropdown_industry as sdi, {}.d_industry_v2 as div ".format(schema, schema)
    sql += "where sdi.industry_id = div.industry_id and area_id={}".format(area)

    cur.execute(sql)
    a = cur.fetchall()
    retval = []
    for i in a:
        b = {}
        b['id'] = i[0]
        b['name'] = i[1]
        b['forecastable'] = i[2]
        b['cross_ref'] = i[3]
        retval.append(b)
    return retval

def get_industry_from_msa_from_db(msa):
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    cur = connection.cursor()

    # sql = "select div.industry_id, div.industry_title, sdim.is_forecastable_flag, sdim.is_cross_data_null_flag "
    # sql += "from {}.s_dropdown_industry_msa as sdim, {}.d_industry_v2 as div ".format(schema, schema)
    # sql += "where sdim.industry_id = div.industry_id and msa_code={}".format(msa)

    sql = "select "
    sql += "    div.industry_id "
    sql += "    , div.industry_title "
    sql += "    , sdim.is_forecastable_flag "
    sql += "    , sdim.is_cross_data_null_flag "
    sql += "    , case when diom.industry_id is not null then 1 else 0 end as occupation_flag "
    sql += "from "
    sql += "    {}.s_dropdown_industry_msa_20221222 as sdim ".format(schema)
    sql += "    left join {}.d_industry_v2 as div ".format(schema)
    sql += "        on sdim.industry_id = div.industry_id "
    sql += "    left join (select distinct msa_code, industry_id from {}.s_dropdown_industry_occupation_msa_20221222) as diom ".format(schema)
    sql += "        on sdim.msa_code::int = diom.msa_code::int "
    sql += "        and sdim.industry_id::int = diom.industry_id::int "
    sql += "where "
    sql += "    sdim.msa_code={} ".format(msa)
    sql += "; "


    cur.execute(sql)
    a = cur.fetchall()
    retval = []
    for i in a:
        b = {}
        b['id'] = i[0]
        b['name'] = i[1]
        b['forecastable'] = i[2]
        b['cross_ref'] = i[3]
        b['occupation'] = i[4]
        retval.append(b)
    return retval

def get_occupation_from_msa_from_db(msa, industry):
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    cur = connection.cursor()

    sql = "select occ_code, occ_title "
    sql += "from {}.s_dropdown_industry_occupation_msa_20221222 ".format(schema)
    sql += "where msa_code = '{}' and industry_id = '{}';".format(msa, industry)

    # print(sql)

    cur.execute(sql)
    a = cur.fetchall()
    retval = []
    for i in a:
        b = {}
        b['id'] = i[0]
        b['name'] = i[1]
        # b['forecastable'] = i[2]
        # b['cross_ref'] = i[3]
        retval.append(b)
    return retval

def get_wage_objs_v4(area, industry):
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    cur = connection.cursor()
    sql = "select w.latest_year, w.latest_qtr, w.latest_avg_wkly_wage, " # 0, 1, 2
    
    # 1 year
    sql += "json_data -> 'data_annually' ->> 'f1' AS t0_a, " # 3
    sql += "json_data -> 'data_annually' ->> 'f2' AS t1_a, " # 4
    sql += "json_data -> 'data_annually' ->> 'f3' AS t2_a, " # 5
    sql += "json_data -> 'data_annually' ->> 'f4' AS t3_a, " # 6
    
    # 2 year
    sql += "json_data -> 'data_annually' ->> 'f5' AS t4_a, " # 7
    sql += "json_data -> 'data_annually' ->> 'f6' AS t5_a, " # 8
    sql += "json_data -> 'data_annually' ->> 'f7' AS t6_a, " # 9
    sql += "json_data -> 'data_annually' ->> 'f8' AS t7_a, " # 10
    
    # 3 year
    sql += "json_data -> 'data_annually' ->> 'f9' AS t8_a, " # 11
    sql += "json_data -> 'data_annually' ->> 'f10' AS t9_a, " # 12
    sql += "json_data -> 'data_annually' ->> 'f11' AS t10_a, " # 13
    sql += "json_data -> 'data_annually' ->> 'f12' AS t11_a, " # 14
    
    # 4 year
    sql += "json_data -> 'data_annually' ->> 'f13' AS t12_a, " # 15
    sql += "json_data -> 'data_annually' ->> 'f14' AS t13_a, " # 16
    sql += "json_data -> 'data_annually' ->> 'f15' AS t14_a, " # 17
    sql += "json_data -> 'data_annually' ->> 'f16' AS t15_a, " # 18

    # 5 year
    sql += "json_data -> 'data_annually' ->> 'f17' AS t17_a, " # 19
    sql += "json_data -> 'data_annually' ->> 'f18' AS t18_a, " # 20
    sql += "json_data -> 'data_annually' ->> 'f19' AS t19_a, " # 21
    sql += "json_data -> 'data_annually' ->> 'f20' AS t20_a, " # 22
    
    # 6 year
    sql += "json_data -> 'data_annually' ->> 'f21' AS t21_a, " # 23
    sql += "json_data -> 'data_annually' ->> 'f22' AS t22_a, " # 24
    sql += "json_data -> 'data_annually' ->> 'f23' AS t23_a, " # 25
    sql += "json_data -> 'data_annually' ->> 'f24' AS t24_a, " # 26

    # 7 year
    sql += "json_data -> 'data_annually' ->> 'f25' AS t25_a, " # 27
    sql += "json_data -> 'data_annually' ->> 'f26' AS t26_a, " # 28
    sql += "json_data -> 'data_annually' ->> 'f27' AS t27_a, " # 29
    sql += "json_data -> 'data_annually' ->> 'f28' AS t28_a, " # 30

    # 8 year
    sql += "json_data -> 'data_annually' ->> 'f29' AS t29_a, " # 31
    sql += "json_data -> 'data_annually' ->> 'f30' AS t30_a, " # 32
    sql += "json_data -> 'data_annually' ->> 'f31' AS t31_a, " # 33
    sql += "json_data -> 'data_annually' ->> 'f32' AS t32_a, " # 34
    
    # 9 year
    sql += "json_data -> 'data_annually' ->> 'f33' AS t33_a, " # 35
    sql += "json_data -> 'data_annually' ->> 'f34' AS t34_a, " # 36
    sql += "json_data -> 'data_annually' ->> 'f35' AS t35_a, " # 37
    sql += "json_data -> 'data_annually' ->> 'f36' AS t36_a, " # 38
    
    # 10 year
    sql += "json_data -> 'data_annually' ->> 'f37' AS t37_a, " # 39
    sql += "json_data -> 'data_annually' ->> 'f38' AS t38_a, " # 40
    sql += "json_data -> 'data_annually' ->> 'f39' AS t39_a, " # 41
    sql += "json_data -> 'data_annually' ->> 'f40' AS t40_a, " # 42

    # Forecast 1 year
    sql += "CAST(predictions -> 'predictions' ->> '0' AS BIGINT) AS tm1_a, " # 43
    sql += "CAST(predictions -> 'predictions' ->> '1' AS BIGINT) AS tm2_a, " # 44
    sql += "CAST(predictions -> 'predictions' ->> '2' AS BIGINT) AS tm3_a, " # 45
    sql += "CAST(predictions -> 'predictions' ->> '3' AS BIGINT) AS tm4_a, " # 46

    # Forecast 2 year
    sql += "CAST(predictions -> 'predictions' ->> '4' AS BIGINT) AS tm5_a, " # 47
    sql += "CAST(predictions -> 'predictions' ->> '5' AS BIGINT) AS tm6_a, " # 48
    sql += "CAST(predictions -> 'predictions' ->> '6' AS BIGINT) AS tm7_a, " # 49
    sql += "CAST(predictions -> 'predictions' ->> '7' AS BIGINT) AS tm8_a, " # 50



    # 1 year
    sql += "json_data -> 'data_hourly' ->> 'f1' AS t0_h, " # 51
    sql += "json_data -> 'data_hourly' ->> 'f2' AS t1_h, " # 52
    sql += "json_data -> 'data_hourly' ->> 'f3' AS t2_h, " # 53
    sql += "json_data -> 'data_hourly' ->> 'f4' AS t3_h, " # 54

    # 2 year
    sql += "json_data -> 'data_hourly' ->> 'f5' AS t4_h, " # 55
    sql += "json_data -> 'data_hourly' ->> 'f6' AS t5_h, " # 56
    sql += "json_data -> 'data_hourly' ->> 'f7' AS t6_h, " # 57
    sql += "json_data -> 'data_hourly' ->> 'f8' AS t7_h, " # 58

    # 3 year
    sql += "json_data -> 'data_hourly' ->> 'f9' AS t8_h, " # 59
    sql += "json_data -> 'data_hourly' ->> 'f10' AS t9_h, " # 60
    sql += "json_data -> 'data_hourly' ->> 'f11' AS t10_h, " # 61
    sql += "json_data -> 'data_hourly' ->> 'f12' AS t11_h, " # 62

    # 4 year    
    sql += "json_data -> 'data_hourly' ->> 'f13' AS t12_h, " # 63
    sql += "json_data -> 'data_hourly' ->> 'f14' AS t13_h, " # 64
    sql += "json_data -> 'data_hourly' ->> 'f15' AS t14_h, " # 65
    sql += "json_data -> 'data_hourly' ->> 'f16' AS t15_h, " # 66
    
    # 5 year    
    sql += "json_data -> 'data_hourly' ->> 'f17' AS t17_h, " # 67
    sql += "json_data -> 'data_hourly' ->> 'f18' AS t18_h, " # 68
    sql += "json_data -> 'data_hourly' ->> 'f19' AS t19_h, " # 69
    sql += "json_data -> 'data_hourly' ->> 'f20' AS t20_h, " # 70

    # 6 year    
    sql += "json_data -> 'data_hourly' ->> 'f21' AS t21_h, " # 71
    sql += "json_data -> 'data_hourly' ->> 'f22' AS t22_h, " # 72
    sql += "json_data -> 'data_hourly' ->> 'f23' AS t23_h, " # 73
    sql += "json_data -> 'data_hourly' ->> 'f24' AS t24_h, " # 74

    # 7 year    
    sql += "json_data -> 'data_hourly' ->> 'f25' AS t25_h, " # 75
    sql += "json_data -> 'data_hourly' ->> 'f26' AS t26_h, " # 76
    sql += "json_data -> 'data_hourly' ->> 'f27' AS t27_h, " # 77
    sql += "json_data -> 'data_hourly' ->> 'f28' AS t28_h, " # 78

    # 8 year    
    sql += "json_data -> 'data_hourly' ->> 'f29' AS t29_h, " # 79
    sql += "json_data -> 'data_hourly' ->> 'f30' AS t30_h, " # 80
    sql += "json_data -> 'data_hourly' ->> 'f31' AS t31_h, " # 81
    sql += "json_data -> 'data_hourly' ->> 'f32' AS t32_h, " # 82

    # 9 year    
    sql += "json_data -> 'data_hourly' ->> 'f33' AS t33_h, " # 83
    sql += "json_data -> 'data_hourly' ->> 'f34' AS t34_h, " # 84
    sql += "json_data -> 'data_hourly' ->> 'f35' AS t35_h, " # 85
    sql += "json_data -> 'data_hourly' ->> 'f36' AS t36_h, " # 86
    
    # 10 year    
    sql += "json_data -> 'data_hourly' ->> 'f37' AS t37_h, " # 87
    sql += "json_data -> 'data_hourly' ->> 'f38' AS t38_h, " # 88
    sql += "json_data -> 'data_hourly' ->> 'f39' AS t39_h, " # 89
    sql += "json_data -> 'data_hourly' ->> 'f40' AS t40_h, " # 90

    # Forecast 1 year
    sql += "CAST(predictions -> 'predictions' ->> '0' AS BIGINT) / 2079.99999 AS tm1_h, " # 91
    sql += "CAST(predictions -> 'predictions' ->> '1' AS BIGINT) / 2079.99999 AS tm2_h, " # 92
    sql += "CAST(predictions -> 'predictions' ->> '2' AS BIGINT) / 2079.99999 AS tm3_h, " # 93
    sql += "CAST(predictions -> 'predictions' ->> '3' AS BIGINT) / 2079.99999 AS tm4_h, " # 94

    # Forecast 2 year
    sql += "CAST(predictions -> 'predictions' ->> '4' AS BIGINT) / 2079.99999 AS tm5_h, " # 95
    sql += "CAST(predictions -> 'predictions' ->> '5' AS BIGINT) / 2079.99999 AS tm6_h, " # 96
    sql += "CAST(predictions -> 'predictions' ->> '6' AS BIGINT) / 2079.99999 AS tm7_h, " # 97
    sql += "CAST(predictions -> 'predictions' ->> '7' AS BIGINT) / 2079.99999 AS tm8_h, " # 98

    sql += "json_data_cross, " # 99

    sql += "json_data -> 'data_inferred' AS inferred, " # 100

    sql += "CASE WHEN predictions IS NULL THEN 0 ELSE 1 END AS is_forecastable_null_flag, " # 101
    sql += "is_cross_data_null_flag, " # 102

    sql += "unemployment -> 'employment' AS employment " # 103

    sql += "from {}.f_wkly_wage_20221222 w ".format(schema)
    # sql += "from {}.f_wkly_wage_20220713 w ".format(schema)
    # sql += "from {}.f_wkly_wage_20220602 w ".format(schema)
    sql += "where w.area_id::INT='{}' and w.industry_id::INT='{}' ".format(area, industry)
    cur.execute(sql)
    a = cur.fetchone()
    try:
        retval = list(a)
    except Exception as e:
        retval = []
        print(e)
    return retval

def get_msa_wage_objs_v5(msa, industry):
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    cur = connection.cursor()
    sql = "select w.latest_year, w.latest_qtr, w.latest_avg_wkly_wage, " # 0, 1, 2
    
    # 1 year
    sql += "json_data -> 'data_annually' ->> 'f1' AS t0_a, " # 3
    sql += "json_data -> 'data_annually' ->> 'f2' AS t1_a, " # 4
    sql += "json_data -> 'data_annually' ->> 'f3' AS t2_a, " # 5
    sql += "json_data -> 'data_annually' ->> 'f4' AS t3_a, " # 6
    
    # 2 year
    sql += "json_data -> 'data_annually' ->> 'f5' AS t4_a, " # 7
    sql += "json_data -> 'data_annually' ->> 'f6' AS t5_a, " # 8
    sql += "json_data -> 'data_annually' ->> 'f7' AS t6_a, " # 9
    sql += "json_data -> 'data_annually' ->> 'f8' AS t7_a, " # 10
    
    # 3 year
    sql += "json_data -> 'data_annually' ->> 'f9' AS t8_a, " # 11
    sql += "json_data -> 'data_annually' ->> 'f10' AS t9_a, " # 12
    sql += "json_data -> 'data_annually' ->> 'f11' AS t10_a, " # 13
    sql += "json_data -> 'data_annually' ->> 'f12' AS t11_a, " # 14
    
    # 4 year
    sql += "json_data -> 'data_annually' ->> 'f13' AS t12_a, " # 15
    sql += "json_data -> 'data_annually' ->> 'f14' AS t13_a, " # 16
    sql += "json_data -> 'data_annually' ->> 'f15' AS t14_a, " # 17
    sql += "json_data -> 'data_annually' ->> 'f16' AS t15_a, " # 18

    # 5 year
    sql += "json_data -> 'data_annually' ->> 'f17' AS t17_a, " # 19
    sql += "json_data -> 'data_annually' ->> 'f18' AS t18_a, " # 20
    sql += "json_data -> 'data_annually' ->> 'f19' AS t19_a, " # 21
    sql += "json_data -> 'data_annually' ->> 'f20' AS t20_a, " # 22
    
    # 6 year
    sql += "json_data -> 'data_annually' ->> 'f21' AS t21_a, " # 23
    sql += "json_data -> 'data_annually' ->> 'f22' AS t22_a, " # 24
    sql += "json_data -> 'data_annually' ->> 'f23' AS t23_a, " # 25
    sql += "json_data -> 'data_annually' ->> 'f24' AS t24_a, " # 26

    # 7 year
    sql += "json_data -> 'data_annually' ->> 'f25' AS t25_a, " # 27
    sql += "json_data -> 'data_annually' ->> 'f26' AS t26_a, " # 28
    sql += "json_data -> 'data_annually' ->> 'f27' AS t27_a, " # 29
    sql += "json_data -> 'data_annually' ->> 'f28' AS t28_a, " # 30

    # 8 year
    sql += "json_data -> 'data_annually' ->> 'f29' AS t29_a, " # 31
    sql += "json_data -> 'data_annually' ->> 'f30' AS t30_a, " # 32
    sql += "json_data -> 'data_annually' ->> 'f31' AS t31_a, " # 33
    sql += "json_data -> 'data_annually' ->> 'f32' AS t32_a, " # 34
    
    # 9 year
    sql += "json_data -> 'data_annually' ->> 'f33' AS t33_a, " # 35
    sql += "json_data -> 'data_annually' ->> 'f34' AS t34_a, " # 36
    sql += "json_data -> 'data_annually' ->> 'f35' AS t35_a, " # 37
    sql += "json_data -> 'data_annually' ->> 'f36' AS t36_a, " # 38
    
    # 10 year
    sql += "json_data -> 'data_annually' ->> 'f37' AS t37_a, " # 39
    sql += "json_data -> 'data_annually' ->> 'f38' AS t38_a, " # 40
    sql += "json_data -> 'data_annually' ->> 'f39' AS t39_a, " # 41
    sql += "json_data -> 'data_annually' ->> 'f40' AS t40_a, " # 42

    # Forecast 1 year
    sql += "CAST(predictions -> 'predictions' ->> 'f1' AS BIGINT) AS tm1_a, " # 43
    sql += "CAST(predictions -> 'predictions' ->> 'f2' AS BIGINT) AS tm2_a, " # 44
    sql += "CAST(predictions -> 'predictions' ->> 'f3' AS BIGINT) AS tm3_a, " # 45
    sql += "CAST(predictions -> 'predictions' ->> 'f4' AS BIGINT) AS tm4_a, " # 46

    # Forecast 2 year
    sql += "CAST(predictions -> 'predictions' ->> 'f5' AS BIGINT) AS tm5_a, " # 47
    sql += "CAST(predictions -> 'predictions' ->> 'f6' AS BIGINT) AS tm6_a, " # 48
    sql += "CAST(predictions -> 'predictions' ->> 'f7' AS BIGINT) AS tm7_a, " # 49
    sql += "CAST(predictions -> 'predictions' ->> 'f8' AS BIGINT) AS tm8_a, " # 50



    # 1 year
    sql += "json_data -> 'data_hourly' ->> 'f1' AS t0_h, " # 51
    sql += "json_data -> 'data_hourly' ->> 'f2' AS t1_h, " # 52
    sql += "json_data -> 'data_hourly' ->> 'f3' AS t2_h, " # 53
    sql += "json_data -> 'data_hourly' ->> 'f4' AS t3_h, " # 54

    # 2 year
    sql += "json_data -> 'data_hourly' ->> 'f5' AS t4_h, " # 55
    sql += "json_data -> 'data_hourly' ->> 'f6' AS t5_h, " # 56
    sql += "json_data -> 'data_hourly' ->> 'f7' AS t6_h, " # 57
    sql += "json_data -> 'data_hourly' ->> 'f8' AS t7_h, " # 58

    # 3 year
    sql += "json_data -> 'data_hourly' ->> 'f9' AS t8_h, " # 59
    sql += "json_data -> 'data_hourly' ->> 'f10' AS t9_h, " # 60
    sql += "json_data -> 'data_hourly' ->> 'f11' AS t10_h, " # 61
    sql += "json_data -> 'data_hourly' ->> 'f12' AS t11_h, " # 62

    # 4 year    
    sql += "json_data -> 'data_hourly' ->> 'f13' AS t12_h, " # 63
    sql += "json_data -> 'data_hourly' ->> 'f14' AS t13_h, " # 64
    sql += "json_data -> 'data_hourly' ->> 'f15' AS t14_h, " # 65
    sql += "json_data -> 'data_hourly' ->> 'f16' AS t15_h, " # 66
    
    # 5 year    
    sql += "json_data -> 'data_hourly' ->> 'f17' AS t17_h, " # 67
    sql += "json_data -> 'data_hourly' ->> 'f18' AS t18_h, " # 68
    sql += "json_data -> 'data_hourly' ->> 'f19' AS t19_h, " # 69
    sql += "json_data -> 'data_hourly' ->> 'f20' AS t20_h, " # 70

    # 6 year    
    sql += "json_data -> 'data_hourly' ->> 'f21' AS t21_h, " # 71
    sql += "json_data -> 'data_hourly' ->> 'f22' AS t22_h, " # 72
    sql += "json_data -> 'data_hourly' ->> 'f23' AS t23_h, " # 73
    sql += "json_data -> 'data_hourly' ->> 'f24' AS t24_h, " # 74

    # 7 year    
    sql += "json_data -> 'data_hourly' ->> 'f25' AS t25_h, " # 75
    sql += "json_data -> 'data_hourly' ->> 'f26' AS t26_h, " # 76
    sql += "json_data -> 'data_hourly' ->> 'f27' AS t27_h, " # 77
    sql += "json_data -> 'data_hourly' ->> 'f28' AS t28_h, " # 78

    # 8 year    
    sql += "json_data -> 'data_hourly' ->> 'f29' AS t29_h, " # 79
    sql += "json_data -> 'data_hourly' ->> 'f30' AS t30_h, " # 80
    sql += "json_data -> 'data_hourly' ->> 'f31' AS t31_h, " # 81
    sql += "json_data -> 'data_hourly' ->> 'f32' AS t32_h, " # 82

    # 9 year    
    sql += "json_data -> 'data_hourly' ->> 'f33' AS t33_h, " # 83
    sql += "json_data -> 'data_hourly' ->> 'f34' AS t34_h, " # 84
    sql += "json_data -> 'data_hourly' ->> 'f35' AS t35_h, " # 85
    sql += "json_data -> 'data_hourly' ->> 'f36' AS t36_h, " # 86
    
    # 10 year    
    sql += "json_data -> 'data_hourly' ->> 'f37' AS t37_h, " # 87
    sql += "json_data -> 'data_hourly' ->> 'f38' AS t38_h, " # 88
    sql += "json_data -> 'data_hourly' ->> 'f39' AS t39_h, " # 89
    sql += "json_data -> 'data_hourly' ->> 'f40' AS t40_h, " # 90

    # Forecast 1 year
    sql += "CAST(predictions -> 'predictions' ->> 'f1' AS BIGINT) / 2079.99999 AS tm1_h, " # 91
    sql += "CAST(predictions -> 'predictions' ->> 'f2' AS BIGINT) / 2079.99999 AS tm2_h, " # 92
    sql += "CAST(predictions -> 'predictions' ->> 'f3' AS BIGINT) / 2079.99999 AS tm3_h, " # 93
    sql += "CAST(predictions -> 'predictions' ->> 'f4' AS BIGINT) / 2079.99999 AS tm4_h, " # 94

    # Forecast 2 year
    sql += "CAST(predictions -> 'predictions' ->> 'f5' AS BIGINT) / 2079.99999 AS tm5_h, " # 95
    sql += "CAST(predictions -> 'predictions' ->> 'f6' AS BIGINT) / 2079.99999 AS tm6_h, " # 96
    sql += "CAST(predictions -> 'predictions' ->> 'f7' AS BIGINT) / 2079.99999 AS tm7_h, " # 97
    sql += "CAST(predictions -> 'predictions' ->> 'f8' AS BIGINT) / 2079.99999 AS tm8_h, " # 98

    sql += "json_data_cross, " # 99

    sql += "json_data -> 'data_inferred' AS inferred, " # 100

    sql += "is_forecastable_flag, " # 101
    sql += "is_cross_data_null_flag, " # 102

    sql += "unemployment -> 'employment' AS employment " # 103

    sql += "from {}.f_wkly_wage_msa_20221222 w ".format(schema)
    # sql += "from {}.f_wkly_wage_msa_20220713 w ".format(schema)
    # sql += "from {}.f_wkly_wage_msa_20220602 w ".format(schema)
    sql += "where w.msa_code::INT='{}' and w.industry_id::INT='{}' ".format(msa, industry)

    # sql = "select * from {}.f_wkly_wage_v11_msa ".format(schema)
    # sql = "select * from {}.f_wkly_wage_msa_20220602 ".format(schema)
    # sql += "where msa_code='{}' and industry_id='{}' ".format(msa, industry)
    cur.execute(sql)
    a = cur.fetchone()
    try:
        retval = list(a)
    except Exception as e:
        retval = []
        print(e)
    return retval

def get_oews_obj_v1(msa_code, naics_code, occ_code):
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    cur = connection.cursor()
    sql = "select "
    sql += "nop.us_occ_naics "                                                                      # 0
    sql += ", nop.naics "                                                                           # 1
    sql += ", nop.occ_code "                                                                        # 2
    sql += ", nop.msa_code "                                                                        # 3

    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '0' AS NUMERIC), 0)::INT AS a_pct10_0 "       # 4
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '1' AS NUMERIC), 0)::INT AS a_pct10_1 "       # 5
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '2' AS NUMERIC), 0)::INT AS a_pct10_2 "       # 6
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '3' AS NUMERIC), 0)::INT AS a_pct10_3 "       # 7
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '4' AS NUMERIC), 0)::INT AS a_pct10_4 "       # 8
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '5' AS NUMERIC), 0)::INT AS a_pct10_5 "       # 9
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '6' AS NUMERIC), 0)::INT AS a_pct10_6 "       # 10
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '7' AS NUMERIC), 0)::INT AS a_pct10_7 "       # 11
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '8' AS NUMERIC), 0)::INT AS a_pct10_8 "       # 12
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '9' AS NUMERIC), 0)::INT AS a_pct10_9 "       # 13
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '10' AS NUMERIC), 0)::INT AS a_pct10_10 "     # 14
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '11' AS NUMERIC), 0)::INT AS a_pct10_11 "     # 15
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '12' AS NUMERIC), 0)::INT AS a_pct10_12 "     # 16

    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '0' AS NUMERIC), 0)::INT AS a_pct25_0 "       # 17
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '1' AS NUMERIC), 0)::INT AS a_pct25_1 "       #18
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '2' AS NUMERIC), 0)::INT AS a_pct25_2 "       #19
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '3' AS NUMERIC), 0)::INT AS a_pct25_3 "       #20
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '4' AS NUMERIC), 0)::INT AS a_pct25_4 "       #21
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '5' AS NUMERIC), 0)::INT AS a_pct25_5 "       #22
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '6' AS NUMERIC), 0)::INT AS a_pct25_6 "       #23
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '7' AS NUMERIC), 0)::INT AS a_pct25_7 "       #24
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '8' AS NUMERIC), 0)::INT AS a_pct25_8 "       #25
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '9' AS NUMERIC), 0)::INT AS a_pct25_9 "       #26
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '10' AS NUMERIC), 0)::INT AS a_pct25_10 "     #27
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '11' AS NUMERIC), 0)::INT AS a_pct25_11 "     #28
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '12' AS NUMERIC), 0)::INT AS a_pct25_12 "     #29

    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '0' AS NUMERIC), 0)::INT AS a_median_0 "     #30
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '1' AS NUMERIC), 0)::INT AS a_median_1 "     #31
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '2' AS NUMERIC), 0)::INT AS a_median_2 "     #32
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '3' AS NUMERIC), 0)::INT AS a_median_3 "     #33
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '4' AS NUMERIC), 0)::INT AS a_median_4 "     #34
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '5' AS NUMERIC), 0)::INT AS a_median_5 "     #35
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '6' AS NUMERIC), 0)::INT AS a_median_6 "     #36
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '7' AS NUMERIC), 0)::INT AS a_median_7 "     #37
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '8' AS NUMERIC), 0)::INT AS a_median_8 "     #38
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '9' AS NUMERIC), 0)::INT AS a_median_9 "     #39
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '10' AS NUMERIC), 0)::INT AS a_median_10 "   #40
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '11' AS NUMERIC), 0)::INT AS a_median_11 "   #41
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '12' AS NUMERIC), 0)::INT AS a_median_12 "   #42

    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '0' AS NUMERIC), 0)::INT AS a_pct75_0 "       #43
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '1' AS NUMERIC), 0)::INT AS a_pct75_1 "       #44
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '2' AS NUMERIC), 0)::INT AS a_pct75_2 "       #45
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '3' AS NUMERIC), 0)::INT AS a_pct75_3 "       #46
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '4' AS NUMERIC), 0)::INT AS a_pct75_4 "       #47
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '5' AS NUMERIC), 0)::INT AS a_pct75_5 "       #48
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '6' AS NUMERIC), 0)::INT AS a_pct75_6 "       #49
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '7' AS NUMERIC), 0)::INT AS a_pct75_7 "       #50
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '8' AS NUMERIC), 0)::INT AS a_pct75_8 "       #51
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '9' AS NUMERIC), 0)::INT AS a_pct75_9 "       #52
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '10' AS NUMERIC), 0)::INT AS a_pct75_10 "     #53
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '11' AS NUMERIC), 0)::INT AS a_pct75_11 "     #54
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '12' AS NUMERIC), 0)::INT AS a_pct75_12 "     #55

    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '0' AS NUMERIC), 0)::INT AS a_pct90_0 "       #56
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '1' AS NUMERIC), 0)::INT AS a_pct90_1 "       #57
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '2' AS NUMERIC), 0)::INT AS a_pct90_2 "       #58
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '3' AS NUMERIC), 0)::INT AS a_pct90_3 "       #59
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '4' AS NUMERIC), 0)::INT AS a_pct90_4 "       #60
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '5' AS NUMERIC), 0)::INT AS a_pct90_5 "       #61
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '6' AS NUMERIC), 0)::INT AS a_pct90_6 "       #62
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '7' AS NUMERIC), 0)::INT AS a_pct90_7 "       #63
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '8' AS NUMERIC), 0)::INT AS a_pct90_8 "       #64
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '9' AS NUMERIC), 0)::INT AS a_pct90_9 "       #65
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '10' AS NUMERIC), 0)::INT AS a_pct90_10 "     #66
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '11' AS NUMERIC), 0)::INT AS a_pct90_11 "     #67
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '12' AS NUMERIC), 0)::INT AS a_pct90_12 "     #68

    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '0' AS NUMERIC), 0)::INT AS a_mean_0 "         #69
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '1' AS NUMERIC), 0)::INT AS a_mean_1 "         #70
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '2' AS NUMERIC), 0)::INT AS a_mean_2 "         #71
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '3' AS NUMERIC), 0)::INT AS a_mean_3 "         #72
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '4' AS NUMERIC), 0)::INT AS a_mean_4 "         #73
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '5' AS NUMERIC), 0)::INT AS a_mean_5 "         #74
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '6' AS NUMERIC), 0)::INT AS a_mean_6 "         #75
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '7' AS NUMERIC), 0)::INT AS a_mean_7 "         #76
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '8' AS NUMERIC), 0)::INT AS a_mean_8 "         #77
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '9' AS NUMERIC), 0)::INT AS a_mean_9 "         #78
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '10' AS NUMERIC), 0)::INT AS a_mean_10 "       #79
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '11' AS NUMERIC), 0)::INT AS a_mean_11 "       #80
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '12' AS NUMERIC), 0)::INT AS a_mean_12 "       #81

    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '0' AS NUMERIC) / 2080, 2) AS h_pct10_0 "     #82
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '1' AS NUMERIC) / 2080, 2) AS h_pct10_1 "     #83
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '2' AS NUMERIC) / 2080, 2) AS h_pct10_2 "     #84
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '3' AS NUMERIC) / 2080, 2) AS h_pct10_3 "     #85
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '4' AS NUMERIC) / 2080, 2) AS h_pct10_4 "     #86
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '5' AS NUMERIC) / 2080, 2) AS h_pct10_5 "     #87
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '6' AS NUMERIC) / 2080, 2) AS h_pct10_6 "     #88
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '7' AS NUMERIC) / 2080, 2) AS h_pct10_7 "     #89
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '8' AS NUMERIC) / 2080, 2) AS h_pct10_8 "     #90
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '9' AS NUMERIC) / 2080, 2) AS h_pct10_9 "     #91
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '10' AS NUMERIC) / 2080, 2) AS h_pct10_10 "   #92
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '11' AS NUMERIC) / 2080, 2) AS h_pct10_11 "   #93
    sql += ", ROUND(CAST(predictions -> 'a_pct10' ->> '12' AS NUMERIC) / 2080, 2) AS h_pct10_12 "   #94

    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '0' AS NUMERIC) / 2080, 2) AS h_pct25_0 "     #95
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '1' AS NUMERIC) / 2080, 2) AS h_pct25_1 "     #96
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '2' AS NUMERIC) / 2080, 2) AS h_pct25_2 "     #97
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '3' AS NUMERIC) / 2080, 2) AS h_pct25_3 "     #98
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '4' AS NUMERIC) / 2080, 2) AS h_pct25_4 "     #99
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '5' AS NUMERIC) / 2080, 2) AS h_pct25_5 "     #100
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '6' AS NUMERIC) / 2080, 2) AS h_pct25_6 "     #101
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '7' AS NUMERIC) / 2080, 2) AS h_pct25_7 "     #102
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '8' AS NUMERIC) / 2080, 2) AS h_pct25_8 "     #103
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '9' AS NUMERIC) / 2080, 2) AS h_pct25_9 "     #104
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '10' AS NUMERIC) / 2080, 2) AS h_pct25_10 "   #105
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '11' AS NUMERIC) / 2080, 2) AS h_pct25_11 "   #106
    sql += ", ROUND(CAST(predictions -> 'a_pct25' ->> '12' AS NUMERIC) / 2080, 2) AS h_pct25_12 "   #107

    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '0' AS NUMERIC) / 2080, 2) AS h_median_0 "   #108
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '1' AS NUMERIC) / 2080, 2) AS h_median_1 "   #109
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '2' AS NUMERIC) / 2080, 2) AS h_median_2 "   #110
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '3' AS NUMERIC) / 2080, 2) AS h_median_3 "   #111
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '4' AS NUMERIC) / 2080, 2) AS h_median_4 "   #112
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '5' AS NUMERIC) / 2080, 2) AS h_median_5 "   #113
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '6' AS NUMERIC) / 2080, 2) AS h_median_6 "   #114
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '7' AS NUMERIC) / 2080, 2) AS h_median_7 "   #115
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '8' AS NUMERIC) / 2080, 2) AS h_median_8 "   #116
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '9' AS NUMERIC) / 2080, 2) AS h_median_9 "   #117
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '10' AS NUMERIC) / 2080, 2) AS h_median_10 " #118
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '11' AS NUMERIC) / 2080, 2) AS h_median_11 " #119
    sql += ", ROUND(CAST(predictions -> 'a_median' ->> '12' AS NUMERIC) / 2080, 2) AS h_median_12 " #120

    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '0' AS NUMERIC) / 2080, 2) AS h_pct75_0 "     #121
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '1' AS NUMERIC) / 2080, 2) AS h_pct75_1 "     #122
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '2' AS NUMERIC) / 2080, 2) AS h_pct75_2 "     #123
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '3' AS NUMERIC) / 2080, 2) AS h_pct75_3 "     #124
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '4' AS NUMERIC) / 2080, 2) AS h_pct75_4 "     #125
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '5' AS NUMERIC) / 2080, 2) AS h_pct75_5 "     #126
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '6' AS NUMERIC) / 2080, 2) AS h_pct75_6 "     #127
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '7' AS NUMERIC) / 2080, 2) AS h_pct75_7 "     #128
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '8' AS NUMERIC) / 2080, 2) AS h_pct75_8 "     #129
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '9' AS NUMERIC) / 2080, 2) AS h_pct75_9 "     #130
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '10' AS NUMERIC) / 2080, 2) AS h_pct75_10 "   #131
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '11' AS NUMERIC) / 2080, 2) AS h_pct75_11 "   #132
    sql += ", ROUND(CAST(predictions -> 'a_pct75' ->> '12' AS NUMERIC) / 2080, 2) AS h_pct75_12 "   #133

    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '0' AS NUMERIC) / 2080, 2) AS h_pct90_0 "     #134
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '1' AS NUMERIC) / 2080, 2) AS h_pct90_1 "     #135
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '2' AS NUMERIC) / 2080, 2) AS h_pct90_2 "     #136
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '3' AS NUMERIC) / 2080, 2) AS h_pct90_3 "     #137
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '4' AS NUMERIC) / 2080, 2) AS h_pct90_4 "     #138
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '5' AS NUMERIC) / 2080, 2) AS h_pct90_5 "     #139
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '6' AS NUMERIC) / 2080, 2) AS h_pct90_6 "     #140
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '7' AS NUMERIC) / 2080, 2) AS h_pct90_7 "     #141
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '8' AS NUMERIC) / 2080, 2) AS h_pct90_8 "     #142
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '9' AS NUMERIC) / 2080, 2) AS h_pct90_9 "     #143
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '10' AS NUMERIC) / 2080, 2) AS h_pct90_10 "   #144
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '11' AS NUMERIC) / 2080, 2) AS h_pct90_11 "   #145
    sql += ", ROUND(CAST(predictions -> 'a_pct90' ->> '12' AS NUMERIC) / 2080, 2) AS h_pct90_12 "   #146

    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '0' AS NUMERIC) / 2080, 2) AS h_mean_0 "       #147
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '1' AS NUMERIC) / 2080, 2) AS h_mean_1 "       #148
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '2' AS NUMERIC) / 2080, 2) AS h_mean_2 "       #149
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '3' AS NUMERIC) / 2080, 2) AS h_mean_3 "       #150
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '4' AS NUMERIC) / 2080, 2) AS h_mean_4 "       #151
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '5' AS NUMERIC) / 2080, 2) AS h_mean_5 "       #152
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '6' AS NUMERIC) / 2080, 2) AS h_mean_6 "       #153
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '7' AS NUMERIC) / 2080, 2) AS h_mean_7 "       #154
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '8' AS NUMERIC) / 2080, 2) AS h_mean_8 "       #155
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '9' AS NUMERIC) / 2080, 2) AS h_mean_9 "       #156
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '10' AS NUMERIC) / 2080, 2) AS h_mean_10 "     #157
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '11' AS NUMERIC) / 2080, 2) AS h_mean_11 "     #158
    sql += ", ROUND(CAST(predictions -> 'a_mean' ->> '12' AS NUMERIC) / 2080, 2) AS h_mean_12 "     #159

    sql += ", CASE WHEN "
    sql += "(ROUND(CAST(predictions -> 'a_pct10' ->> '11' AS NUMERIC), 0)::INT IS NOT NULL "
    sql += "AND ROUND(CAST(predictions -> 'a_pct10' ->> '12' AS NUMERIC), 0)::INT IS NOT NULL) "
    sql += "OR (ROUND(CAST(predictions -> 'a_pct25' ->> '11' AS NUMERIC), 0)::INT IS NOT NULL "
    sql += "AND ROUND(CAST(predictions -> 'a_pct25' ->> '12' AS NUMERIC), 0)::INT IS NOT NULL) "
    sql += "OR (ROUND(CAST(predictions -> 'a_median' ->> '11' AS NUMERIC), 0)::INT IS NOT NULL "
    sql += "AND ROUND(CAST(predictions -> 'a_median' ->> '12' AS NUMERIC), 0)::INT IS NOT NULL) "
    sql += "OR (ROUND(CAST(predictions -> 'a_pct75' ->> '11' AS NUMERIC), 0)::INT IS NOT NULL "
    sql += "AND ROUND(CAST(predictions -> 'a_pct75' ->> '12' AS NUMERIC), 0)::INT IS NOT NULL) "
    sql += "OR (ROUND(CAST(predictions -> 'a_pct90' ->> '11' AS NUMERIC), 0)::INT IS NOT NULL "
    sql += "AND ROUND(CAST(predictions -> 'a_pct90' ->> '12' AS NUMERIC), 0)::INT IS NOT NULL) "
    sql += "OR (ROUND(CAST(predictions -> 'a_mean' ->> '11' AS NUMERIC), 0)::INT IS NOT NULL "
    sql += "AND ROUND(CAST(predictions -> 'a_mean' ->> '12' AS NUMERIC), 0)::INT IS NOT NULL) "
    sql += "THEN 1 ELSE 0 "
    sql += "END AS forecast_flag "                                                                  #161

    sql += ", 'oews' AS oews_flag "                                                                 #162
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
    sql += ") employment "                                                                          #163
    sql += ", predictions -> 'index' AS dates "                                                     #164

    sql += "FROM "
    sql += "{}.naics_occ_pred_20221222 nop ".format(schema)
    # sql += "{}.naics_occ_pred_v5 nop ".format(schema)
    # sql += "{}.naics_occ_pred_v4 nop ".format(schema)

    sql += "LEFT JOIN {}.unemployment_msa_transpose_20221222 umt ".format(schema)
    sql += "ON nop.msa_code = umt.msa_code "

    sql += "WHERE 1=1 "
    sql += "AND nop.msa_code = '{}' ".format(msa_code)
    sql += "AND nop.us_occ_naics = '{}' ".format(naics_code)
    sql += "AND nop.occ_code = '{}' ".format(occ_code)

    # print(sql)

    cur.execute(sql)
    a = cur.fetchone()
    try:
        retval = list(a)
    except Exception as e:
        retval = []
        print(e)
    return retval


def get_skills_from_county_from_db(county):
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    cur = connection.cursor()
    cur.execute("select distinct tech_skills from {}.county_occ_skills_v1 where area_fips = '" + county + "' order by tech_skills".format(schema))
    # cur.execute("select distinct onetsoc_code, example from onet.technology_skills order by example")
    a = cur.fetchall()
    return a


def get_skills_from_msa_from_db(msa):
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    # print("select distinct tech_skills from dev.msa_occ_skills_v1 where msa_code = '" + msa + "' order by tech_skills")

    cur = connection.cursor()
    cur.execute("select distinct tech_skills from {}.msa_occ_skills_v1 where msa_code = '".format(schema) + msa + "' order by tech_skills")
    a = cur.fetchall()
    return a

def get_msa_wage_objs_skills_v1(msa_code, skills_list, user_id='1234'):
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    b = incremental_forecast(skills_list, msa_code, user_id, schema)
    # print("dataset_id = ", b)
    return b

def get_msa_wage_objs_skills_only_data_v1(dataset_id, user_id='1234'):
    if settings.ENVIRONMENT == 'prod':
        schema = 'prod'
    else:
        schema = 'dev'

    a = queryer2(dataset_id = dataset_id, schema = schema)[0]
    
    try:
        retval = list(a)
        # retval = list(b)
    except Exception as e:
        retval = []
        print(e)
    return retval
