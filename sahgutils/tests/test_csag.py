def test_basic_read():
    import datetime
    from pprint import pprint

    import numpy as np
    from numpy.testing import assert_allclose, assert_equal

    from sahgutils.io import CSAGStationReader

    csag_reader = CSAGStationReader('0009084_.txt')

    assert_equal(csag_reader.header(), {'ALTITUDE': 153.0,
                                        'CLEANING': 3,
                                        'COUNTRY': 'ZA',
                                        'CREATED':
                                        datetime.datetime(2012, 6, 20, 0, 0),
                                        'END_DATE':
                                        datetime.datetime(1998, 3, 20, 0, 0),
                                        'FORMAT': '1.0',
                                        'ID': '0009084_',
                                        'LATITUDE': -36.54,
                                        'LONGITUDE': 22.05,
                                        'NAME': 'KLEINDORP_-_POL',
                                        'START_DATE':
                                        datetime.datetime(1998, 3, 1, 0, 0),
                                        'VARIABLE': 'PPT'})

    assert_allclose(csag_reader.data(), np.array([0. , 0. , 0. , 0. , 8. , 0. ,
                                                  0. , 0. , 4.4, 1. , 2.5, 0. ,
                                                  0. , 0. , 0. , 5.3,12. , 0. ,
                                                  0. , 0. ]))

    assert_equal(csag_reader.dates(), [datetime.datetime(1998, 3, 1, 0, 0),
                                       datetime.datetime(1998, 3, 2, 0, 0),
                                       datetime.datetime(1998, 3, 3, 0, 0),
                                       datetime.datetime(1998, 3, 4, 0, 0),
                                       datetime.datetime(1998, 3, 5, 0, 0),
                                       datetime.datetime(1998, 3, 6, 0, 0),
                                       datetime.datetime(1998, 3, 7, 0, 0),
                                       datetime.datetime(1998, 3, 8, 0, 0),
                                       datetime.datetime(1998, 3, 9, 0, 0),
                                       datetime.datetime(1998, 3, 10, 0, 0),
                                       datetime.datetime(1998, 3, 11, 0, 0),
                                       datetime.datetime(1998, 3, 12, 0, 0),
                                       datetime.datetime(1998, 3, 13, 0, 0),
                                       datetime.datetime(1998, 3, 14, 0, 0),
                                       datetime.datetime(1998, 3, 15, 0, 0),
                                       datetime.datetime(1998, 3, 16, 0, 0),
                                       datetime.datetime(1998, 3, 17, 0, 0),
                                       datetime.datetime(1998, 3, 18, 0, 0),
                                       datetime.datetime(1998, 3, 19, 0, 0),
                                       datetime.datetime(1998, 3, 20, 0, 0)])
