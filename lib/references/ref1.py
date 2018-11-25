
def list_to_dict(a):

    b = {}
    for l in xrange(len(a)):
        if a[l][0] not in b.keys(): b[ a[l][0] ] = {}
        if a[l][1] not in b[ a[l][0] ].keys(): b[ a[l][0] ][ a[l][1] ] = {}

        if len(a[l]) > 4:
            b[ a[l][0] ][ a[l][1] ].update({a[l][2]: a[l][3], a[l][4]: a[l][5]})
        else:
            b[ a[l][0] ][ a[l][1] ].update({a[l][2]: a[l][3]})

    del a
    return b 

matriz = 'matriz'# numpy.zeros((2,2), 'f')

a = [
     ('modelo1', 'rodada1', 'data1', (matriz, 'acumulacao1')), 
     ('modelo1', 'rodada1', 'data11', (matriz, 'acumulacao11')), 
     ('modelo2', 'rodada2',  'data2', (matriz, 'acumulacao2')),
     ('modelo2', 'rodada21', 'data2', (matriz, 'acumulacao2')), 
     ('modelo3', 'rodada3', 'data3', (matriz, 'acumulacao3')), 
     ('modelo3', 'rodada31', 'data3', (matriz, 'acumulacao3')),
     ('modelo3', 'rodada31', 'data31', (matriz, 'acumulacao31')), 
     ('modelo4', 'rodada4', 'data4', (matriz, 'acumulacao4'), 'latlon', 'lat e lon'),
     ('modelo4', 'rodada4', 'data41', (matriz, 'acumulacao41')),
     ('modelo4', 'rodada4', 'data42', (matriz, 'acumulacao42')),
     ('modelo4', 'rodada4', 'data43', (matriz, 'acumulacao43'))
    ]


b = list_to_dict(a)

for m in b.keys():
   for r in b[m].keys():
       print m, r, b[m][r]

