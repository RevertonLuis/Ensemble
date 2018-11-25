import numpy


def percentiles(vetor, percentil):
   
    if not isinstance(vetor, list):
        vetor = list(vetor)

    n = len(vetor)
    vetor.sort()
    p = percentil/100. # p = t/100
    np = n*p
    j = int(np)
    g = np - j
   
    if g > 0.:
        y = vetor[j+1]
    else:
        y = (vetor[j] + vetor[j+1])/2.

    print g
    return y


a = [1, 1.9, 2.2, 3, 3.7, 4.1, 5]

p = percentiles(a, 20)
 
print p

