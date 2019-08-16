import simplejson as json
import matplotlib
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
import base64
from collections import OrderedDict
import mock
# import pandas as pd


def get_medicine_schedule(medicine_list):
    print "get medicine list: ", medicine_list

    ordered_time1 = OrderedDict()
    ordered_time1["before"] = list()
    ordered_time1["after"] = list()
    ordered_time1["bed"] = list()

    ordered_time2 = OrderedDict()
    ordered_time2["before"] = list()
    ordered_time2["after"] = list()
    ordered_time2["bed"] = list()

    ordered_time3 = OrderedDict()
    ordered_time3["before"] = list()
    ordered_time3["after"] = list()
    ordered_time3["bed"] = list()

    usage = OrderedDict()
    usage["morning"] = ordered_time1
    usage["noon"] = ordered_time2
    usage["evening"] = ordered_time3
    usage["bedtime"] = []

    for med in medicine_list:
        for key in med:
            for meal in (med.get(key).get("med_meal")).split():
                for times in (med.get(key).get("times_daily")).split():
                    title = med.get(key).get("title")
                    if meal == 'bedtime':
                        if not title in usage.get("bedtime"):
                            usage.get("bedtime").append(title)
                    elif times == 'before':
                        usage.get(meal).get("before").append(title)
                    elif times == 'after':
                        usage.get(meal).get("after").append(title)

    return usage


def get_all_medicine_title(medicine_list):
    lists = []
    for med in medicine_list:
        lists.append(
            {"medId": med, "title": medicine_list.get(med).get("title")})

    return lists


def get_medicine_bykey(_id):
    return mock.get_all_medicine().get(_id)


def generate_info_nutrient_linechart(data, minValue, maxValue, begin, amount):
    dic = {}
    _list = []
    last_date = ''
    dateList = sorted(data.keys())
    dic['date'] = []
    dic['points'] = []
    dic['min'] = []
    dic['max'] = []
    i = 0
    _amount = amount
    for date in dateList:
        _formatted_date = dt.datetime.strptime(date, "%Y-%m-%d")
        while i < _amount:
            _date = begin + dt.timedelta(days=i)
            if _formatted_date != _date:
                dic.get('date').append(_date.strftime("%Y-%m-%d"))
                dic.get('points').append(0)
                dic.get('min').append(minValue)
                dic.get('max').append(maxValue)
                i += 1
            else:
                break
        last_date = dt.datetime.strptime(date, "%Y-%m-%d")
        dic.get('date').append(date)
        dic.get('points').append(data.get(date))
        dic.get('min').append(minValue)
        dic.get('max').append(maxValue)
        i += 1
    while i < _amount:
        _date = last_date + dt.timedelta(days=i)
        dic.get('date').append(_date.strftime("%Y-%m-%d"))
        dic.get('points').append(0)
        dic.get('min').append(minValue)
        dic.get('max').append(maxValue)
        i += 1

    _list.append(dic)

    return _list


def generate_info_result_linechart(data):
    _data = data
    _list = []
    for item in data:
        dic = {}
        dic['title'] = item
        dateList = sorted(_data[item].keys())
        dic['date'] = dateList
        dic['limits'] = []
        dic['points'] = []
        for date in dateList:
            arr = np.array((_data[item].get(date).split(',')))
            value = arr.astype(np.float)
            dic.get('points').append(value[0])
            dic.get('limits').append(value[1])
        _list.append(dic)

    return _list


def generate_info_exercise_barchart(data):
    _data = data
    _list = []
    for item in data:
        dic = {}
        dic['title'] = item
        dateList = sorted(_data[item].keys())
        dic['date'] = dateList
        dic['goal'] = []
        dic['points'] = []
        for date in dateList:
            arr = np.array((_data[item].get(date).split(',')))
            value = arr.astype(np.float)
            dic.get('points').append(value[0])
            dic.get('goal').append(value[1])
        _list.append(dic)

    return _list


def generate_key_value_appointment(data_dic):
    data_list = []
    for item in list(data_dic):
        data = {}
        for key in item:
            data['date'] = key.split('_')[2]
            data['description'] = item[key]['treatment']['appointment']
            data_list.append(data)

    return data_list


def get_nutrients_minmax(limit_list):
    result = {}
    for key in limit_list:
        maxValue = limit_list.get(key).get("maxVal")
        minValue = limit_list.get(key).get("minVal")
        result[key] = {"maxValue": maxValue, "minValue": minValue}

    return result


def summary_per_day(result, columnFamily):
    dic = {}
    for item in list(result):
        for key in item:
            splitKey = (item[key].get(columnFamily))
            for d in splitKey:
                if dic.has_key(d):
                    dic[d] += float(splitKey[d])
                else:
                    dic[d] = 0
                    dic[d] += float(splitKey[d])

    return dic


