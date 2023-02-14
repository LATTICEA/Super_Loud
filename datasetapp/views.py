from django.shortcuts import render, redirect
from .models import datasetmodel
from authentication.models import profilemodel
from django.contrib.auth.decorators import login_required
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.http import JsonResponse
from .dbreqs import *
from subscription.views import find_sub_obj

bootstrap_colors = ['dark','secondary','success','primary','danger','white']

@login_required(login_url="/login/")
def subscriptions(request):
    template = 'dataset/superloud_template.html'
    context = {'segment':'superloud_template'}

    if settings.ENVIRONMENT == 'prod':
        context['environment'] = 'prod'
    else:
        context['environment'] = 'dev'

    obj = profilemodel.objects.get(user=request.user)
    context['obj'] = obj
    if context['obj'].is_suspended:
        return redirect('/account-suspended')
    if not context['obj'].verified:
        return redirect('/not-verified')

    subobj = find_sub_obj(context['obj'])
    context['subobj'] = subobj

    if not context['subobj'].active:
        return redirect('accounts/not-subscribed')

    context['subtype'] = subobj.subtype
    if request.method == 'POST':
        try:
            if request.POST['edit'] == "Y":
                obj = datasetmodel.objects.get(pk=request.POST['sels'])
            else:
                obj = datasetmodel()
        except:
            if request.POST['edit-create'] == "Y":
                obj = datasetmodel.objects.get(pk=request.POST['sels-create'])
            else:
                obj = datasetmodel()

        try:
            # if request.POST['county_msa_switch_value'] == 'county':
            #     obj.user = request.user
            #     obj.settype = request.POST['county_msa_switch_value']
            #     obj.name = request.POST['name']
            #     obj.area_fips = request.POST['area'].split('--==--')[0]
            #     obj.industry_code = request.POST['industry'].split('--==--')[0]
            #     obj.state_code = request.POST['state'].split('--==--')[0]
            #     obj.area_title = request.POST['area'].split('--==--')[1]
            #     obj.industry_title = request.POST['industry'].split('--==--')[1]
            #     obj.state_title = request.POST['state'].split('--==--')[1]
            #     obj.skills = request.POST['skills']
            #     obj.save()
            # else:
            obj.user = request.user
            # obj.settype = request.POST['county_msa_switch_value']
            obj.settype = 'msa'
            obj.name = request.POST['name']
            obj.area_fips = request.POST['msa'].split('--==--')[0]
            obj.industry_code = request.POST['industry'].split('--==--')[0]
            obj.state_code = request.POST['state'].split('--==--')[0]
            obj.area_title = request.POST['msa'].split('--==--')[1]
            obj.industry_title = request.POST['industry'].split('--==--')[1]
            obj.state_title = request.POST['state'].split('--==--')[1]
            try:
                obj.occupation_code = request.POST['occupation'].split('--==--')[0]
                obj.occupation_title = request.POST['occupation'].split('--==--')[1]
            except:
                obj.occupation_code = " "
                obj.occupation_title = " "
            obj.skills = request.POST['skills']
            obj.save()
        except:
            # if request.POST['county_msa_switch_value_create'] == 'county':
            #     obj.user = request.user
            #     obj.settype = request.POST['county_msa_switch_value_create']
            #     obj.name = request.POST['name_create']
            #     obj.area_fips = request.POST['areaCreate'].split('--==--')[0]
            #     obj.industry_code = request.POST.getlist('skillCreate')
            #     obj.state_code = request.POST['state_create'].split('--==--')[0]
            #     obj.area_title = request.POST['areaCreate'].split('--==--')[1]
            #     obj.industry_title = request.POST.getlist('skillCreate')
            #     obj.state_title = request.POST['state_create'].split('--==--')[1]
            #     obj.skills = request.POST['skills-create']
            #     obj.save()
            # else:

            obj.user = request.user
            # obj.settype = request.POST['county_msa_switch_value_create']
            obj.settype = 'msa'
            try:
                obj.name = request.POST['name_create']
            except:
                obj.name = request.POST['nameCreate']

            try:
                obj.area_fips = request.POST['msaCreate'].split('--==--')[0]
            except:
                obj.area_fips = request.POST['msa_create'].split('--==--')[0]
            
            try:
                obj.industry_code = request.POST.getlist('skillCreate')
            except:
                obj.industry_code = request.POST.getlist('skill_create')
            
            try:
                obj.state_code = request.POST['stateCreate'].split('--==--')[0]
            except:
                obj.state_code = request.POST['state_create'].split('--==--')[0]
            
            try:
                obj.area_title = request.POST['msaCreate'].split('--==--')[1]
            except:
                obj.area_title = request.POST['msa_create'].split('--==--')[1]
            
            try:
                obj.industry_title = request.POST.getlist('skillCreate')
            except:
                obj.industry_title = request.POST.getlist('skill_create')
            
            try:
                obj.state_title = request.POST['stateCreate'].split('--==--')[1]
            except:
                obj.state_title = request.POST['state_create'].split('--==--')[1]
            
            try:
                obj.occupation_code = request.POST['occupationCreate'].split('--==--')[0]
                obj.occupation_title = request.POST['occupationCreate'].split('--==--')[1]
            except:
                obj.occupation_code = " "
                obj.occupation_title = " "
            obj.skills = request.POST['skills-create']
            obj.save()

    context['datasets'] = datasetmodel.objects.filter(user=request.user)

    # print(context['datasets'][0].industry_code)
    # print(context['datasets'][0].industry_title)

    if len(context['datasets']) > 0:
        wagelist_hourly = []
        wagelist_salary = []
        qtrlist = []
        yearlist = []
        forecastable_flag = []
        cross_ref_flag = []
        area_id = []
        industry_id = []
        occupation_flag = []
        occupation_name = []
        occupation_code = []
        skills_list =[]
        skills_flag = []

        all_data = []

        # if subobj.active == False or context['obj'].is_admin == False:
        if subobj.active == False:
            tempno = 40
        else:
            tempno = 48
            
        date_range = get_date_range(48 - tempno)

        for obj in context['datasets']:
            if obj.skills != 'Y':
                print(obj.id)
                area_id.append(obj.area_fips)
                industry_id.append(obj.industry_code)

                if obj.settype == 'county':
                    temp = get_wage_objs_v4(obj.area_fips, obj.industry_code)
                else:
                    if obj.occupation_code != " ":
                        industry = get_industry_clean_code(obj.industry_code)[0]
                        temp = get_oews_obj_v1(obj.area_fips, industry, obj.occupation_code)
                    else:
                        if obj.skills == 'Y':
                            pass
                        else:
                            temp = get_msa_wage_objs_v5(obj.area_fips, obj.industry_code)

                all_data.append(temp)

                # print(temp)

                if obj.occupation_code != " ":
                    occupation_flag.append(1)
                    skills_flag.append(0)
                    occupation_name.append(obj.occupation_title)
                    occupation_code.append(obj.occupation_code)
                    counter = 0
                    for i in temp[69:80][::-1]: ### mean for non-forecasted values. Reverse list to get most recent data since it's at the end
                        if i is not None:
                            wagelist_hourly.append("{:,.2f}".format(i / 2080)) #latest wage
                            wagelist_salary.append("{:,}".format(i)) #latest wage

                            forecastable_flag.append(0) 
                            cross_ref_flag.append(0)

                            qtrlist.append(2) #qtr will always be Q2 for annual data since it's updated in May. Will change when broken down into quarters.

                            #year only forecasting two years out, so minus 2 to get current year. Minus counter to get latest year. 
                            yearlist.append(date_range[0][0]-2-counter) 
                            # yearlist.append(date_range[0][0]-counter) 

                            skills_list.append("")
                            break
                        counter += 1

                else:
                    occupation_flag.append(0)
                    skills_flag.append(0)
                    occupation_name.append("")
                    occupation_code.append("")
                    wagelist_hourly.append("{:,.2f}".format(temp[2]/39.99999)) #latest wage
                    wagelist_salary.append("{:,}".format(temp[2]*52)) #latest wage

                    forecastable_flag.append(temp[-3]) 
                    cross_ref_flag.append(temp[-2])

                    qtrlist.append(temp[1]) #qtr
                    yearlist.append(temp[0]) #year

                    skills_list.append("")
            else:
                area_id.append(obj.area_fips)
                industry_id.append("") ### Acutally a list of skills

                if obj.settype == 'county':
                    # temp = get_wage_objs_v4(obj.area_fips, obj.industry_code)
                    pass
                else:
                    if obj.dataset_id == '':
                        ### There is no dataset yet and it needs to be created
                        dataset_id = get_msa_wage_objs_skills_v1(obj.area_fips, obj.industry_code)
                        obj.dataset_id = dataset_id
                        obj.save()

                        temp = get_msa_wage_objs_skills_only_data_v1(obj.dataset_id)
                    else:
                        ### There is a dataset and we're skipping the creation piece
                        temp = get_msa_wage_objs_skills_only_data_v1(obj.dataset_id)

                    all_data.append(temp)

                    occupation_flag.append(1)
                    skills_flag.append(1)
                    occupation_name.append("")
                    occupation_code.append("")
                    wagelist_hourly.append("{:,.2f}".format(temp[157])) #latest wage
                    wagelist_salary.append("{:,}".format(temp[79])) #latest wage

                    forecastable_flag.append(0) 
                    cross_ref_flag.append(0)

                    qtrlist.append(2) #qtr
                    yearlist.append(2021) #year

                    skills_list.append(', '.join(str(obj.industry_code).strip('][').replace("'",'').split(',')))


        context['datasets_view_hourly'] = zip(
            context['datasets']
            , wagelist_hourly
            , qtrlist
            , yearlist
            , forecastable_flag
            , cross_ref_flag
            , area_id
            , industry_id
            , occupation_flag
            , occupation_name
            , occupation_code
            , skills_list
            , skills_flag
        )

        context['datasets_view_salary'] = zip(
            context['datasets']
            , wagelist_salary
            , qtrlist
            , yearlist
            , forecastable_flag
            , cross_ref_flag
            , area_id
            , industry_id
            , occupation_flag
            , occupation_name
            , occupation_code
            , skills_list
            , skills_flag
        )
        
        temp = {}
        count = 0
        for i in range(len(context['datasets'])):
            count += 1
            temp[context['datasets'][i].name] = bootstrap_colors[i]
            if count == 6:
                break
        context['colors'] = temp

        temp = ['Dataset', 'Area', 'Details']
        # temp = ['Dataset', 'Area', 'Industry', 'Occupation']
        qtr = date_range[0][1]
        year = date_range[0][0]

        xaxis = []
        for i in range(tempno):
            temp.append('Q{}-{}'.format(qtr,year))
            xaxis.append('Q{}-{}'.format(qtr,year))
            qtr = qtr - 1
            if qtr == 0:
                qtr = 4
                year = year - 1

        context['table_data'] = temp


        temp1a = []
        temp1b = []
        for i in range(len(context['datasets'])):
            # print(context['datasets'][i])
            if context['datasets'][i].occupation_title == " " and all_data[i][-1] != 'skills':
                temp1 = [
                    context['datasets'][i].name
                    , context['datasets'][i].area_title
                    , context['datasets'][i].industry_title
                    # , ""
                ]
                
                temp2 = [
                    context['datasets'][i].name
                    , context['datasets'][i].area_title
                    , context['datasets'][i].industry_title
                    # , ""
                ]

                if subobj.subtype != 'Data+Predictions' and all_data[i][-1] != 'skills':
                    retval_annually = all_data[i][3:43]
                    retval_hourly = all_data[i][51:91]
                else:
                    if all_data[i][98] is not None:
                        retval_annually = all_data[i][43:51][::-1] + all_data[i][3:43]
                        retval_hourly = all_data[i][91:99][::-1] + all_data[i][51:91]
                    else:
                        retval_annually = all_data[i][3:43]
                        retval_hourly = all_data[i][51:91]

                while len(retval_hourly) < tempno: #minus 8 for two quarters. Cannot make predictions
                    retval_hourly.insert(0, None)
                    retval_annually.insert(0, None)

                for i in retval_hourly:
                    try:
                        temp1.append(round(float(i),2))
                    except:
                        temp1.append(i)

                for h in retval_annually:
                    try:
                        temp2.append("{:,}".format(int(h)))
                    except:
                        temp2.append(h)

                temp1a.append(temp1)
                temp1b.append(temp2)

            elif context['datasets'][i].occupation_title == " " and all_data[i][-1] == 'skills':
                temp1 = [
                    context['datasets'][i].name
                    , context['datasets'][i].area_title
                    # , context['datasets'][i].industry_title
                    , ', '.join(str(context['datasets'][i].industry_title).strip('][').replace("'",'').split(','))
                    # , context['datasets'][i].occupation_title
                ]

                temp2 = [
                    context['datasets'][i].name
                    , context['datasets'][i].area_title
                    # , context['datasets'][i].industry_title
                    , ', '.join(str(context['datasets'][i].industry_title).strip('][').replace("'",'').split(','))
                    # , context['datasets'][i].occupation_title
                ]

                if subobj.subtype != 'Data+Predictions':
                    retval_annually = all_data[i][69:80][::-1]
                    retval_hourly = all_data[i][147:158][::-1]
                else:
                    retval_annually = all_data[i][69:82][::-1]
                    retval_hourly = all_data[i][147:160][::-1]

                temp_hourly_2 = []
                temp_salary_2 = []
                for j in retval_hourly:
                    try:
                        temp_hourly_2.append(round(float(j),2))
                    except:
                        temp_hourly_2.append(j)
                for j in retval_annually:
                    try:
                        temp_salary_2.append("{:,}".format(int(j)))
                    except:
                        temp_salary_2.append(j)

                counter = 0
                for x in range(len(xaxis[::-1])):
                    if xaxis[::-1][x-1][-4:] != xaxis[::-1][x][-4:]:
                        temp1.append(temp_hourly_2[::-1][counter])
                        temp2.append(temp_salary_2[::-1][counter])
                        counter += 1
                    else:
                        temp1.append(temp_hourly_2[::-1][counter-1])
                        temp2.append(temp_salary_2[::-1][counter-1])

                temp1a.append(temp1[:3] + temp1[3:][::-1])
                temp1b.append(temp2[:3] + temp2[3:][::-1])

            else:
                temp1 = [
                    context['datasets'][i].name
                    , context['datasets'][i].area_title
                    # , context['datasets'][i].industry_title
                    , context['datasets'][i].occupation_title
                ]
                
                temp2 = [
                    context['datasets'][i].name
                    , context['datasets'][i].area_title
                    # , context['datasets'][i].industry_title
                    , context['datasets'][i].occupation_title
                ]

                if subobj.subtype != 'Data+Predictions':
                    retval_annually = all_data[i][69:80][::-1]
                    retval_hourly = all_data[i][147:158][::-1]
                else:
                    retval_annually = all_data[i][69:82][::-1]
                    retval_hourly = all_data[i][147:160][::-1]

                temp_hourly_2 = []
                temp_salary_2 = []
                for j in retval_hourly:
                    try:
                        temp_hourly_2.append(round(float(j),2))
                    except:
                        temp_hourly_2.append(j)
                for j in retval_annually:
                    try:
                        temp_salary_2.append("{:,}".format(int(j)))
                    except:
                        temp_salary_2.append(j)

                counter = 0
                for x in range(len(xaxis[::-1])):
                    if xaxis[::-1][x-1][-4:] != xaxis[::-1][x][-4:]:
                        temp1.append(temp_hourly_2[::-1][counter])
                        temp2.append(temp_salary_2[::-1][counter])
                        counter += 1
                    else:
                        temp1.append(temp_hourly_2[::-1][counter-1])
                        temp2.append(temp_salary_2[::-1][counter-1])

                temp1a.append(temp1[:3] + temp1[3:][::-1])
                temp1b.append(temp2[:3] + temp2[3:][::-1])

        context['table_data_rows_hourly'] = temp1a
        context['table_data_rows_annually'] = temp1b
    context['areas'] = get_area_fips()
    context['msa'] = get_msa()
    context['industries'] = get_industry()
    context['states'] = get_states()

    context['unemp'] = subobj.active

    return render(request,template,context)

