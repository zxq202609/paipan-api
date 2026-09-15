# -*- coding: utf-8 -*-
"""八字排盘 API（Flask on Vercel）"""
from flask import Flask, request, jsonify
from lunar_python import Solar

app = Flask(__name__)


def calc(y, m, d, h, i, x):
    solar = Solar.fromYmdHms(int(y), int(m), int(d), int(h), int(i), 0)
    lunar = solar.getLunar()
    ec = lunar.getEightChar()
    gender = "female" if str(x) == "1" else "male"

    pillars = [ec.getYear(), ec.getMonth(), ec.getDay(), ec.getTime()]
    shishen_gan = [ec.getYearShiShenGan(), ec.getMonthShiShenGan(), "日主", ec.getTimeShiShenGan()]
    canggan = {
        "年": ec.getYearHideGan(), "月": ec.getMonthHideGan(),
        "日": ec.getDayHideGan(), "时": ec.getTimeHideGan(),
    }
    canggan_shishen = {
        "年": ec.getYearShiShenZhi(), "月": ec.getMonthShiShenZhi(),
        "日": ec.getDayShiShenZhi(), "时": ec.getTimeShiShenZhi(),
    }
    yun = ec.getYun(1 if gender == "male" else 0)
    dayun = []
    for dy in yun.getDaYun()[:9]:
        if dy.getGanZhi():
            dayun.append({
                "start_age": dy.getStartAge(),
                "start_year": dy.getStartYear(),
                "ganzhi": dy.getGanZhi(),
            })

    return {
        "sizhu": pillars,
        "rizhu": ec.getDayGan(),
        "shishen_gan": shishen_gan,
        "canggan": canggan,
        "canggan_shishen": canggan_shishen,
        "qiyun": "出生后%d年%d个月起运" % (yun.getStartYear(), yun.getStartMonth()),
        "dayun": dayun,
        "nongli": lunar.toString(),
    }


@app.route("/api/paipan")
def paipan():
    y, m, d, h = request.args.get("y"), request.args.get("m"), request.args.get("d"), request.args.get("h")
    if not all([y, m, d, h]):
        return jsonify({"code": 400, "msg": "缺少参数：需 y(年) m(月) d(日) h(时)"}), 400
    try:
        data = calc(y, m, d, h, request.args.get("i", 0), request.args.get("x", "0"))
        return jsonify({"code": 200, "msg": "成功", "data": data})
    except Exception as e:
        return jsonify({"code": 500, "msg": "出错：%s" % str(e)}), 500


@app.route("/")
def index():
    return jsonify({"code": 200, "msg": "八字排盘 API 运行中"})
