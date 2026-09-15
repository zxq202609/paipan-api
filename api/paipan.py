# -*- coding: utf-8 -*-
"""八字排盘 API（Vercel Serverless Function）"""
from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

try:
    from lunar_python import Solar
except Exception:
    Solar = None


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
        "qiyun": f"出生后{yun.getStartYear()}年{yun.getStartMonth()}个月起运",
        "dayun": dayun,
        "nongli": lunar.toString(),
    }


class handler(BaseHTTPRequestHandler):
    def _respond(self, payload, code=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _run(self, params):
        if Solar is None:
            return self._respond({"code": 500, "msg": "服务未就绪（缺少依赖）"}, 500)
        try:
            y, m, d, h = params.get("y"), params.get("m"), params.get("d"), params.get("h")
            i = params.get("i", 0)
            x = params.get("x", "0")
            if not all([y, m, d, h]):
                return self._respond({"code": 400, "msg": "缺少参数：需 y(年) m(月) d(日) h(时)"}, 400)
            data = calc(y, m, d, h, i, x)
            return self._respond({"code": 200, "msg": "成功", "data": data})
        except Exception as e:
            return self._respond({"code": 500, "msg": "出错：%s" % str(e)}, 500)

    def do_GET(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        self._run({k: v[0] for k, v in q.items()})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length).decode("utf-8") if length else ""
        try:
            p = json.loads(raw)
        except Exception:
            p = {k: v[0] for k, v in urllib.parse.parse_qs(raw).items()}
        self._run(p)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
