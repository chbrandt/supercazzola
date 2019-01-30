# -*- coding:utf-8 -*-
import logging

def setup(nprocs=2):
    """
    Run xmatch in parallel

    It splits the first array in 'nprocs' for parallel processing,
    then it concatenates the outputs and return that.
    """
    #TODO: do all the verifications for parallel run

    # Lets us see what happens in parallel
    # First, run from the command line:
    #$ ipcluster start -n 2
    try:
        import ipyparallel as ipp
        client = ipp.Client()
        dview = client[:]
    except Exception as e:
        logging.error("Not able to setup parallel environment: {}".format(e))
        dview = None
    return dview
