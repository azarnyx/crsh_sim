#!/usr/bin/env python

# i=$HOME/startgallen/data/raw/1.json
# curl -H "Content-Type: application/json" -X POST -d @$i  http://0.0.0.0:8000/api/v1/getCrashInfo
# curl -H "Content-Type: application/json" -X POST -d @$i  http://0.0.0.0:8000/api/v1/getCrashImage --output o.jpg
# curl -H "Content-Type: application/json" -X POST -d @$i  http://0.0.0.0:8000/api/v1/getCrashImage?timeOffsetMS=0 --output o.jpg

from flask import Flask, jsonify, abort, request, make_response, url_for
import decode_files as df
from flask import send_file, send_from_directory
from io import BytesIO
import transform as tr
import sys
import pcar

application = Flask(__name__, static_url_path = "")

@application.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@application.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

def msg(s): sys.stderr.write(str(s) + "\n")
@application.route('/api/v1/getCrashInfo', methods = ['POST'])
def get_data():
    req_json = request.get_json()
    dec_json = df.decode_req(req_json)
    alpha, severity, tmax_offset, t_start, t_finish = tr.compute_parameters(dec_json)
    while alpha <= 0:  alpha += 360
    while alpha > 360: alpha -= 360
    return jsonify( {'impactAngle': alpha,  'offsetMaximumForce': tmax_offset*1000} )

@application.route('/api/v1/getCrashImage', methods = ['POST'])
def create_image():
    req_json = request.get_json()
    dec_json = df.decode_req(req_json)

    try:
        alpha, severity, tmax_offset, t_start, t_finish = tr.compute_parameters(dec_json)
        timeOffsetMS = request.args.get('timeOffsetMS')
        toffset = float(timeOffsetMS)*1.0e-3  - tmax_offset
    except:
        alpha = 0
        toffset = -10
    toffset = min( 0.5,  toffset)
    toffset = max(-1.0, toffset)
    toffset = (toffset+1.)/1.5
    
    while alpha <= 0:  alpha += 360
    while alpha > 360: alpha -= 360
    msg(alpha)
    pcar.plot_new(angle = alpha, toffset = toffset,
                  datafile = 'AudiTT.jpg', severity = severity)
    return send_file("plot.jpg", mimetype="image/jpeg")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=80)
