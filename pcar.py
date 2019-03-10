#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import imageio
import math
import sys
from scipy.stats import skewnorm
def msg(s): sys.stderr.write(str(s) + "\n")

class M(object):
    def __init__(self, a):
        self.x = self.y = None
        self.a = a
    def upd(self, x, y):
        if self.x == None:
            self.x = x
            self.y = y
        else:
            u = math.atan2(-y, x)
            v = math.atan2(-self.y, self.x)
            if abs(u - self.a) < abs(v - self.a):
                self.x = x
                self.y = y

def intersect(x0, y0, x1, y1,  a):
    n = 100
    if a > 180: a -= 360
    a = a/180.0*math.pi

    m = M(a)
    xc = (x1 - x0)/2.0
    yc = (y1 - y0)/2.0
    x0 -= xc; x1 -= xc
    y0 -= yc; y1 -= yc
    for i in range(n):
        x  = x0 + (x1 - x0)*i/n
        y  = y0
        m.upd(x, y)
    for i in range(n):
        x  = x0 + (x1 - x0)*i/n
        y  = y1
        m.upd(x, y)
    for i in range(n):
        x  = x0
        y  = y0 + (y1 - y0)*i/n
        m.upd(x, y)
    for i in range(n):
        x  = x1
        y  = y0 + (y1 - y0)*i/n
        m.upd(x, y)
    return m.x + xc, m.y + yc

def plot(angle, toffset, datafile):
    def twoD_Gaussian(x, y, xo, yo, sigma_x, sigma_y):
        a = 1./(2*sigma_x**2) + 1./(2*sigma_y**2)
        c = 1./(2*sigma_x**2) + 1./(2*sigma_y**2)
        g = np.exp( - (a*((x-xo)**2) + c*((y-yo)**2)))
        return g.ravel()

    def transparent_cmap(cmap, N=255):
        "Copy colormap and set alpha values"
        mycmap = cmap
        mycmap._init()
        mycmap._lut[:,-1] = np.linspace(0, 0.8, N+4)
        return mycmap

    msg("pcar.py: angle: %g" % angle)
    alpha = angle
    impact_sev_max=0.3
    impact_sev=impact_sev_max*np.exp(toffset)/np.exp(1)
    arrow_l = 100
    mycmap = transparent_cmap(plt.cm.Reds)
    I = imageio.imread(datafile)
    p = np.asarray(I).astype('float')
    h, w = I.shape[0:2]
    y, x = np.mgrid[0:h, 0:w]
    lx = x.max(); ly = y.max()
    xx, yy = intersect(0, 0, lx, ly, angle)
    dx = -arrow_l*np.cos(angle*math.pi/180.0)
    dy =  arrow_l*np.sin(angle*math.pi/180.0)
    fig, ax = plt.subplots(figsize=(w/200,h/200))
    ax.imshow(I)
    if toffset >= 0:
        Gauss = twoD_Gaussian(x, y, xx + 0.5*dx, yy + 0.5*dy, impact_sev*x.max(), impact_sev*y.max())
        cb = ax.contourf(x, y, Gauss.reshape(x.shape[0], y.shape[1]), 15, cmap=mycmap)
        ax.arrow(xx - dx, yy - dy, 1.5*dx, 1.5*dy, width=10, color='r', head_width=40, head_length=30)
        ax.plot([lx/2], [ly/2], 'xk');
    plt.axis('off')
    plt.tight_layout()
    ax.xaxis.set_major_locator(matplotlib.ticker.NullLocator())
    ax.yaxis.set_major_locator(matplotlib.ticker.NullLocator())
    plt.savefig("plot.jpg", dpi=150, bbox_inches='tight', pad_inches = 0)


