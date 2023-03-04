import datetime
import io
import re
import sqlite3

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from pylab import rcParams

# rcParams['figure.figsize'] = 5, 3

from flask import Blueprint, request, jsonify, g, render_template
import csv

BASED = datetime.date(2001,1,1)
KEYS = "id, name, name_en, active, short_decs, description, short_decs_en, description_en, mo, subject, dep, city, " \
       "city_en, addr, addr_en, octmo, fcp, actions, starts, ends, money, fed_money, take_money, subj_money, " \
       "subj_take_money, city_money, city_take_money, own_money, own_take_money, keys, curator, curator_en, " \
       "curator_addr, curator_addr_en, curator_phone, phone, works_mon_fri, works_sat, works_sun, area, email, " \
       "url, registry, type, champtype, sports, x, y, z, cx, cy, mx, my, general_plan, sub_plans, photo, " \
       "gallerey_url, video, panoramy, web_trans, elses".split(", ")

api = Blueprint('api', __name__, url_prefix='/api')


def get_db():
    """ Возвращает объект соединения с БД"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("data.sqlite")
    return db


@api.route('/all')
def api_all():
    cur = get_db().cursor()
    data = []
    for row in cur.execute("select id, name, x, y from data"):
        try:
            obj = [float(row[3]), float(row[2])]
        except:
            continue
        else:
            data.append([row[0], row[1], obj])

    return jsonify(data)


@api.route('/object/<id>')
def api_object(id):
    cur = get_db().cursor()
    cur.execute(f"select * from data where id = {id!r}")

    data = dict(zip(KEYS, cur.fetchone()))
    cur.execute(f"select * from ext where id = {id!r}")
    comments = cur.fetchall()

    print(comments)

    return render_template('object.html', obj=data, comms=comments)


@api.route('/object/<id>/comment', methods=['POST'])
def api_object_comment(id: str):
    if id.isdigit():
        db = get_db()
        cur = db.cursor()
        cur.execute(f"insert into ext VALUES (?, ?, ?, ?)",
                    (id, request.form.get('rating'), request.form.get('name'), request.form.get('comment')))

        db.commit()

        return '', 203
    else:
        return '', 400


@api.route('/graphics', methods=["POST"])
def api_graphics():
    cur = get_db().cursor()

    ind, dind, x, starts, ends = [], [], [], [], []
    fs = ', '.join(re.search(r'[0-9]+', e).group() for e in request.json)
    for row in cur.execute(f"select name, money, starts, ends from data where id in ({fs})"):
        try:
            ind.append(row[0])
            x.append(int(row[1]))
            if row[3] and row[2]:
                dind.append(row[0])
                starts.append(datetime.datetime.strptime(row[2], "%d.%m.%Y"))
                ends.append(datetime.datetime.strptime(row[3], "%d.%m.%Y"))
        except IndexError:
            continue

    # fig = plt.subplot()
    # fig = plt.figure(dpi=dpi, figsize=(700 / dpi, 400 / dpi))
    # axes = fig.add_axes([0, 0.4, 0.6, 0.7])
    # axes.tick_params(axis=u'both', which=u'both', length=10)
    # for tk in axes.get_yticklabels():
    #     tk.set_visible(True)
    # for tk in axes.get_xticklabels():
    #     tk.set_visible(True)
    plt.bar(ind, x)
    plt.xticks(rotation='vertical')

    f = io.BytesIO()
    plt.savefig(f, format="svg")
    plt.cla()

    start = np.fromiter((mdates.date2num(event) for event in starts),
                        dtype='float', count=len(starts))
    finish = np.fromiter((mdates.date2num(event) for event in ends),
                         dtype='float', count=len(ends))
    date = (start + finish) // 2
    duration = finish - start

    plt.gca().yaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y'))
    plt.errorbar(dind, date, [np.zeros(len(duration)), duration], linestyle='')
    plt.xticks(rotation='vertical')
    plt.gcf().autofmt_xdate()
    # plt.xaxis_date()
    # plt.yaxis_date()

    d = io.BytesIO()
    plt.savefig(d, format="svg")
    plt.cla()

    return render_template('graphics.html', ffg=str(f.getvalue().decode('utf-8')), datesg=str(d.getvalue().decode('utf-8')))
