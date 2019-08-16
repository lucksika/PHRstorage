import io
from flask import Flask, request, jsonify, json, send_file
from flask_cors import CORS, cross_origin
import starbase
import datetime as dt
# from dateutil.relativedelta import *
import dateutil.relativedelta as relativedelta
import calendar
import numpy as np
import base64

import manager
import service
import mock

app = Flask(__name__)
# app.config["JSON_SORT_KEYS"] = False
CORS(app)

#
# connect HBase
table_nutrient = 'nutrients'
table_result = 'results'
table_information = 'information'
table_exercise = 'exercise'
table_medicines = 'medicines'
table_activity_results_1 = 'activity_results_1'
table_activity_results_2 = 'activity_results_2'
table_hospital = "hospitals"
table_surgery = "surgeries"
table_patient_code = "patient_code"
table_pin_code = "pin_code"


@app.route('/')
@cross_origin
#######
# Nutrient
#######
@app.route('/nutrient/meal', methods=['GET', 'POST'])
def nutrientdata():
    if request.method == 'POST':
        obj = request.json
        print json.dumps(obj, indent=4, separators=(',', ': '))
        userid = obj.get("userid")
        appid = obj.get("appid")
        nutrients = obj.get("nutrients")
        date = obj.get("date")
        meal = obj.get("meal")

        rowkey = userid + "_" + appid + "_" + date + "_" + meal

        data = {}
        data['nutrient'] = nutrients

        manager.save_batch(table_nutrient, rowkey, data)

        # print json.dumps(obj, indent=4, separators=(',', ': '))
        return jsonify(success="true")

    if request.method == 'GET':
        userid = request.args.get("userid")
        appid = request.args.get("appid")
        date = request.args.get("date")
        meal = request.args.get("meal")

        rowkey = userid + "_" + appid + "_" + date + "_" + meal

        data = manager.fetch(table_nutrient, rowkey)

        # print data
    return jsonify(data=data)

    return jsonify(success="true")


