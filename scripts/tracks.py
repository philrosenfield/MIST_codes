import os
from astropy.table import Table

def replace_all(text, dic):
    """perfrom text.replace(key, value) for all keys and values in dic"""
    for old, new in dic.items():
        text = text.replace(old, new)
    return text

# unified column names with other stellar evolution models
DEFAULTDICT = {'star_age': 'age', 'star_mass': 'mass', 'log_L': 'logL',
               'log_Teff': 'logT', 'log_g': 'logg', '#': ''}

class Track(object):
    """MESA/MIST Track class to read track data and record metadata"""
    def __init__(self, filename=None, data_start=6):
        if filename is not None:
            self.base, self.name = os.path.split(filename)
            self.read_mesa_track(filename, data_start=data_start)

    def read_mesa_track(self, filename, data_start=6):
        self.data, self.metadata = read_mesa_track(filename,
                                                   data_start=data_start)

    def savetrack(self, output=None, include_names=None, format='ascii',
                  overwrite=False):
        if output is None:
            output = os.path.join(self.base, self.name) + '.dat'
        if include_names is None:
            include_names = ['age', 'mass', 'logL', 'logT', 'logg']

        self.data.write(output, include_names=include_names, format=format,
                        formats={k: '{:.6f}' for k in include_names},
                        overwrite=overwrite)
        print('wrote {:s}'.format(output))
        return output



def parse_tracksetname(string):
    """
    track sets should have key_val pairs for filename with m/p to denote -/+
    values. E.g., string='feh_m0.15_afe_p0.0_cov_0.016_eov_0.016_vvcrit_0.0'
    """
    items = os.path.split(string)[-1].split('_')
    keys = items[::2]
    vals = [float(v.replace('m', '-').replace('p','')) for v in items[1::2]]
    return {k:v for k, v in zip(keys, vals)}

def read_mesa_track(filename, data_start=6):
    # data_start=15 for MIST
    header = []
    with open(filename) as inp:
        for i in range(data_start):
            header.append(inp.readline().strip())
    if len(header) > 0:
        names = replace_all(header[-1], DEFAULTDICT).split()
        metadata = {}
        # doesn't work for mist...
        if len(header) > 2:
            metadata = {k: v for k,v in zip(header[1].split(), header[2].split())}
        data = Table.read(filename, data_start=data_start, names=names,
                          format='ascii')
    else:
        print('Warning, do not know column names.')
        data = Table.read(filename, data_start=data_start, format='ascii')

    return data, metadata

class TrackSet(object):
    def __init__(self, tracksetname=None, data_start=6, masses=None):
        self.tracks = []
        if tracksetname is not None:
            self.metadata = parse_tracksetname(tracksetname)
            self.load_tracks(tracksetname, data_start=data_start,
                             masses=masses)

    def load_tracks(self, tracksetname, subdir='tracks', basedir=None,
                    data_start=6, ext='track', masses=None):
        if basedir is None:
            base = os.path.join(tracksetname, subdir)
        self.trackfiles = [os.path.join(base, l) for l in os.listdir(base)
                           if l.endswith(ext)]
        for trackname in self.trackfiles:
            # MIST mass string: path/00400M.extensions... = 4 Msun
            mass_str = os.path.splitext(
                os.path.split(trackname)[1])[0].split('_')[0].split('M')[0]
            mass = float(mass_str) / 100
            if masses is not None:
                if not mass in masses:
                    continue
            newattr = 'M{}'.format(mass_str)
            track = Track(trackname, data_start=data_start)
            self.tracks.append(track)
            track.mass = mass

        if not len(self.tracks):
            print('No tracks found: {:s}'.format(tracksetname))

    def savetracks(self, kwargs=None):
        kwargs = kwargs or {}
        [t.savetrack(**kwargs) for t in self.tracks]
