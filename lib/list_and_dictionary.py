def list_to_dict(a):

    """ Function that transform a list in the form
        a = [
            (model1, run1, date1,  (matrix1,  acc1)),
            (model1, run1, date11, (matrix11, acc11)),
            (model2, run2, date2,  (matrix2,  acc2)),
            (model3, run3, date3,  (matrix3,  acc3)),
            (model4, run4, date4,  (matrix4,  acc4), latlon, lat/lon),
            (model4, run4, date41, (matrix41, acc41)),
            (model4, run4, date42, (matrix42, acc42)),
            (model4, run4, date43, (matrix43, acc43))
            ]

        in dictionary in the form

        b = {
             model1: {run1: {date1:  (matrix1,   acc1),
             date11: (matrix11,  acc11)}},
             model2: {run2: {date2:  (matrix2,   acc2)}},
             model3: {run3: {date3:  (matrix3,   acc3)}},
             model4: {run4: {date4:  (matrix4,   acc4),
             date41: (matrix41,  acc41),
             date42: (matrix42,  acc42),
             date43: (matrix43,  acc43),
             latlon: lat/lon}},
             }

    """

    b = {}
    for l in range(len(a)):
        if a[l][0] not in b.keys():
            b[a[l][0]] = {}
        if a[l][1] not in b[a[l][0]].keys():
            b[a[l][0]][a[l][1]] = {}

        if len(a[l]) > 4:
            b[a[l][0]][a[l][1]].update({a[l][2]: a[l][3], a[l][4]: a[l][5]})
        else:
            b[a[l][0]][a[l][1]].update({a[l][2]: a[l][3]})

    return b