def group_by_key(result, columnFamily):
    dic = {}
    print result
    for item in list(result):
        for key in item:
            title = item.get(key).get(columnFamily).keys()[0]
            value = item.get(key).get(columnFamily).get(title)
            # splitKey -> date
            date = key.split('_')[2]

            if title in dic:
                dic[title].update({date: value})
            else:
                dic[title] = {date: value}

    return dic


def get_value(item, key, columnFamily, title):
    value = item.get(key).get(columnFamily).get(title)
    return float(value.split(',')[0])


def get_limit(item, key, columnFamily, title):
    limit = (item.get(key).get(columnFamily).get(title)).split(',')
    if len(limit) == 1:
        return None
    else:
        return limit[1]


def summary_by_date(result, columnFamily, title):
    _result = list(result)
    dic = {}
    summary = 0.0
    flag = ''
    state = 0
    for item in _result:
        for key in item:
            if item.get(key).get(columnFamily).get(title):
                splitKey = key.split('_')[2]
                if(flag != '' and flag != splitKey):
                    state = 2
                if(state == 0):
                    flag = splitKey
                    summary += get_value(item, key, columnFamily, title)
                    state = 1
                elif(state == 1):
                    summary += get_value(item, key, columnFamily, title)
                elif(state == 2):
                    limit = get_limit(item, key, columnFamily, title)
                    if limit:
                        dic["{}".format(flag)] = str(
                            summary) + ',' + str(limit)
                    else:
                        dic["{}".format(flag)] = summary
                    flag = splitKey
                    summary = 0.0
                    summary += get_value(item, key, columnFamily, title)
                    state = 1

        if item.get(key).get(columnFamily).get(title):
            limit = get_limit(item, key, columnFamily, title)
            if limit:
                dic["{}".format(flag)] = str(summary) + ',' + str(limit)
            else:
                dic["{}".format(flag)] = summary

    return dic
# dic
# {
#     "2016-11-09": 60.0,
#     "2016-11-12": 45.0,
#     "2016-11-13": 55.0,
#     "2016-11-10": 66.0,
#     "2016-11-11": 55.0,
#     "2016-11-14": 60.0,
#     "2016-11-15": 60.0
# }


def generate_date_value_list(data_dic, begin, amount):
    dic = data_dic if data_dic else data_dic.append({})
    graphDate = []
    value = []
    date_value = []
    i = 0
    _amount = amount
    last_date = ''

    for key in sorted(dic):
        date = dt.datetime.strptime(key, "%Y-%m-%d")
        while i < _amount:
            _date = begin + dt.timedelta(days=i)

            if date != _date:
                graphDate.append(_date)
                value.append(0)
                i += 1
            else:
                break
        last_date = date
        graphDate.append(date)
        value.append(dic.get(key))
        i += 1

    while i < _amount:
        _date = last_date + dt.timedelta(days=i)
        graphDate.append(_date)
        value.append(0)
        i += 1

    date_value.append(graphDate)
    date_value.append(value)
    return date_value


def generate_linechart_img(title, date_list, value_list, xlabel, ylabel, chart_title, maxValue, minValue, amount):
    img_path = 'img/value-{}.png'.format(title)
    encoded_string = ""

    x = np.array(range(0, amount))
    y = np.array(value_list)

    my_xticks = [date.strftime("%b %d, %y") for date in date_list]

    plt.xticks(x, my_xticks, rotation=25, fontsize=12)
    plt.yticks(y, fontsize=12)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.tight_layout()

    plt.title(chart_title)
    # plt.title("sodium (min: {}, max: {})".format(minValue, maxValue))
    plt.fill_between(x, minValue, maxValue, facecolor='#C8FFDA')
    # plt.tight_layout()
    lines = plt.plot(x, y)
    plt.setp(lines, linewidth=5, color="#7CAFE6")
    plt.savefig('img/value-{}.png'.format(title))
    plt.clf()

    return img_path


# def generate_activity1_linechart_img(filename, raw_data):
#     # transform raw_data to data format
#     # data = {
#     #     'date': ['2017-09-11', '2017-09-11', '2017-09-12'],
#     #     'time': ['09:15:28', '13:15:28', '08:15:28'],
#     #     'max_level': [2, 4, 5]
#     # }

#     img_path = 'img/value-{}.png'.format(filename)
#     t = 'Result from ' + raw_data['date'][0] + ' to ' + raw_data['date'][-1]
#     df = pd.DataFrame(raw_data)

#     df.plot(x=['date', 'time'], rot=0, title=t, marker='o', linestyle='--')
#     plt.xlabel('date')
#     plt.ylabel('Max Level (0-10)')
#     plt.ylim([0, 10])
#     plt.show()

#     plt.savefig('img/value-{}.png'.format(filename))
#     plt.clf()
#     return img_path
