"""

Generates appropriate replacements (masses, BC conditions, and abundances for MESA
inlist files. Outputs lists of replacements that are inputs to make_replacements.py

Args:
    runname: the name of the grid
    startype: the mass range of the models
    afe: the [a/Fe] value of the grid as str
    feh: the [Fe/H] value of the grid as str
    zbase: the Zbase corresponding to [Fe/H] and [a/Fe] as float
    rot: initial v/vcrit
    net: name of the nuclear network

Returns:
    the list of replacements

See Also:
    make_replacements: takes the list of replacements as an input

Example:
    >>> replist = make_inlist_inputs(runname, 'VeryLow')

Acknowledgment:
    Thanks to Joshua Burkart for providing assistance with and content for
    earlier versions of this code.

"""

import sys

import numpy as np


def make_inlist_inputs(runname, startype, feh, afe, zbase, rot, net,
                       amlt=1.82, asc=0.1, fovc=0.016, fovc0=0.008,
                       ath=666, etar=0.1):

    # Array of all masses
    def massgrid(i, f, step): return np.linspace(
        i, f, round(((f - i) / step)) + 1.0)

#    bigmassgrid = np.unique(np.hstack(massgrid(0.6,2.0,0.1)))
#    bigmassgrid = np.unique(np.hstack(massgrid(2.1,3.0,0.1)))

    bigmassgrid = np.unique(np.hstack((massgrid(0.1, 0.5, 0.05),
                                       massgrid(0.5, 2.0, 0.1),
                                       massgrid(2.0, 12.0, 0.5),
                                       massgrid(12.0, 40.0, 2))))

    # Choose the correct mass range and boundary conditions
    if (startype == 'VeryLow'):
        massindex = np.where(bigmassgrid < 0.30)
        bctype = 'tau_100_tables'
        bclabel = ''
    elif (startype == 'LowDiffBC'):
        massindex = np.where((bigmassgrid >= 0.30) & (bigmassgrid < 0.6))
        bctype1 = 'tau_100_tables'
        bclabel1 = '_tau100'
        bctype2 = 'photosphere_tables'
        bclabel2 = '_PT'
    elif (startype == 'Intermediate'):
        massindex = np.where((bigmassgrid >= 0.6) & (bigmassgrid < 10.0))
        bctype = 'photosphere_tables'
        bclabel = ''
    elif (startype == 'HighDiffBC'):
        massindex = np.where((bigmassgrid >= 10.0) & (bigmassgrid < 16.0))
        bctype1 = 'photosphere_tables'
        bclabel1 = '_PT'
        bctype2 = 'simple_photosphere'
        bclabel2 = '_SP'
    elif (startype == 'VeryHigh'):
        massindex = np.where(bigmassgrid >= 16.0)
        bctype = 'simple_photosphere'
        bclabel = ''
    else:
        print 'Invalid choice.'
        sys.exit(0)

    # Create mass lists
    def mapfunc(var): return np.str(
        int(var)) if var == int(var) else np.str(var)
    masslist = map(mapfunc, bigmassgrid[massindex])

    # Create BC lists
    if ('Diff' in startype):
        bctablelist = list([bctype1] * np.size(massindex)) + \
            list([bctype2] * np.size(massindex))
        bclabellist = list([bclabel1] * np.size(massindex)) + \
            list([bclabel2] * np.size(massindex))
    else:
        bctablelist = list([bctype] * np.size(massindex))
        bclabellist = list([bclabel] * np.size(massindex))

    # Create [a/Fe] lists
    afelist = list([afe] * np.size(massindex))

    # create [Fe/H] lists
    fehlist = list([feh] * np.size(massindex))

    # Create Zbase list
    zbaselist = list([zbase] * np.size(massindex))

    # Create rot list
    rotlist = list([rot] * np.size(massindex))

    # Create net list
    netlist = list([net] * np.size(massindex))

    # Create alpha mlt list
    amltlist = list([amlt] * np.size(massindex))

    # Create alpha semiconvection list
    asclist = list([asc] * np.size(massindex))

    # Create core overshoot strength list
    fovclist = list([fovc] * np.size(massindex))

    # Create core overshoot strength 0 list (typically fovc/2)
    fovc0list = list([fovc0] * np.size(massindex))

    # Create alpha thermohaline list
    athlist = list([ath] * np.size(massindex))

    # Create Reimers eta list
    etarlist = list([etar] * np.size(massindex))

    # Make list of [replacement string, values]
    replist = [
        ["<<MASS>>", masslist],
        ["<<BC_LABEL>>", bclabellist],
        ["<<BC_TABLE>>", bctablelist],
        ["<<AFE>>", afelist],
        ["<<FEH>>", fehlist],
        ["<<ZBASE>>", zbaselist],
        ["<<ROT>>", rotlist],
        ["<<NET>>", netlist],
        ["<<AMLT>>", amltlist],
        ["<<ASC>>", asclist],
        ["<<FOVC>>", fovclist],
        ["<<FOVC0>>", fovc0list],
        ["<<ATH>>", athlist],
        ["<<ETAR>>", etarlist],
    ]

    # Special case for LowDiffBC
    if ('Diff' in startype):
        replist = [
            ["<<MASS>>", masslist * 2],
            ["<<BC_LABEL>>", bclabellist],
            ["<<BC_TABLE>>", bctablelist],
            ["<<AFE>>", afelist * 2],
            ["<<FEH>>", fehlist * 2],
            ["<<ZBASE>>", zbaselist * 2],
            ["<<ROT>>", rotlist * 2],
            ["<<NET>>", netlist * 2],
            ["<<AMLT>>", amltlist * 2],
            ["<<ASC>>", asclist * 2],
            ["<<FOVC>>", fovclist * 2],
            ["<<FOVC0>>", fovc0list * 2],
            ["<<ATH>>", athlist * 2],
            ["<<ETAR>>", etarlist * 2],
        ]

    return replist
