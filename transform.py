#!/usr/bin/env python3

import math
import json
import sys
import numpy as np
import scipy.integrate
import scipy.signal
import os.path
import numpy as np
from scipy.signal import butter, lfilter, freqz
from scipy.stats import linregress
from scipy.interpolate import UnivariateSpline

def find_nearest(array,value):
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
        return idx-1
    else:
        return idx

def sortw(timestamps, elements):
    timestamps, elements = zip(*sorted(zip(timestamps, elements)))
    return elements

def npa(a): return np.array(a)

def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / float(N)

def trap(x, t):
    y = scipy.integrate.cumtrapz(x, t)
    y = np.append(y, y[-1])
    return y

G = 9.81 # m/(ms)^2
X, Y, Z = 0, 1, 2
def conv(u, v, w, ca):
    x = ca[X][X]*u + ca[X][Y]*v + ca[X][Z]*w
    y = ca[Y][X]*u + ca[Y][Y]*v + ca[Y][Z]*w
    z = ca[Z][X]*u + ca[Z][Y]*v + ca[Z][Z]*w
    return x, y, z

def transform_func(d):
    ca = d["calibration"]
    oneG = d["oneG"]
    timestamp = d["timestamp"]
    referenceTime = d["referenceTime"]
    severity = d["severity"]
    tt = []; ax = []; ay = []; az = []
    for relativeTimestamp, x, y, z in d["data"]:
        t = (timestamp - referenceTime) * 1000 + relativeTimestamp
        x, y, z = conv(x, y, z, ca)
        x /= oneG; y /= oneG; z /= oneG
        x *= G; y *= G; z *= G
        tt.append(t); ax.append(x); ay.append(y); az.append(z)
    ax = npa(sortw(tt, ax))
    ay = npa(sortw(tt, ay))
    az = npa(sortw(tt, az))
    tt  = npa(sorted(tt)) / 1e3 # `ms' to `s'
    tt -= tt[0]

    vx = trap(ax, tt)
    vy = trap(ay, tt)
    vz = trap(az, tt)

    x = trap(vx, tt)
    y = trap(vy, tt)
    z = trap(vz, tt)

    return tt, vx, vy, ax, ay, severity

def roots(x, y):
    #slope, inter = linregress(x, y)[:2]
    #y -= slope*x + inter
    spl = UnivariateSpline(x, y, k = 4)
    spl.set_smoothing_factor(1.0)
    return spl.derivative().roots()

def force(x, y):
    sml = 0.1
    big = 3.0
    spl = UnivariateSpline(x, y, k = 4)
    spl.set_smoothing_factor(0.75)

    r = roots(x, y)
    r = r[0]
    y = spl(x)
    l = find_nearest(x, r - big)
    h = find_nearest(x, r - sml)
    sA = linregress(x[l:h], y[l:h])[0]
    l = find_nearest(x, r + sml)
    h = find_nearest(x, r + big)
    sB = linregress(x[l:h], y[l:h])[0]
    return sB - sA, r - big, r + big

def compute_parameters(file_json):
    mu = 0.7
    t, vx, vy, ax, ay, severity = transform_func(file_json)

    a = np.sqrt(ax**2+ay**2)
    ni = np.argmax(a)
    tmax_offset = t[ni]
    
    Fx, t_start, t_end = force(t, vx)
    Fy, t_start, t_end = force(t, vy)

    alpha = np.arctan2(-Fy, Fx)*180/np.pi
    return alpha, severity, tmax_offset, t_start, t_end
