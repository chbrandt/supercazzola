# -*- coding:utf-8 -*-

_ROOTS = {
    'arith' : {
        'family' :'arithmetics',
        'description' : """This section includes concepts involving or indicating some mathematical
                        operation performed on the primary ‘concept’ or just the presence of an
                        arithmetic factor or operator."""
    },

    'em' : {
        'family' :'electromagnetic spectrum',
        'description' : """This section describes the electromagnetic spectrum, either in a monochromatic
                        way or in predefined intervals. The complete list of proposed bands (in seven
                        classical regions of the e.m. spectrum: radio, millimeter, infrared, optical,
                        ultraviolet, x-ray and gamma-ray), can be found in the document Note-EMSpectrum-20040520"""
    },

    'instr' : {
        'family' :'instrument',
        'description' : """This section includes all quantities related to astronomical instrumentation,
                        e.g. detectors (plates, CCDs, etc.), spectrographs, and telescopes
                        (including observatories or missions), etc."""
    },

    'meta' : {
        'family' :'metadata',
        'description' : """This section includes all the information that is not coming directly from a
                        measurement, and information that could not be included in other sections."""
    },

    'obs' : {
        'family' :'observation',
        'description' : """This section includes, in principle under this section should go all words
                        describing an observation (the name of the observer or PI, the observing
                        conditions, the name of the field). In practice, the section is very ‘thin’
                        and could be deleted, if the sparse content could be housed elsewere."""
    },

    'phot' : {
        'family' :'photometry',
        'description' : """This section includes all the words describing photometric measures
                        are included in this section. The definitions distinguish between a
                        flux density (flux per unit frequency interval), a flux density
                        integrated over a given e.m. interval (flux if expressed linearly,
                        mag if expressed by a log), or a flux expressed in counts/s (if the
                        setup of the detector is photon counting observing mode). ‘Colors’,
                        which are differences of magnitudes (i.e. ratios of fluxes) measured
                        in different bandpasses, are also included."""
    },

    'phys' : {
        'family' :'physics',
        'description' : """This section includes atomic and molecular data (mainly used for spectroscopy)
                        and basic physical quantities (temperature, mass, gravity, luminosity, etc.)"""
    },

    'pos' : {
        'family' :'positional data',
        'description' : """This section describes all quantities related to the position of an object on the sky."""
    },

    'spect' : {
        'family' :'spectral data',
        'description' : """This section includes, for historical reasons, photometric data taken
                        in narrow spectral bands with instruments called spectrographs
                        are classified as spectroscopic data. These definitions should
                        not be confused with those in the 'em' category. em represents
                        the independent variable, or dispersion axis, and phot and spect
                        describe the dependent variable, or flux axis."""
    },

    'src' : {
        'family' :'source',
        'description' : """This is a rather generic section, mainly devoted to source classifications.
                        Variability, orbital, and velocity data are also included in this section."""
    },

    'stat' : {
        'family' :'statistics',
        'description' : """This section includes statistical information on measurements."""
    },

    'time' : {
        'family' :'time',
        'description' : """This section includes quantities related to time (age, date, period, etc.)
                        are described in this section."""
    }
}



from collections import OrderedDict
class _UCDRoots(OrderedDict):
    '''
    '''
    def __str__(self):
        s = ''
        for k,v in self.iteritems():
            fmt = '\n{0}\n{1}\n\tfamily      : {2}\n\tdescription : {3}\n'
            k_under = ''.join(['-']*len(k))
            s += fmt.format(k, k_under, v.family, v.description)
        return s


def init_roots():
    from ucd import UCDAtom
    roots = _UCDRoots()
    atoms = list(_ROOTS.keys())
    atoms.sort()
    for atom in atoms:
        _root        = _ROOTS[atom]
        family       = _root['family']
        #TODO:remove the slicing when done with the tests.
        description  = _root['description'][:50] # for test purposes only,
        root         = UCDAtom(atom,family,description)
        roots[atom]  = root
    return roots