def get_qtr_year_from_objs(objs):
    qtr = 1
    year = 0
    for i in objs:
        year = i.year
        qtr = i.month
        break
    if str(qtr) == "4":
        qtr = 2
    elif str(qtr) == "7":
        qtr = 3
    elif str(qtr) == "10":
        qtr = 4
    else:
        qtr = 1
    return qtr,year

def delete_dataset(request,id):
    obj = datasetmodel.objects.get(pk=id)
    obj.delete()
    return redirect('/datasets')

# @cache_page(CACHE_TTL)
def get_graph_values(request, area, industry, occupation, skills):
    # print(request, area, industry, occupation, skills)
    obj = profilemodel.objects.get(user=request.user)
    subobj = find_sub_obj(obj)

    if area == 'none' and industry == 'none' and occupation == 'none':
        dataobjs = datasetmodel.objects.filter(user=request.user)
        check = True

    subobj = find_sub_obj(profilemodel.objects.get(user=request.user))

    # if subobj.active == False or obj.is_admin == False:
    if subobj.active == False:
        tempno = 40
    else:
        tempno = 48

    xaxis = []
    temp = []
    qtr = 1
    year = 0

    date_range = get_date_range(48 - tempno)

    all_county_data = []
    county_names = []
    county_ids = []
    all_msa_data = []
    msa_names = []
    msa_ids = []
    all_occ_data = []
    occ_names = []
    occ_ids = []
    all_skills_data = []
    skills_names = []
    skills_ids = []

    for i in dataobjs:
        if i.settype == 'county':
            temp = get_wage_objs_v4(i.area_fips, i.industry_code)
            all_county_data.append(temp)
            county_names.append(i.name)
            county_ids.append(i.id)
        elif i.settype == 'msa' and i.occupation_code == " " and i.skills != "Y":
            temp = get_msa_wage_objs_v5(i.area_fips, i.industry_code)
            all_msa_data.append(temp)
            msa_names.append(i.name)
            msa_ids.append(i.id)
        elif i.settype == 'msa' and i.occupation_code == " " and i.skills == "Y":
            # temp = get_msa_wage_objs_skills_v1(i.area_fips, i.industry_code) ### i.industry_code = skills... horrible naming convention
            # temp = GET_THE_DATASET_FROM_NEW_TABLE(i.area_fips, i.industry_code, i.dataset_id) ### i.industry_code = skills... horrible naming convention

            temp = get_msa_wage_objs_skills_only_data_v1(i.dataset_id)
            
            all_skills_data.append(temp)
            skills_names.append(i.name)

            skills_ids.append(i.id)
        else:
            industry = get_industry_clean_code(i.industry_code)[0]
            temp = get_oews_obj_v1(i.area_fips, industry, i.occupation_code)
            all_occ_data.append(temp)
            occ_names.append(i.name)
            occ_ids.append(i.id)

    qtr, year = date_range[0][1], date_range[0][0]

    for i in range(tempno):
        xaxis.append('Q{}-{}'.format(qtr,year))
        qtr = qtr - 1
        if qtr == 0:
            qtr = 4
            year = year - 1

    unemployment_rate = []
    unemployment = []
    employment = []
    labor_force = []
    inferred = []
    yaxis_hourly = []
    yaxis_annually = []
    yaxis_cross_ref = []
    bands = []

    for i in range(len(all_county_data)):
        temp1 = []
        temp2 = []
        if tempno == 40:
            retval_annually = all_county_data[i][3:43]
            retval_hourly = all_county_data[i][51:91]
        else:
            if all_county_data[i][98] is not None:
                retval_annually = all_county_data[i][43:51][::-1] + all_county_data[i][3:43]
                retval_hourly = all_county_data[i][91:99][::-1] + all_county_data[i][51:91]
            else:
                retval_annually = all_county_data[i][3:43]
                retval_hourly = all_county_data[i][51:91]

        if all_county_data[i][98] is not None:
            while len(retval_hourly) < tempno: #minus 8 for two quarters. Cannot make predictions
                retval_hourly.append(None)
                retval_annually.append(None)

            for j in retval_hourly:
                try:
                    temp1.append(round(float(j),2))
                except:
                    temp1.append(j)

            for h in retval_annually:
                try:
                    temp2.append(int(h))
                except:
                    temp2.append(h)
        else:
            for j in retval_hourly:
                try:
                    temp1.append(round(float(j),2))
                except:
                    temp1.append(j)

            for h in retval_annually:
                try:
                    temp2.append(int(h))
                except:
                    temp2.append(h)

            while len(temp1) < tempno:
                temp1.insert(0, None)
                temp2.insert(0, None)

        inferred_1 = []
        for j in all_county_data[i][100].values():
            if j == 0:
                inferred_1.append(0)
            else:
                inferred_1.append(1)

        for r in all_county_data[i][99]:
            try:
                r['data_hourly'] = list(r['data_hourly'].values())
                r['data_annually'] = list(r['data_annually'].values())
                r['data_inferred'] = list(r['data_inferred'].values())
            except:
                pass

        if subobj.active == True:
            unemployment_rate.append(list(all_county_data[i][103]['unemployment_rate'].values())[:-1][::-1])
            unemployment.append(list(all_county_data[i][103]['unemployment'].values())[:-1][::-1])
            employment.append(list(all_county_data[i][103]['employment'].values())[:-1][::-1])
            labor_force.append(list(all_county_data[i][103]['labor_force'].values())[:-1][::-1])
            bands.append([])
        else:
            pass

        inferred.append(inferred_1)
        yaxis_hourly.append({'name':county_names[i], 'data':temp1[::-1], 'id':county_ids[i]})
        yaxis_annually.append({'name':county_names[i], 'data':temp2[::-1], 'id':county_ids[i]})
        yaxis_cross_ref.append({'name':county_names[i],'id':county_ids[i],'data':all_county_data[i][99]})


    for i in range(len(all_msa_data)):
        temp1 = []
        temp2 = []
        if tempno == 40:
            retval_annually = all_msa_data[i][3:43]
            retval_hourly = all_msa_data[i][51:91]
        else:
            if all_msa_data[i][98] is not None:
                retval_annually = all_msa_data[i][43:51][::-1] + all_msa_data[i][3:43]
                retval_hourly = all_msa_data[i][91:99][::-1] + all_msa_data[i][51:91]
            else:
                retval_annually = all_msa_data[i][3:43]
                retval_hourly = all_msa_data[i][51:91]

        if all_msa_data[i][98] is not None:
            while len(retval_hourly) < tempno: #minus 8 for two quarters. Cannot make predictions
                retval_hourly.append(None)
                retval_annually.append(None)

            for j in retval_hourly:
                try:
                    temp1.append(round(float(j),2))
                except:
                    temp1.append(j)

            for h in retval_annually:
                try:
                    temp2.append(int(h))
                except:
                    temp2.append(h)
        else:
            for j in retval_hourly:
                try:
                    temp1.append(round(float(j),2))
                except:
                    temp1.append(j)

            for h in retval_annually:
                try:
                    temp2.append(int(h))
                except:
                    temp2.append(h)

            while len(temp1) < tempno:
                temp1.insert(0, None)
                temp2.insert(0, None)

        inferred_1 = []
        for j in all_msa_data[i][100].values():
            if j == 0:
                inferred_1.append(0)
            else:
                inferred_1.append(1)

        for r in all_msa_data[i][99]:
            try:
                r['data_hourly'] = list(r['json_data']['data_hourly'].values())
                r['data_annually'] = list(r['json_data']['data_annually'].values())
                r['data_inferred'] = list(r['json_data']['data_inferred'].values())
            except:
                pass

        if subobj.active == True:
            unemployment_rate.append(list(all_msa_data[i][103]['unemployment_rate'].values())[:-1][::-1])
            unemployment.append(list(all_msa_data[i][103]['unemployment'].values())[:-1][::-1])
            employment.append(list(all_msa_data[i][103]['employment'].values())[:-1][::-1])
            labor_force.append(list(all_msa_data[i][103]['labor_force'].values())[:-1][::-1])
            bands.append([])
        else:
            pass

        inferred.append(inferred_1)
        yaxis_hourly.append({'name':msa_names[i], 'data':temp1[::-1], 'id':msa_ids[i]})
        yaxis_annually.append({'name':msa_names[i], 'data':temp2[::-1], 'id':msa_ids[i]})
        yaxis_cross_ref.append({'name':msa_names[i], 'id':msa_ids[i], 'data':all_msa_data[i][99]})


    for i in range(len(all_occ_data)):
        temp_mean_hourly = []
        temp_mean_salary = []
        temp_10_hourly = []
        temp_10_salary = []
        temp_25_hourly = []
        temp_25_salary = []
        temp_median_hourly = []
        temp_median_salary = []
        temp_75_hourly = []
        temp_75_salary = []
        temp_90_hourly = []
        temp_90_salary = []
        if tempno == 40:
            mean_annually = all_occ_data[i][69:80]
            mean_hourly = all_occ_data[i][147:158]

            p10_annually = all_occ_data[i][4:15]
            p10_hourly = all_occ_data[i][82:93]

            p25_annually = all_occ_data[i][17:28]
            p25_hourly = all_occ_data[i][95:106]

            median_annually = all_occ_data[i][30:41]
            median_hourly = all_occ_data[i][108:119]

            p75_annually = all_occ_data[i][43:54]
            p75_hourly = all_occ_data[i][121:132]

            p90_annually = all_occ_data[i][56:67]
            p90_hourly = all_occ_data[i][134:145]
        else:
            mean_annually = all_occ_data[i][69:82]
            mean_hourly = all_occ_data[i][147:160]

            p10_annually = all_occ_data[i][4:17]
            p10_hourly = all_occ_data[i][82:95]

            p25_annually = all_occ_data[i][17:30]
            p25_hourly = all_occ_data[i][95:108]

            median_annually = all_occ_data[i][30:43]
            median_hourly = all_occ_data[i][108:121]

            p75_annually = all_occ_data[i][43:56]
            p75_hourly = all_occ_data[i][121:134]

            p90_annually = all_occ_data[i][56:69]
            p90_hourly = all_occ_data[i][134:147]

        # if all_occ_data[i][82] is not None:
        for a in mean_hourly:
            try:
                temp_mean_hourly.append(round(float(a),2))
            except:
                temp_mean_hourly.append(a)
        for b in p10_hourly: 
            try:
                temp_10_hourly.append(round(float(b),2))
            except:
                temp_10_hourly.append(b)
        for c in p25_hourly: 
            try:
                temp_25_hourly.append(round(float(c),2))
            except:
                temp_25_hourly.append(c)
        for d in median_hourly: 
            try:
                temp_median_hourly.append(round(float(d),2))
            except:
                temp_median_hourly.append(d)
        for e in p75_hourly: 
            try:
                temp_75_hourly.append(round(float(e),2))
            except:
                temp_75_hourly.append(e)
        for f in p90_hourly: 
            try:
                temp_90_hourly.append(round(float(f),2))
            except:
                temp_90_hourly.append(f)

        for g in mean_annually:
            try:
                temp_mean_salary.append(int(g))
            except:
                temp_mean_salary.append(g)
        for h in p10_annually: 
            try:
                temp_10_salary.append(int(h))
            except:
                temp_10_salary.append(h)
        for j in p25_annually: 
            try:
                temp_25_salary.append(int(j))
            except:
                temp_25_salary.append(j)
        for k in median_annually: 
            try:
                temp_median_salary.append(int(k))
            except:
                temp_median_salary.append(k)
        for l in p75_annually: 
            try:
                temp_75_salary.append(int(l))
            except:
                temp_75_salary.append(l)
        for m in p90_annually: 
            try:
                temp_90_salary.append(int(m))
            except:
                temp_90_salary.append(m)

        # occ_date_range = get_date_range_occ()

        occ_date_range_raw = get_date_range_occ()

        occ_date_range = []
        for n in range(len(occ_date_range_raw)):
            occ_date_range.append('Q1-{}'.format(str(occ_date_range_raw[n][0])[0:4]))

        band_dict = {
            'hourly': {
                'dates': occ_date_range
                , 'series': [
                    {
                        'id': str(occ_ids[i])+'Lowest'+'Hourly'
                        , 'name':'Lowest'
                        , 'values': temp_10_hourly
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                    , {
                        'id': str(occ_ids[i])+'Low'+'Hourly'
                        , 'name':'Low'
                        , 'values': temp_25_hourly
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                    , {
                        'id': str(occ_ids[i])+'Middle'+'Hourly'
                        , 'name':'Middle'
                        , 'values': temp_median_hourly
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                    , {
                        'id': str(occ_ids[i])+'High'+'Hourly'
                        , 'name':'High'
                        , 'values': temp_75_hourly
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                    , {
                        'id': str(occ_ids[i])+'Highest'+'Hourly'
                        , 'name':'Highest'
                        , 'values': temp_90_hourly
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                    , {
                        'id': str(occ_ids[i])+'Average'+'Hourly'
                        , 'name':'Average'
                        , 'values': temp_mean_hourly
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                ]
            }
            , 'salary': {
                'dates': occ_date_range
                , 'series': [
                    {
                        'id': str(occ_ids[i])+'Lowest'+'Salary'
                        , 'name':'Lowest'
                        , 'values': temp_10_salary
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                    , {
                        'id': str(occ_ids[i])+'Low'+'Salary'
                        , 'name':'Low'
                        , 'values': temp_25_salary
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                    , {
                        'id': str(occ_ids[i])+'Middle'+'Salary'
                        , 'name':'Middle'
                        , 'values': temp_median_salary
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                    , {
                        'id': str(occ_ids[i])+'High'+'Salary'
                        , 'name':'High'
                        , 'values': temp_75_salary
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                    , {
                        'id': str(occ_ids[i])+'Highest'+'Salary'
                        , 'name':'Highest'
                        , 'values': temp_90_salary
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                    , {
                        'id': str(occ_ids[i])+'Average'+'Salary'
                        , 'name':'Average'
                        , 'values': temp_mean_salary
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                ]
            }
        }

        inferred_1 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1]

        temp_hourly_2 = []
        temp_salary_2 = []
        counter = 0
        for x in range(len(xaxis[::-1])):
            if xaxis[::-1][x-1][-4:] != xaxis[::-1][x][-4:]:
                temp_hourly_2.append(temp_mean_hourly[counter])
                temp_salary_2.append(temp_mean_salary[counter])
                counter += 1
            else:
                temp_hourly_2.append(temp_mean_hourly[counter-1])
                temp_salary_2.append(temp_mean_salary[counter-1])

        if subobj.active == True:
            unemployment_rate.append(list(all_occ_data[i][-2]['employment']['unemployment_rate'].values())[:-1][::-1])
            unemployment.append(list(all_occ_data[i][-2]['employment']['unemployment'].values())[:-1][::-1])
            employment.append(list(all_occ_data[i][-2]['employment']['employment'].values())[:-1][::-1])
            labor_force.append(list(all_occ_data[i][-2]['employment']['labor_force'].values())[:-1][::-1])
            bands.append([band_dict])
        else:
            pass

        inferred.append(inferred_1)
        yaxis_hourly.append({'name':occ_names[i], 'data':temp_hourly_2, 'id':occ_ids[i]})
        yaxis_annually.append({'name':occ_names[i], 'data':temp_salary_2, 'id':occ_ids[i]})
        yaxis_cross_ref.append({'name':occ_names[i], 'id':occ_ids[i], 'data':[]})

        ###########
        ### END ###
        ###########


    for i in range(len(all_skills_data)):
        # print(all_skills_data[i])

        temp_mean_hourly = []
        temp_mean_salary = []
        temp_10_hourly = []
        temp_10_salary = []
        temp_25_hourly = []
        temp_25_salary = []
        temp_median_hourly = []
        temp_median_salary = []
        temp_75_hourly = []
        temp_75_salary = []
        temp_90_hourly = []
        temp_90_salary = []
        if tempno == 40:
            mean_annually = all_skills_data[i][69:80]
            mean_hourly = all_skills_data[i][147:158]

            p10_annually = all_skills_data[i][4:15]
            p10_hourly = all_skills_data[i][82:93]

            p25_annually = all_skills_data[i][17:28]
            p25_hourly = all_skills_data[i][95:106]

            median_annually = all_skills_data[i][30:41]
            median_hourly = all_skills_data[i][108:119]

            p75_annually = all_skills_data[i][43:54]
            p75_hourly = all_skills_data[i][121:132]

            p90_annually = all_skills_data[i][56:67]
            p90_hourly = all_skills_data[i][134:145]
        else:
            mean_annually = all_skills_data[i][69:82]
            mean_hourly = all_skills_data[i][147:160]

            p10_annually = all_skills_data[i][4:17]
            p10_hourly = all_skills_data[i][82:95]

            p25_annually = all_skills_data[i][17:30]
            p25_hourly = all_skills_data[i][95:108]

            median_annually = all_skills_data[i][30:43]
            median_hourly = all_skills_data[i][108:121]

            p75_annually = all_skills_data[i][43:56]
            p75_hourly = all_skills_data[i][121:134]

            p90_annually = all_skills_data[i][56:69]
            p90_hourly = all_skills_data[i][134:147]

        # if all_occ_data[i][82] is not None:
        for a in mean_hourly:
            try:
                temp_mean_hourly.append(round(float(a),2))
            except:
                temp_mean_hourly.append(a)
        for b in p10_hourly: 
            try:
                temp_10_hourly.append(round(float(b),2))
            except:
                temp_10_hourly.append(b)
        for c in p25_hourly: 
            try:
                temp_25_hourly.append(round(float(c),2))
            except:
                temp_25_hourly.append(c)
        for d in median_hourly: 
            try:
                temp_median_hourly.append(round(float(d),2))
            except:
                temp_median_hourly.append(d)
        for e in p75_hourly: 
            try:
                temp_75_hourly.append(round(float(e),2))
            except:
                temp_75_hourly.append(e)
        for f in p90_hourly: 
            try:
                temp_90_hourly.append(round(float(f),2))
            except:
                temp_90_hourly.append(f)

        for g in mean_annually:
            try:
                temp_mean_salary.append(int(g))
            except:
                temp_mean_salary.append(g)
        for h in p10_annually: 
            try:
                temp_10_salary.append(int(h))
            except:
                temp_10_salary.append(h)
        for j in p25_annually: 
            try:
                temp_25_salary.append(int(j))
            except:
                temp_25_salary.append(j)
        for k in median_annually: 
            try:
                temp_median_salary.append(int(k))
            except:
                temp_median_salary.append(k)
        for l in p75_annually: 
            try:
                temp_75_salary.append(int(l))
            except:
                temp_75_salary.append(l)
        for m in p90_annually: 
            try:
                temp_90_salary.append(int(m))
            except:
                temp_90_salary.append(m)

        occ_date_range_raw = get_date_range_occ()

        occ_date_range = []
        for n in range(len(occ_date_range_raw)):
            occ_date_range.append('Q1-{}'.format(str(occ_date_range_raw[n][0])[0:4]))

        band_dict = {
            'hourly': {
                'dates': occ_date_range
                , 'series': [
                    {
                        'id': str(skills_ids[i])+'Lowest'+'Hourly'
                        , 'name':'Lowest'
                        , 'values': temp_10_hourly
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                    , {
                        'id': str(skills_ids[i])+'Low'+'Hourly'
                        , 'name':'Low'
                        , 'values': temp_25_hourly
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                    , {
                        'id': str(skills_ids[i])+'Middle'+'Hourly'
                        , 'name':'Middle'
                        , 'values': temp_median_hourly
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                    , {
                        'id': str(skills_ids[i])+'High'+'Hourly'
                        , 'name':'High'
                        , 'values': temp_75_hourly
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                    , {
                        'id': str(skills_ids[i])+'Highest'+'Hourly'
                        , 'name':'Highest'
                        , 'values': temp_90_hourly
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                    , {
                        'id': str(skills_ids[i])+'Average'+'Hourly'
                        , 'name':'Average'
                        , 'values': temp_mean_hourly
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                ]
            }
            , 'salary': {
                'dates': occ_date_range
                , 'series': [
                    {
                        'id': str(skills_ids[i])+'Lowest'+'Salary'
                        , 'name':'Lowest'
                        , 'values': temp_10_salary
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                    , {
                        'id': str(skills_ids[i])+'Low'+'Salary'
                        , 'name':'Low'
                        , 'values': temp_25_salary
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                    , {
                        'id': str(skills_ids[i])+'Middle'+'Salary'
                        , 'name':'Middle'
                        , 'values': temp_median_salary
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                    , {
                        'id': str(skills_ids[i])+'High'+'Salary'
                        , 'name':'High'
                        , 'values': temp_75_salary
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                    , {
                        'id': str(skills_ids[i])+'Highest'+'Salary'
                        , 'name':'Highest'
                        , 'values': temp_90_salary
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                    , {
                        'id': str(skills_ids[i])+'Average'+'Salary'
                        , 'name':'Average'
                        , 'values': temp_mean_salary
                        , 'inferred': [0,0,0,0,0,0,0,0,0,0,0,1,1]
                    }
                ]
            }
        }

        inferred_1 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1]

        temp_hourly_2 = []
        temp_salary_2 = []
        counter = 0
        for x in range(len(xaxis[::-1])):
            if xaxis[::-1][x-1][-4:] != xaxis[::-1][x][-4:]:
                temp_hourly_2.append(temp_mean_hourly[counter])
                temp_salary_2.append(temp_mean_salary[counter])
                counter += 1
            else:
                temp_hourly_2.append(temp_mean_hourly[counter-1])
                temp_salary_2.append(temp_mean_salary[counter-1])

        if subobj.active == True:
            unemployment_rate.append(list(all_skills_data[i][-2]['employment']['unemployment_rate'].values())[:-1][::-1])
            unemployment.append(list(all_skills_data[i][-2]['employment']['unemployment'].values())[:-1][::-1])
            employment.append(list(all_skills_data[i][-2]['employment']['employment'].values())[:-1][::-1])
            labor_force.append(list(all_skills_data[i][-2]['employment']['labor_force'].values())[:-1][::-1])
            bands.append([band_dict])
        else:
            pass

        inferred.append(inferred_1)
        yaxis_hourly.append({'name':skills_names[i], 'data':temp_hourly_2, 'id':skills_ids[i]})
        yaxis_annually.append({'name':skills_names[i], 'data':temp_salary_2, 'id':skills_ids[i]})
        yaxis_cross_ref.append({'name':skills_names[i], 'id':skills_ids[i], 'data':[]})

        ###########
        ### END ###
        ###########

    xaxis = xaxis[::-1] ### Reverse list

    return JsonResponse({
        'xaxis': xaxis
        , 'yaxis_hourly': yaxis_hourly
        , 'yaxis_annually': yaxis_annually
        , 'yaxis_cross_ref': yaxis_cross_ref
        , 'unemployment': unemployment
        , 'unemployment_rate': unemployment_rate
        , 'employment': employment
        , 'labor_force': labor_force
        , 'inferred': inferred
        , 'bands': bands
        , 'check': check
    })



def get_areas_from_state(request, state):
    retval = get_area_from_state_from_db(state)
    return JsonResponse(retval, safe=False)

def get_msa_from_state(request, state):
    retval = get_msa_from_state_from_db(state)
    return JsonResponse(retval, safe=False)

def get_industries_from_area(request, area):
    retval = get_industry_from_area_from_db(area)
    return JsonResponse(retval, safe=False)

def get_industries_from_msa(request, msa):
    retval = get_industry_from_msa_from_db(msa)
    return JsonResponse(retval, safe=False)

def get_occupation_from_msa(request, msa, industry):
    retval = get_occupation_from_msa_from_db(msa, industry)
    return JsonResponse(retval, safe=False)

def get_skills_from_county(request, county):
    retval = get_skills_from_county_from_db(county)
    return JsonResponse(retval, safe=False)

def get_skills_from_msa(request, msa):
    retval = get_skills_from_msa_from_db(msa)
    return JsonResponse(retval, safe=False)



def graph_disco(request, area_id, industry_id, msa_county):
    obj = profilemodel.objects.get(user=request.user)
    subobj = find_sub_obj(obj)

    if subobj.active == False:
        tempno = 40
    else:
        tempno = 48

    xaxis = []
    temp = []
    qtr = 1
    year = 0

    # industry_name = get_industry_title(industry_id)

    date_range = get_date_range(48 - tempno)

    if msa_county == 'county':
        area_name = get_area_title(area_id)
        temp = get_wage_objs_v4(area_id, industry_id)
    else:
        area_name = get_msa_title(area_id)
        temp = get_msa_wage_objs_v5(area_id, industry_id)

    qtr, year = date_range[0][1], date_range[0][0]

    for i in range(tempno):
        xaxis.append('Q{}-{}'.format(qtr,year))
        qtr = qtr - 1
        if qtr == 0:
            qtr = 4
            year = year - 1

    #############
    ### START ###
    #############
    temp_hourly = []
    temp_salary = []
    if tempno == 40:
        retval_annually = temp[3:43]
        retval_hourly = temp[51:91]
    else:
        if temp[98] is not None:
            retval_annually = temp[43:51][::-1] + temp[3:43]
            retval_hourly = temp[91:99][::-1] + temp[51:91]
        else:
            retval_annually = temp[3:43]
            retval_hourly = temp[51:91]

    if temp[98] is not None:
        while len(retval_hourly) < tempno: #minus 8 for two quarters. Cannot make predictions
            retval_hourly.append(None)
            retval_annually.append(None)

        for j in retval_hourly:
            try:
                temp_hourly.append(round(float(j),2))
            except:
                temp_hourly.append(j)

        for h in retval_annually:
            try:
                temp_salary.append(int(h))
            except:
                temp_salary.append(h)
    else:
        for j in retval_hourly:
            try:
                temp_hourly.append(round(float(j),2))
            except:
                temp_hourly.append(j)

        for h in retval_annually:
            try:
                temp_salary.append(int(h))
            except:
                temp_salary.append(h)

        while len(temp_hourly) < tempno:
            temp_hourly.insert(0, None)
            temp_salary.insert(0, None)

    inferred = []
    for j in temp[100].values():
        if j == 0:
            inferred.append(0)
        else:
            inferred.append(1)

    yaxis_hourly = {'name': area_name, 'data': temp_hourly[::-1]}
    yaxis_annually = {'name': area_name, 'data': temp_salary[::-1]}
    # yaxis_cross_ref = {'name': area_name,'id': area_id, 'data': temp[99]}

    ###########
    ### END ###
    ###########
    


    xaxis = xaxis[::-1] ### Reverse list

    # print(yaxis_cross_ref)

    return JsonResponse({
        'xaxis': xaxis
        , 'yaxis_hourly': [yaxis_hourly]
        , 'yaxis_annually': [yaxis_annually]
        # , 'yaxis_cross_ref': yaxis_cross_ref
        # , 'unemployment': unemployment
        # , 'unemployment_rate': unemployment_rate
        # , 'employment': employment
        # , 'labor_force': labor_force
        , 'inferred': [inferred]
    })

def graph_disco_occ(request, area_id, industry_id, msa_county, occupation_id):
    # print(1, request)
    # print(2, area_id)
    # print(3, industry_id)
    # print(4, msa_county)
    # print(5, occupation_id)
    obj = profilemodel.objects.get(user=request.user)
    subobj = find_sub_obj(obj)

    if subobj.active == False:
        tempno = 40
    else:
        tempno = 48

    # print(tempno, '\n')

    xaxis = []
    temp = []
    qtr = 1
    year = 0

    industry = get_industry_clean_code(industry_id)[0]
    # print(industry, '\n')

    date_range = get_date_range_occ()
    # print(date_range, '\n')

    if msa_county == 'county':
        pass
        # area_name = get_area_title(area_id)
        # temp = get_wage_objs_v4(area_id, industry_id)
    else:
        area_name = get_msa_title(area_id)
        temp = get_oews_obj_v1(area_id, industry, occupation_id)

    qtr, year = 1, date_range[0]

    for i in range(len(date_range)):
        xaxis.append('Q1-{}'.format(str(date_range[i][0])[0:4]))

    # print(temp, '\n')

    #############
    ### START ###
    #############
    temp_hourly = []
    temp_salary = []
    if tempno == 40:
        retval_annually = temp[69:80]
        retval_hourly = temp[147:158]
    else:
        retval_annually = temp[69:82]
        retval_hourly = temp[147:160]

    if temp[82] is not None:
        # while len(retval_hourly) < tempno: #minus 8 for two quarters. Cannot make predictions
        #     retval_hourly.append(None)
        #     retval_annually.append(None)

        for j in retval_hourly:
            try:
                temp_hourly.append(round(float(j),2))
            except:
                temp_hourly.append(j)

        for h in retval_annually:
            try:
                temp_salary.append(int(h))
            except:
                temp_salary.append(h)
    else:
        for j in retval_hourly:
            try:
                temp_hourly.append(round(float(j),2))
            except:
                temp_hourly.append(j)

        for h in retval_annually:
            try:
                temp_salary.append(int(h))
            except:
                temp_salary.append(h)

        # while len(temp_hourly) < tempno:
        #     temp_hourly.insert(0, None)
        #     temp_salary.insert(0, None)

    inferred = [0,0,0,0,0,0,0,0,0,0,0,1,1]

    yaxis_hourly = {'name': area_name, 'data': temp_hourly}
    yaxis_annually = {'name': area_name, 'data': temp_salary}
    # yaxis_cross_ref = {'name': area_name,'id': area_id, 'data': temp[99]}

    ###########
    ### END ###
    ###########

    # xaxis = xaxis[::-1] ### Reverse list
    # xaxis = date_range ### Reverse list

    # print(xaxis, '\n')
    # print(yaxis_hourly, '\n')
    # print(yaxis_annually, '\n')
    # print(inferred, '\n')

    # print(yaxis_cross_ref)

    return JsonResponse({
        'xaxis': xaxis
        , 'yaxis_hourly': [yaxis_hourly]
        , 'yaxis_annually': [yaxis_annually]
        # , 'yaxis_cross_ref': yaxis_cross_ref
        # , 'unemployment': unemployment
        # , 'unemployment_rate': unemployment_rate
        # , 'employment': employment
        # , 'labor_force': labor_force
        , 'inferred': [inferred]
    })

def graph_bands(request, area_id, industry_id, msa_county, occupation_id):
    obj = profilemodel.objects.get(user=request.user)
    subobj = find_sub_obj(obj)

    if subobj.active == False:
        tempno = 40
    else:
        tempno = 48

    # print(tempno, '\n')

    xaxis = []
    temp = []
    qtr = 1
    year = 0

    industry = get_industry_code(industry_id)[0]
    # print(industry, '\n')

    date_range = get_date_range_occ()
    # print(date_range, '\n')

    if msa_county == 'county':
        pass
        # area_name = get_area_title(area_id)
        # temp = get_wage_objs_v4(area_id, industry_id)
    else:
        area_name = get_msa_title(area_id)
        temp = get_oews_obj_v1(area_id, industry, occupation_id)

    qtr, year = 1, date_range[0]

    for i in range(len(date_range)):
        xaxis.append('Q1-{}'.format(str(date_range[i][0])[0:4]))

    # print(temp, '\n')

    #############
    ### START ###
    #############
    temp_hourly = []
    temp_salary = []
    if tempno == 40:
        retval_annually = temp[69:80]
        retval_hourly = temp[147:158]
    else:
        retval_annually = temp[69:82]
        retval_hourly = temp[147:160]

    if temp[82] is not None:
        # while len(retval_hourly) < tempno: #minus 8 for two quarters. Cannot make predictions
        #     retval_hourly.append(None)
        #     retval_annually.append(None)

        for j in retval_hourly:
            try:
                temp_hourly.append(round(float(j),2))
            except:
                temp_hourly.append(j)

        for h in retval_annually:
            try:
                temp_salary.append(int(h))
            except:
                temp_salary.append(h)
    else:
        for j in retval_hourly:
            try:
                temp_hourly.append(round(float(j),2))
            except:
                temp_hourly.append(j)

        for h in retval_annually:
            try:
                temp_salary.append(int(h))
            except:
                temp_salary.append(h)

        # while len(temp_hourly) < tempno:
        #     temp_hourly.insert(0, None)
        #     temp_salary.insert(0, None)

    inferred = [0,0,0,0,0,0,0,0,0,0,0,1,1]

    yaxis_hourly = {'name': area_name, 'data': temp_hourly}
    yaxis_annually = {'name': area_name, 'data': temp_salary}
    # yaxis_cross_ref = {'name': area_name,'id': area_id, 'data': temp[99]}

    ###########
    ### END ###
    ###########

    # xaxis = xaxis[::-1] ### Reverse list
    # xaxis = date_range ### Reverse list

    # print(xaxis, '\n')
    # print(yaxis_hourly, '\n')
    # print(yaxis_annually, '\n')
    # print(inferred, '\n')

    # print(yaxis_cross_ref)

    return JsonResponse({
        'xaxis': xaxis
        , 'yaxis_hourly': [yaxis_hourly]
        , 'yaxis_annually': [yaxis_annually]
        # , 'yaxis_cross_ref': yaxis_cross_ref
        # , 'unemployment': unemployment
        # , 'unemployment_rate': unemployment_rate
        # , 'employment': employment
        # , 'labor_force': labor_force
        , 'inferred': [inferred]
    })



def graph_disco_create(request, area_id, skills):
    # print(area_id, skills, '\n')
    obj = profilemodel.objects.get(user=request.user)
    subobj = find_sub_obj(obj)

    if subobj.active == False:
        tempno = 40
    else:
        tempno = 48

    # print(tempno, '\n')

    xaxis = []
    temp = []
    qtr = 1
    year = 0

    # industry = get_industry_clean_code(industry_id)[0]
    # print(industry, '\n')

    date_range = get_date_range_occ()
    # print(date_range, '\n')

    area_name = get_msa_title(area_id)
    # print(area_name, '\n')
    # temp = get_oews_obj_v1(area_id, industry, occupation_id)

    dataset_id = get_msa_wage_objs_skills_v1(area_id, skills, obj.user_id)
    # print(dataset_id, '\n')

    temp = get_msa_wage_objs_skills_only_data_v1(dataset_id)
    # print(temp, '\n')

    qtr, year = 1, date_range[0]

    for i in range(len(date_range)):
        xaxis.append('Q1-{}'.format(str(date_range[i][0])[0:4]))

    #############
    ### START ###
    #############
    temp_hourly = []
    temp_salary = []
    if tempno == 40:
        retval_annually = temp[69:80]
        retval_hourly = temp[147:158]
    else:
        retval_annually = temp[69:82]
        retval_hourly = temp[147:160]

    if temp[82] is not None:
        # while len(retval_hourly) < tempno: #minus 8 for two quarters. Cannot make predictions
        #     retval_hourly.append(None)
        #     retval_annually.append(None)

        for j in retval_hourly:
            try:
                temp_hourly.append(round(float(j),2))
            except:
                temp_hourly.append(j)

        for h in retval_annually:
            try:
                temp_salary.append(int(h))
            except:
                temp_salary.append(h)
    else:
        for j in retval_hourly:
            try:
                temp_hourly.append(round(float(j),2))
            except:
                temp_hourly.append(j)

        for h in retval_annually:
            try:
                temp_salary.append(int(h))
            except:
                temp_salary.append(h)

        # while len(temp_hourly) < tempno:
        #     temp_hourly.insert(0, None)
        #     temp_salary.insert(0, None)

    inferred = [0,0,0,0,0,0,0,0,0,0,0,1,1]

    yaxis_hourly = {'name': area_name, 'data': temp_hourly}
    yaxis_annually = {'name': area_name, 'data': temp_salary}
    # yaxis_cross_ref = {'name': area_name,'id': area_id, 'data': temp[99]}

    ###########
    ### END ###
    ###########

    # xaxis = xaxis[::-1] ### Reverse list
    # xaxis = date_range ### Reverse list

    # print(xaxis, '\n')
    # print(yaxis_hourly, '\n')
    # print(yaxis_annually, '\n')
    # print(inferred, '\n')

    # print(yaxis_cross_ref)

    return JsonResponse({
        'xaxis': xaxis
        , 'yaxis_hourly': [yaxis_hourly]
        , 'yaxis_annually': [yaxis_annually]
        # , 'yaxis_cross_ref': yaxis_cross_ref
        # , 'unemployment': unemployment
        # , 'unemployment_rate': unemployment_rate
        # , 'employment': employment
        # , 'labor_force': labor_force
        , 'inferred': [inferred]
    })