@app.route('/nutrient/chart/image', methods=['GET', 'POST'])
def nutrientImage():
    maxDateAmount = 7
    userid = ''
    appid = ''
    string_date = ''
    title = ''
    amount = 0
    result = ''

    if request.method == 'GET':
        userid = request.args.get("userid")
        appid = request.args.get("appid")
        string_date = request.args.get("date")
        title = request.args.get("title")
        amount = int(request.args.get("amount")
                     ) if request.args.get("amount") else 0
        amount = (amount if amount < maxDateAmount and amount >
                  0 else maxDateAmount) + 1

    elif request.method == 'POST':
        obj = request.json

        userid = obj.get("userid")
        appid = obj.get("appid")
        title = obj.get("title")
        string_date = obj.get("date")
        amount = int(obj.get("amount")) if obj.get("amount") else 0
        amount = (amount if amount < maxDateAmount and amount >
                  0 else maxDateAmount) + 1

    # print amount
    end = dt.datetime.strptime(string_date, "%Y-%m-%d")
    end = end + dt.timedelta(days=1)

    columnFamily = "nutrient"
    limit = mock.get_nutrient_limit()
    maxValue = limit.get(title).get("maxVal")
    minValue = limit.get(title).get("minVal")
    # start row - end row
    begin = end - dt.timedelta(days=(amount))
    # date = begin.strftime("%Y-%m-%d")
    # print appid
    # print userid
    start_row = base64.b64encode("{}_{}_{}_".format(userid, appid, begin))
    end_row = base64.b64encode("{}_{}_{}_".format(userid, appid, end))
    column = base64.b64encode("{}:{}".format(columnFamily, title))

    result = list(manager.fetch_part(
        table_nutrient, start_row, end_row, column))

    if not result:
        return jsonify(nodata="no data")
    # print json.dumps(list(result), indent=4, separators=(',', ': '))

    dic = service.summary_by_date(result, columnFamily, title)
    # print json.dumps(dic, indent=4, separators=(',', ': '))

    date_value_list = service.generate_date_value_list(dic, begin, amount)
    date_list = date_value_list[0]
    value_list = date_value_list[1]
    chart_title = "{} (min: {}, max: {})".format(title, minValue, maxValue)
    # print date_value_list
    img_path = service.generate_linechart_img(
        title, date_list, value_list, "Date", "Value (g/day)", chart_title, maxValue, minValue, amount)

    with open(img_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    return jsonify(image=encoded_string)
    # return send_file(img_path, mimetype='image/png')
    # return "ok"

    return jsonify(success="true")


@app.route('/nutrient/chart/progress', methods=['GET'])
def nutrientProgress():
    userid = request.args.get("userid")
    appid = request.args.get("appid")
    # end = dt.datetime.now()
    string_date = request.args.get("date")
    begin = dt.datetime.strptime(string_date, "%Y-%m-%d")

    columnFamily = "nutrient"

    if request.method == 'GET':
        # start row - end row
        end = begin + dt.timedelta(days=1)
        # print begin
        # print end
        start_row = base64.b64encode("{}_{}_{}_".format(userid, appid, begin))
        end_row = base64.b64encode("{}_{}_{}_".format(userid, appid, end))

        result = manager.fetch_part(table_nutrient, start_row, end_row)

        data = service.summary_per_day(result, columnFamily)
        limit = service.get_nutrients_minmax(mock.get_nutrient_limit())
        # print limit

        return jsonify(data=data, limit=limit)


@app.route('/nutrient/chart/points', methods=['GET'])
def chartnutrient():
    maxDateAmount = 7
    if request.method == 'GET':
        userid = request.args.get("userid")
        appid = request.args.get("appid")
        string_date = request.args.get("date")
        title = request.args.get("title")
        amount = int(request.args.get("amount")
                     ) if request.args.get("amount") else 0
        amount = (amount if amount < maxDateAmount and amount >
                  0 else maxDateAmount) + 1
        # print amount

        end = dt.datetime.strptime(string_date, "%Y-%m-%d")
        end = end + dt.timedelta(days=1)

        columnFamily = "nutrient"
        limit = mock.get_nutrient_limit()
        maxValue = limit.get(title).get("maxVal")
        minValue = limit.get(title).get("minVal")
        # start row - end row
        begin = end - dt.timedelta(days=(amount))
        # date = begin.strftime("%Y-%m-%d")

        start_row = base64.b64encode("{}_{}_{}_".format(userid, appid, begin))
        end_row = base64.b64encode("{}_{}_{}_".format(userid, appid, end))
        column = base64.b64encode("{}:{}".format(columnFamily, title))

        result = list(manager.fetch_part(
            table_nutrient, start_row, end_row, column))
        # print result
        if not result:
            return jsonify(nodata="no data")
        # print json.dumps(list(result), indent=4, separators=(',', ': '))

        dic = service.summary_by_date(result, columnFamily, title)
        data_chart = service.generate_info_nutrient_linechart(
            dic, minValue, maxValue, begin, amount)

        return jsonify(chart=data_chart)
#######
# Result
#######


@app.route('/result/chart/points', methods=['GET'])
def chartpoint():
    if request.method == 'GET':
        userid = request.args.get("userid")
        appid = request.args.get("appid")
        year = request.args.get("year")
        month = request.args.get("month")
        amount = request.args.get("amount")
        title = request.args.get("title")

        # print title
        _, last_day = calendar.monthrange(int(year), int(month))
        end = dt.datetime.strptime(
            year + '-' + month + '-' + str(last_day), "%Y-%m-%d")
        begin = end + relativedelta(months=-int(amount))

        start_row = base64.b64encode("{}_{}_{}".format(userid, appid, begin))
        end_row = base64.b64encode("{}_{}_{}".format(userid, appid, end))

        if not title:
            data = manager.fetch_part(table_result, start_row, end_row)
        else:
            column = base64.b64encode("testresults:" + title)
            data = manager.fetch_part(table_result, start_row, end_row, column)

        result = service.group_by_key(data, 'testresults')
        info_linechart = service.generate_info_result_linechart(result)

        # points = [0.5, 0.8, 1.2, 1.5, 1.7, 2.0, 1.8]
        # dates = ["2015-03-20", "2015-04-18", "2015-05-22", "2015-06-21", "2015-07-20"]
        # dates = ["January", "February", "March", "April", "May", "June", "July"]
        # lastcheck = "2015-12-25"
        # limit = 1.5
        # unit = "mg/dL"
        # print list(data)
        # print json.dumps(list(data), indent=4, separators=(',', ': '))
        # encode to JSON and get value of parameter "view_type"
        # print (json.loads(obj)).get("view_type")
        # return jsonify(points=points,dates=dates,lastcheck=lastcheck,limit=limit,unit=unit)
        # return jsonify(success="true")
        return jsonify(chart=info_linechart, data=result)


@app.route('/result/info', methods=['GET', 'POST'])
def resultdata():
    if request.method == 'POST':
        obj = request.json

        userid = obj.get("userid")
        appid = obj.get("appid")
        date = obj.get("date")
        labresult = obj.get("result")

        title = labresult.get("title")
        value = labresult.get("value")
        limit = labresult.get("limit")

        rowkey = userid + "_" + appid + "_" + date
        _value = str(value) + ',' + str(limit)

        # print json.dumps(obj, indent=4, separators=(',', ': '))

        manager.insert_data(table_result, rowkey, 'testresults', title, _value)

        return jsonify(success="true")
    elif request.method == 'GET':
        # not use this condition
        # data = {}
        # column = base64.b64encode("{}:{}".format('activity', title))
        # result = manager.fetch_part(table_exercise, start_row, end_row, column)
        # data[title] = service.summary_by_date(result, 'activity', title)
        data = manager.fetch(table_result, 'lucksika_display01_2017-01-26')
        # print data
        # print type(data)
        title = 'BUN'
        value = 1.2
        limit = 1.5
        check_date = '2015-12-23'
        return jsonify(title=title, value=value, limit=limit, check_date=check_date)


@app.route('/result/water', methods=['GET'])
def water():
    maxDateAmount = 7
    userid = request.args.get("userid")
    appid = request.args.get("appid")
    string_date = request.args.get("date")

    amount = request.args.get("amount")
    amount = int(amount)
    amount = (amount if amount < maxDateAmount and amount >
              0 else maxDateAmount)

    end = dt.datetime.strptime(string_date, "%Y-%m-%d")
    end = end + dt.timedelta(days=1)
    begin = end - dt.timedelta(days=(amount))

    start_row = base64.b64encode("{}_{}_{}_".format(userid, appid, begin))
    end_row = base64.b64encode("{}_{}_{}_".format(userid, appid, end))

    data = {}
    column = base64.b64encode("{}:{}".format('water', 'water'))
    result = manager.fetch_part(table_exercise, start_row, end_row, column)
    data['water'] = service.summary_by_date(result, 'water', 'water')

    chart = service.generate_info_exercise_barchart(data)

    return jsonify(data=data, chart=chart)

#######
# Information
#######


@app.route('/appointment/info', methods=['GET', 'POST'])
def appointment():
    if request.method == 'POST':
        obj = request.json

        userid = obj.get("userid")
        appid = obj.get("appid")
        date = obj.get("date")

        description = json.dumps(obj.get("description"), ensure_ascii=False)

        rowkey = userid + "_" + appid + "_" + date

        manager.insert_data(table_information, rowkey,
                            'treatment', 'appointment', description)

        # print json.dumps(obj, indent=4, separators=(',', ': '))
        return jsonify(success="true")

    elif request.method == 'GET':
        userid = request.args.get("userid")
        appid = request.args.get("appid")
        month = request.args.get("month")
        year = request.args.get("year")

        begin = year + '-' + month + '-01'
        end = year + '-' + month + '-31'

        print "===> begin ; ", begin
        print "===> end ; ", end
        start_row = base64.b64encode("{}_{}_{}".format(userid, appid, begin))
        end_row = base64.b64encode("{}_{}_{}".format(userid, appid, end))
        column = base64.b64encode("treatment:appointment")

        data = manager.fetch_part(
            table_information, start_row, end_row, column)

        data_json = service.generate_key_value_appointment(data)

        return jsonify(data=data_json)


@app.route('/profile/info', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        obj = request.json

        userid = obj.get("userid")
        appid = obj.get("appid")
        profile = obj.get("profile")

        data = {}
        data['profile'] = profile

        # print data

        rowkey = userid + "_" + appid

        manager.save_batch(table_information, rowkey, data)

        return jsonify(success="true")

    elif request.method == 'GET':
        userid = request.args.get("userid")
        appid = request.args.get("appid")

        rowkey = userid + "_" + appid
        column = 'profile'

        data = manager.fetch(table_information, rowkey, column)

        return jsonify(data=data)

#######
# Exercise
#######


@app.route('/exercise/info', methods=['GET', 'POST'])
def exercise():
    if request.method == 'POST':
        obj = request.json
        activity = obj.get("activity")
        result = obj.get("result")
        columnFamily = ""
        # print request

        userid = obj.get("userid")
        appid = obj.get("appid")
        date = obj.get("date")

        if result != None:
            title = result.get("title")
            value = result.get("value")
            goal = result.get("limit")
            columnFamily = 'water'

        elif activity != None:
            title = activity.get("title")
            value = activity.get("value")
            goal = activity.get("goal")
            columnFamily = 'activity'

        time = dt.datetime.now().strftime("%H:%M:%S")

        rowkey = userid + "_" + appid + "_" + date + "_" + time
        _value = str(value) + ',' + str(goal)

        manager.insert_data(table_exercise, rowkey,
                            columnFamily, title, _value)

        # print json.dumps(obj, indent=4, separators=(',', ': '))

        return jsonify(success="true")

    elif request.method == 'GET':
        maxDateAmount = 7
        userid = request.args.get("userid")
        appid = request.args.get("appid")
        title = request.args.get("title")
        string_date = request.args.get("date")
        amount = request.args.get("amount")
        amount = int(amount)
        amount = (amount if amount < maxDateAmount and amount >
                  0 else maxDateAmount) + 2

        end = dt.datetime.strptime(string_date, "%Y-%m-%d")
        end = end + dt.timedelta(days=1)
        begin = end - dt.timedelta(days=(amount))

        start_row = base64.b64encode("{}_{}_{}_".format(userid, appid, begin))
        end_row = base64.b64encode("{}_{}_{}_".format(userid, appid, end))
        column = base64.b64encode("activity")

        if not title:
            result = manager.fetch_part(
                table_exercise, start_row, end_row, column)
            _result = list(result)
            keys = service.group_by_key(_result, "activity").keys()
            data = {}
            for _title in keys:
                data[_title] = service.summary_by_date(
                    _result, 'activity', _title)

        else:
            data = {}
            column = base64.b64encode("{}:{}".format('activity', title))
            result = manager.fetch_part(
                table_exercise, start_row, end_row, column)
            data[title] = service.summary_by_date(result, 'activity', title)

        chart = service.generate_info_exercise_barchart(data)

        return jsonify(chart=chart, data=data)

#######
# Medicine
#######


@app.route('/medicine/list', methods=['GET'])
def medicine_list():
    if request.method == 'GET':
        med_list = service.get_all_medicine_title(mock.get_all_medicine())

        return jsonify(list=med_list)


@app.route('/medicine/info', methods=['GET', 'POST', 'DELETE'])
def medicine():
    if request.method == 'POST':
        obj = request.json

        userid = obj.get("userid")
        appid = obj.get("appid")
        medicine = obj.get("medicine")
        med_id = obj.get("medId")
        desc = service.get_medicine_bykey(med_id)
        side_effect = desc.get("side_effect")
        title = desc.get("title")

        rowkey = userid + "_" + appid + "_" + med_id

        data = {}
        data['medicine'] = medicine
        data['medicine']['title'] = title
        data['medicine']['side_effect'] = side_effect

        manager.save_batch(table_medicines, rowkey, data)

        # print json.dumps(obj, indent=4, separators=(',', ': '))

        return jsonify(success="true")
    elif request.method == 'GET':  # get all current use medicine
        userid = request.args.get("userid")
        appid = request.args.get("appid")

        start_row = base64.b64encode("{}_{}".format(userid, appid))
        # start_row <= key < end_row //must have end_row use x to ended the key
        end_row = base64.b64encode("{}_{}x".format(userid, appid))

        desc = manager.fetch_from(table_medicines, start_row, end_row)
        desc_list = list(desc)
        desc_value = []
        for key in desc_list:
            for x in key:
                desc_value.append(key.get(x))

        schedule = service.get_medicine_schedule(desc_list)

        return jsonify(data=list(schedule.items()), desc=desc_value)

    elif request.method == 'DELETE':
        userid = request.args.get("userid")
        appid = request.args.get("appid")
        med_id = request.args.get('medId')

        rowkey = userid + "_" + appid + "_" + med_id

        manager.delete_row(table_medicines, rowkey)

        return jsonify(success="true")
        # return jsonify(data=list(), desc=desc_list)

###
# Import data
###


# API for sending only 1 person/time: loop
@app.route('/import/profile', methods=['POST'])
def import_profile():
    if request.method == 'POST':
        obj = request.json

        persons = obj

        for userid_appid, profile in persons.items():
            words = userid_appid.split('_')
            userid = words[0]
            appid = words[1]

            data = {}
            data['profile'] = profile

            rowkey = userid + "_" + appid
            manager.save_batch(table_information, rowkey, data)

        return jsonify(success="true")
    else:
        return jsonify(success="false")


# API for sending only 1 appointment/time: loop
@app.route('/import/appointment', methods=['POST'])
def import_appointment():
    if request.method == 'POST':
        obj = request.json

        appointments = obj

        for userid_appid_date, data in appointments.items():
            words = userid_appid_date.split('_')
            userid = words[0]
            appid = words[1]
            date = words[2]

            description = json.dumps(data['description'], ensure_ascii=False)

            rowkey = userid + "_" + appid + "_" + date

            manager.insert_data(table_information, rowkey,
                                'treatment', 'appointment', description)

        return jsonify(success="true")
    else:
        return jsonify(success="false")


# API for get/post activity result in phase 1
@app.route('/activity_result/1', methods=['GET', 'POST', 'DELETE'])
def activity_result_1():
    if request.method == 'POST':
        obj = request.json
        userid = obj.get("userid")
        appid = obj.get("appid")
        date = obj.get("date")
        time = obj.get("time")
        results = obj.get("results")

        rowkey = userid + "_" + appid + "_" + date + "_" + time

        data = {}
        data['activity_result_1'] = results

        manager.save_batch(table_activity_results_1, rowkey, data)

        return jsonify(success="true")

    elif request.method == 'GET':
        userid = request.args.get("userid")
        appid = request.args.get("appid")
        begin = request.args.get("start_date")  # "2017-09-11"
        end = request.args.get("end_date")  # 2017-09-15

        # Get data

        end = dt.datetime.strptime(end, "%Y-%m-%d")
        end = end + dt.timedelta(days=1)

        start_row = base64.b64encode("{}_{}_{}_".format(userid, appid, begin))
        end_row = base64.b64encode("{}_{}_{}_".format(userid, appid, end))

        desc = manager.fetch_from(
            table_activity_results_1, start_row, end_row)

        desc_list = list(desc)

        return jsonify(data=desc_list)

    elif request.method == 'DELETE':
        userid = request.args.get("userid")
        appid = request.args.get("appid")
        date = request.args.get("date")
        time = request.args.get("time")

        rowkey = userid + "_" + appid + "_" + date + "_" + time

        manager.delete_row(table_activity_results_1, rowkey)

        return jsonify(success="true")

# ################################# Get image

#         r_date = []
#         r_time = []
#         r_max_level = []

#         for userid_appid_date_time, activity_result in desc_list.items():
#             words = userid_appid_date_time.split('_')
#             userid = words[0]
#             appid = words[1]
#             date = words[2]
#             time = words[3]

#             r_date.append(date)
#             r_time.append(time)
#             r_max_level.append(activity_result['activity_result_1'].max_level)

#         raw_data = {
#           'date': r_date,
#           'time': r_time,
#           'max_level': r_max_level
#         }

#         filename = r_date[0] + '_' + r_date[-1]
#         img_path = service.generate_activity1_linechart_img(filename, raw_data)

#         with open(img_path, "rb") as image_file:
#             encoded_string = base64.b64encode(image_file.read())

#         return jsonify(data=desc_list, image=encoded_string)


# API for get/post activity result in phase 2
@app.route('/activity_result/2', methods=['GET', 'POST', 'DELETE'])
def activity_result_2():
    if request.method == 'POST':
        obj = request.json
        userid = obj.get("userid")
        appid = obj.get("appid")
        date = obj.get("date")
        time = obj.get("time")
        results = obj.get("results")

        rowkey = userid + "_" + appid + "_" + date + "_" + time

        data = {}
        data['activity_result_2'] = results

        manager.save_batch(table_activity_results_2, rowkey, data)

        return jsonify(success="true")

    elif request.method == 'GET':
        userid = request.args.get("userid")
        appid = request.args.get("appid")
        begin = request.args.get("start_date")  # "2017-09-11"
        end = request.args.get("end_date")  # 2017-09-15

        end = dt.datetime.strptime(end, "%Y-%m-%d")
        end = end + dt.timedelta(days=1)

        start_row = base64.b64encode("{}_{}_{}_".format(userid, appid, begin))
        end_row = base64.b64encode("{}_{}_{}_".format(userid, appid, end))

        desc = manager.fetch_from_with_row_id(
            table_activity_results_2, start_row, end_row)

        desc_list = list(desc)

        return jsonify(data=desc_list)

    elif request.method == 'DELETE':
        userid = request.args.get("userid")
        appid = request.args.get("appid")
        date = request.args.get("date")
        time = request.args.get("time")

        rowkey = userid + "_" + appid + "_" + date + "_" + time

        manager.delete_row(table_activity_results_2, rowkey)

        return jsonify(success="true")


# API for sending only 1 actitity/time: loop
@app.route('/import/activity_result/1', methods=['POST'])
def import_activity_result_1():
    if request.method == 'POST':
        obj = request.json
        activity_results = obj

        for userid_appid_date_time, activity_result in activity_results.items():
            words = userid_appid_date_time.split('_')
            userid = words[0]
            appid = words[1]
            date = words[2]
            time = words[3]

            rowkey = userid + "_" + appid + "_" + date + "_" + time

            data = {}
            data['activity_result_1'] = activity_result['results']

            manager.save_batch(table_activity_results_1, rowkey, data)
        return jsonify(success="true")
    else:
        return jsonify(success="false")


# API for sending only 1 actitity/time: loop
@app.route('/import/activity_result/2', methods=['POST'])
def import_activity_result_2():
    if request.method == 'POST':
        obj = request.json
        activity_results = obj

        for userid_appid_date_time, activity_result in activity_results.items():
            words = userid_appid_date_time.split('_')
            userid = words[0]
            appid = words[1]
            date = words[2]
            time = words[3]

            rowkey = userid + "_" + appid + "_" + date + "_" + time

            data = {}
            data['activity_result_2'] = activity_result['results']

            manager.save_batch(table_activity_results_1, rowkey, data)
        return jsonify(success="true", data=data)
    else:
        return jsonify(success="false")


# API for get/post hospital information
@app.route('/hospital/info', methods=['GET', 'POST'])
def hospital():
    if request.method == 'POST':
        obj = request.json
        hospitalid = obj.get("hospitalid")
        information = obj.get("information")
        data = {}
        data['information'] = information

        rowkey = hospitalid
        manager.save_batch(table_hospital, rowkey, data)

        return jsonify(success="true")

    elif request.method == 'GET':
        hospitalid = request.args.get("hospitalid")
        rowkey = hospitalid
        column = 'information'
        data = manager.fetch(table_hospital, rowkey, column)

        return jsonify(data=data)


# API for sending only 1 hospital/time: loop
@app.route('/import/hospital', methods=['POST'])
def import_hospital():
    if request.method == 'POST':
        obj = request.json

        hospitals = obj

        for hospitalid, information in hospitals.items():
            data = {}
            data['information'] = information

            rowkey = hospitalid
            manager.save_batch(table_hospital, rowkey, data)

        return jsonify(success="true")
    else:
        return jsonify(success="false")


# API for get/post surgery information
@app.route('/surgery/info', methods=['GET', 'POST', 'DELETE'])
def surgery():
    if request.method == 'POST':
        obj = request.json
        userid = obj.get("userid")
        hospitalid = obj.get("hospitalid")
        date = obj.get("date")
        time = obj.get("time")
        information = obj.get("information")

        data = {}
        data['information'] = information

        rowkey = userid + "_" + hospitalid + "_" + date + "_" + time
        manager.save_batch(table_surgery, rowkey, data)

        return jsonify(success="true")

    elif request.method == 'GET':
        userid = request.args.get("userid")

        start_row = base64.b64encode("{}_".format(userid))

        desc = manager.fetch_from(table_surgery, start_row)

        desc_list = list(desc)

        return jsonify(data=desc_list)

    elif request.method == 'DELETE':
        userid = request.args.get("userid")
        hospitalid = request.args.get("hospitalid")
        date = request.args.get("date")
        time = request.args.get("time")

        rowkey = userid + "_" + hospitalid + "_" + date + "_" + time

        manager.delete_row(table_surgery, rowkey)

        return jsonify(success="true")


# API for sending only 1 surgery/time: loop
@app.route('/import/surgery', methods=['POST'])
def import_surgery():
    if request.method == 'POST':
        obj = request.json

        surgeries = obj

        for userid_hospitalid_date_time, information in surgeries.items():
            words = userid_hospitalid_date_time.split('_')
            userid = words[0]
            hospitalid = words[1]
            date = words[2]
            time = words[3]

            rowkey = userid + "_" + hospitalid + "_" + date + "_" + time

            data = {}
            data['information'] = information

            manager.save_batch(table_surgery, rowkey, data)

        return jsonify(success="true")
    else:
        return jsonify(success="false")


# API for get all hospitals in phase 1
@app.route('/hospital/all', methods=['GET'])
def hospital_all():
    if request.method == 'GET':
        desc = manager.fetch_all_with_row_id(table_hospital)
        desc_list = list(desc)

        return jsonify(data=desc_list)


# API for get all hospitals in phase 1
@app.route('/surgery/all', methods=['GET'])
def surgery_all():
    if request.method == 'GET':
        desc = manager.fetch_all_with_row_id(table_surgery)
        desc_list = list(desc)

        return jsonify(data=desc_list)


# API for get all activity results in phase 1
@app.route('/activity_result/1/all', methods=['GET'])
def activity_result_1_all():
    if request.method == 'GET':
        desc = manager.fetch_all(table_activity_results_1)
        desc_list = list(desc)

        return jsonify(data=desc_list)


# API for get all patient code paired with userid
@app.route('/patient_code/all', methods=['GET'])
def patient_code_all():
    if request.method == 'GET':
      data = manager.fetch_all_with_row_id(table_patient_code)
      data_list = list(data)

      return jsonify(data=data_list)


# API for get all pin code paired with userid
@app.route('/pin_code/all', methods=['GET'])
def pin_code_all():
    if request.method == 'GET':
      data = manager.fetch_all_with_row_id(table_pin_code)
      data_list = list(data)

      return jsonify(data=data_list)


# API for generate new patient code
@app.route('/patient_code/generate', methods=['GET'])
def patient_code_generate():
    if request.method == 'GET':
        appid = request.args.get("appid")
        userid = request.args.get("userid")
        
        # generate patient code here
        while True:
          rand = np.random.randint(1000, 9999, 1)[0]
          patient_code = 'PATIENT' + str(rand)

          rowkey = appid + "_" + patient_code
          data = manager.fetch(table_patient_code, rowkey)

          if data is None:
              break

        # save to profile data
        data1 = {}
        data1['profile'] = { 'patient_code': patient_code }

        rowkey1 = userid + "_" + appid
        manager.save_batch(table_information, rowkey1, data1)

        # save to patient code data
        data2 = {}
        data2['information']= { 'userid': userid }

        rowkey2 = appid + "_" + patient_code
        manager.save_batch(table_patient_code, rowkey2, data2)

        return jsonify(success="true", patient_code=patient_code)


# API for generate new patient code
@app.route('/pin_code/generate', methods=['GET'])
def pin_code_generate():
    if request.method == 'GET':
        appid = request.args.get("appid")
        userid = request.args.get("userid")
        
        # generate pin code here
        while True:
          rand = np.random.randint(100000, 999999, 1)[0]
          pin_code = str(rand)

          rowkey = appid + "_" + pin_code
          data = manager.fetch(table_pin_code, rowkey)

          if data is None:
              break

        # save to profile data
        data1 = {}
        data1['profile'] = { 'pin_code': pin_code }

        rowkey1 = userid + "_" + appid
        manager.save_batch(table_information, rowkey1, data1)

        # save to patient code data
        data2 = {}
        data2['pin_code']= { 'userid': userid }

        rowkey2 = appid + "_" + pin_code
        manager.save_batch(table_pin_code, rowkey2, data2)

        return jsonify(success="true", pin_code=pin_code)


# API for get userid paired with patient code
@app.route('/patient_code/check', methods=['GET'])
def patient_code_check():
    if request.method == 'GET':
        appid = request.args.get("appid")
        patient_code = request.args.get("patient_code")

        rowkey = appid + "_" + patient_code
        data = manager.fetch(table_patient_code, rowkey)
        if data is None:
          return jsonify(success="false", data=data)
        
        return jsonify(success="true", data=data)
          

# API for get userid paired with patient code
@app.route('/pin_code/check', methods=['GET'])
def pin_code_check():
    if request.method == 'GET':
        appid = request.args.get("appid")
        pin_code = request.args.get("pin_code")

        rowkey = appid + "_" + pin_code
        data = manager.fetch(table_pin_code, rowkey)
        if data is None:
          return jsonify(success="false", data=data)
        
        return jsonify(success="true", data=data)


@app.route('/test')  # API for test if server is running /// response in text
def test():
    # return "server is running..."

    # exists = manager.create_table(table_patient_code, 'patient_code')
    # tables = manager.all_tables()
    # columns = manager.all_columns(table_patient_code)
    # return jsonify(table=tables, cloumn=columns)

    rand = np.random.randint(1000, 9999, 1)[0]
    code = 'PATIENT' + str(rand)
    return jsonify(code=code)
    #
    #
    #
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
