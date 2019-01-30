def pprint(obj):
    if isinstance(obj,dict):
        for k,v in obj.iteritems():
            print("{} : {}".format(k,v))
