#!/usr/bin/env python
import os
from pylab import *
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy
import netCDF4

def gera_conjunto_txt():

   modelos =  "GFS GEP01 GEP02 GEP03 GEP04 GEP05 GEP06 GEP07 GEP08 GEP09 GEP10 GEP11 GEP12 GEP13 GEP14 GEP15 GEP16 GEP17 GEP18 GEP19 GEP10 SSEOP01 SSEOP02 SSEOP07"
   modelos = modelos.split()
   
   diretorio = "/dados/produtos/gera_ensemble/logs_graficos/"
   arquivos = os.listdir(diretorio)
   
   datas = {}
   
   for arq in arquivos:
       data = arq[-14:-4] 
       
       a = open(diretorio + arq)
       valor = float(a.readlines()[-1].split()[1])
       #if valor < 0.: valor = 0.
       a.close()
       
       if not data in datas.keys():
       
           if datetime.datetime.strptime(data, "%Y%m%d%H") >= datetime.datetime.strptime("2017031200", "%Y%m%d%H") and \
	      datetime.datetime.strptime(data, "%Y%m%d%H") <= (datetime.datetime.strptime("2017031200", "%Y%m%d%H") + datetime.timedelta(hours=24)):
       	      datas[data] = [valor]
       else:
           if datetime.datetime.strptime(data, "%Y%m%d%H") >= datetime.datetime.strptime("2017031200", "%Y%m%d%H") and \
	      datetime.datetime.strptime(data, "%Y%m%d%H") <= (datetime.datetime.strptime("2017031200", "%Y%m%d%H") + datetime.timedelta(hours=24)):
              datas[data].append(valor)
	      	
   return datas
    	
	
	
def carrega_ensemble():

   arq = netCDF4.Dataset("/dados/produtos/gera_ensemble/ensemble_2017031200.nc")
   minimo  = arq.variables["Minimo"][:,116,99]
   qi      = arq.variables["Quartil_Inferior"][:,116,99]
   mediana = arq.variables["Mediana"][:,116,99]
   qs      = arq.variables["Quartil_Superior"][:,116,99]
   maximo  = arq.variables["Maximo"][:,116,99]
   arq.close()
   
   return minimo, qi, mediana, qs, maximo
   

def gera_boxplot(listas):


    minimo, qi, mediana, qs, maximo = carrega_ensemble()
    
    fig = plt.figure(figsize=(13,13))
    graf1 = fig.add_subplot(111)
    ax1 = fig.add_subplot(111)

    #linhas = open("conjunto.txt").readlines()

    candlesticks = []

    #for i in range(len(linhas)):
    #   lista = []
    #   for j in range(len(linhas[i].split())):
#	  lista.append(float(linhas[i].split()[j]))
#       candlesticks.append(lista)


    datas = listas.keys()
    datas.sort()
    for data in datas:
       candlesticks.append(listas[data]) 


    larguras = []
    for i in range(25):
       larguras.append(0.5)

    plotagem = boxplot(candlesticks, notch=0, sym='', vert=1, whis=numpy.inf, positions=range(25), widths=None)
    plt.axis([-1, 26, -0.3, 1])

    setp(plotagem['medians'], color='black', lw=1)               # Deixa a mediana preta


    setp(plotagem['whiskers'], color='black', ls="-") 
    setp(plotagem['boxes'], color='black', lw=1) 

    ## Preenchendo com cores os boxplot
    #boxColors = ['green','red']
    boxColors = ['yellow','yellow']
    
    numBoxes = len(candlesticks)
    #for i in range(numBoxes):
    #  box = a['boxes'][i]
    #  boxX = []
    #  boxY = []
    #  for j in range(5): #===================> Porque sao cinco coordenadas a b => (o programa le c,d,b,a e c novamente)
    #      boxX.append(box.get_xdata()[j])    #                              c d 
    #      boxY.append(box.get_ydata()[j])
    #  boxCoords = zip(boxX,boxY)
    #  #  Alternate between Dark Khaki and Royal Blue
    #  k = i % 2
    #  boxPolygon = Polygon(boxCoords, facecolor=boxColors[k])
    #  graf1.add_patch(boxPolygon)


    comp = 0
    for i in range(numBoxes):
      box = plotagem['boxes'][i]
      boxX = []
      boxY = []
      boxCoords = zip(box.get_xdata(),box.get_ydata())

      if comp > numpy.average(candlesticks[i]):
	 k = 1
      else:
	 k = 0
      comp = numpy.average(candlesticks[i])      

      boxPolygon = Polygon(boxCoords, facecolor=boxColors[k])
      graf1.add_patch(boxPolygon)



    rodadas = []
    data = "10/07/2009 "
    label = range(0, 25)


    for i in range(25):

       try:
	  indice = label.index(i)
       except:
	  indice = None

       if indice != None:
	  hora = "%s" % str(i)

	  if len(hora) < 2:
             hora = "0" + hora

	  rodadas.append(data + hora)
       else:
	  rodadas.append("")   

    xtickNames = plt.setp(ax1, xticklabels=rodadas)
    plt.setp(xtickNames, rotation=90, fontsize=10)

    ax1.plot(xrange(25), minimo, linestyle='-', color='blue')
    ax1.plot(xrange(25), qi, linestyle='-', color='red')
    ax1.plot(xrange(25), mediana, linestyle='-', color='green')
    ax1.plot(xrange(25), qs, linestyle='-', color='cyan')
    ax1.plot(xrange(25), maximo, linestyle='-', color='grey')


    savefig("figura")
    #show()

listas = gera_conjunto_txt()

gera_boxplot(listas)