def plot_new(angle, toffset, datafile, severity):
    def mod_xoyo(xo, yo, angle):
        """ function to modify zero-point of the gaussian 2D function """
        if angle>350 and angle<358:
            yo=yo*1.2
        if angle>6 and angle<50:
            yo=yo*0.8
        if angle>60 and angle<72:
            xo=xo*1.07        
        if angle>72 and angle<86:
            xo=xo*1.07        
        if angle>94 and angle<120:
            xo=xo*0.9
            
        if angle>130 and angle<174:
            yo=yo*0.0
            xo=xo*1.8
            
        if angle>182 and angle<210:
            yo=yo*1.2
        if angle>240 and angle<252:
            xo=xo*0.93        
        if angle>252 and angle<166:
            xo=xo*0.93        
        if angle>274 and angle<300:
            xo=xo*1.1
            
        if angle>330 and angle<340:
            xo=xo*0.95
            yo=yo
        if angle>300 and angle<330:
            xo=xo*0.95
            yo=yo
        return xo, yo

    def twoD_Gaussian(x, y, xo, yo, sigma_x, sigma_y):
        a = 1./(2*sigma_x**2) + 1./(2*sigma_y**2)
        c = 1./(2*sigma_x**2) + 1./(2*sigma_y**2)
        alpha1 = 7*np.cos(np.pi-angle*np.pi/180)
        alpha2 = 7*np.sin(np.pi-angle*np.pi/180)
        xo, yo = mod_xoyo(xo, yo, angle)
        dx = (x-xo)
        dy = (y-yo)
        g = skewnorm.pdf(dx*np.sqrt(a),alpha1)*skewnorm.pdf(dy*np.sqrt(c), alpha2)
        # cut if out of car
        g[:40]=0
        g[600:]=0
        g[:,:60]=0
        g[:,1370:]=0
        g = g.ravel()
        return g

    def transparent_cmap(cmap, N=255):
        "Copy colormap and set alpha values"
        mycmap = cmap
        mycmap._init()
        mycmap._lut[:,-1] = np.linspace(0, 0.8, N+4)
        return mycmap

    msg("pcar.py: angle: %g" % angle)
    alpha = angle
    impact_sev_max=np.sqrt((0.7+severity)/10.)*0.3
    impact_sev=impact_sev_max*np.exp(toffset)/np.exp(1)
    arrow_l = 100
    mycmap = transparent_cmap(plt.cm.jet)
    I = imageio.imread(datafile)
    p = np.asarray(I).astype('float')
    
    h, w = I.shape[0:2]
    y, x = np.mgrid[0:h, 0:w]
    lx = x.max(); ly = y.max()

    xx, yy = intersect(0, 0, lx, ly, angle)
    dx = -arrow_l*np.cos(angle*math.pi/180.0)
    dy =  arrow_l*np.sin(angle*math.pi/180.0)
    fig, ax = plt.subplots(figsize=(w/200,h/200))
    ax.imshow(I)
    if toffset > 0.001:
        Gauss = twoD_Gaussian(x, y, xx + 0.5*dx, yy + 0.5*dy, impact_sev*x.max(), impact_sev*y.max())
        cb = ax.contourf(x, y, Gauss.reshape(x.shape[0], y.shape[1]), 15, cmap=mycmap, top=30)
        ax.arrow(xx - dx, yy - dy, 2.5*dx, 2.5*dy, width=10, color='black', head_width=40, head_length=30)
        ax.plot([lx/2], [ly/2], 'xk');
    plt.axis('off')
    plt.tight_layout()
    ax.xaxis.set_major_locator(matplotlib.ticker.NullLocator())
    ax.yaxis.set_major_locator(matplotlib.ticker.NullLocator())
    plt.title("angle: "+str(round(angle, 3))+"    severity: "+str(severity)+ "    % from max damage: "+str(round(toffset, 3)*100))
    plt.savefig("plot.jpg", dpi=150, bbox_inches='tight', pad_inches = 0)


if __name__ == "__main__":
    plot(angle = 180 + 10, toffset = 0.75, datafile = 'AudiTT.jpg')
