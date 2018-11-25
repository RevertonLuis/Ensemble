import sys
import os
import numpy
import random

sys.path.append("/dados/reverton/gera_ensemble/bibliotecas/install/wquantiles/lib/python2.7/site-packages/wquantiles-0.5-py2.7.egg/")

sys.path.append("/dados/reverton/gera_ensemble/bibliotecas/install/gmisclib/lib/python2.7/site-packages/gmisclib-0.65.5-py2.7.egg/")

import weighted
import gmisclib.weighted_percentile

#data = numpy.array( [round(x,2) for x in [1., 1.9, 2.2, 3., 3.7, 4.1, 5.]] )

N = 100
R = 3
data = numpy.array( [round(random.random(),R) for x in xrange(N)] )
peso = numpy.ones(N, 'f')


#peso = numpy.array( [1.1, 0.5, 23., 0.1, 15., 0.1, 2], 'f')
#print data
#print peso

mediana =  weighted.quantile(data, peso, .5)



print  "Percentil   wquantile     numpy.percentil    gmisclib"
for q in [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.]:
    print "  %3i         %4.4f             %4.4f            %4.4f" % (int(q*100), round(weighted.quantile(data, peso, q), R), \
                                                                                  round(numpy.percentile(data, q*100, interpolation="linear"), R), \
										  round(gmisclib.weighted_percentile.wp( data, peso, [q])[0], R))
    


print
print 
# Teste vetorial
data = data.reshape((int(numpy.sqrt(N)), int(numpy.sqrt(N))))
peso = peso[:int(numpy.sqrt(N))]


for q in [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.]:
    print 
    print "%3i" % (q*100)
    print "%4.4f  %4.4f  %4.4f  %4.4f  %4.4f  %4.4f  %4.4f  %4.4f  %4.4f   %4.4f   Linhas 0-9" % (weighted.quantile(data[0,:], peso, q), \
                                                                                		  weighted.quantile(data[1,:], peso, q), \
												  weighted.quantile(data[2,:], peso, q), \
												  weighted.quantile(data[3,:], peso, q), \
												  weighted.quantile(data[4,:], peso, q), \
												  weighted.quantile(data[5,:], peso, q), \
												  weighted.quantile(data[6,:], peso, q), \
												  weighted.quantile(data[7,:], peso, q), \
												  weighted.quantile(data[8,:], peso, q), \
												  weighted.quantile(data[9,:], peso, q) ) 


    vet = weighted.quantile(data, peso, q)
    print "%4.4f  %4.4f  %4.4f  %4.4f  %4.4f  %4.4f  %4.4f  %4.4f  %4.4f   %4.4f   Vetorial" % (vet[0], vet[1], vet[2], vet[3], vet[4], vet[5], vet[6], vet[7], vet[8], vet[9] ) 


print 
# Testes com 3d
data3d = numpy.random.rand(3, 3, 3)
pesos = numpy.ones(3, 'f')
q = 0.5


matriz = numpy.zeros((3,3),'f')

for q in [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.]:
    
    for j in xrange(3):
       for i in xrange(3):
       
          matriz[j,i] = weighted.quantile(data3d[:,j,i], pesos, q)
	  
      	  
    
    print
    print q, matriz      

