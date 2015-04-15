# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals, print_function

import os

import numpy as np

from astropy.io import fits

from .. import asdf
from .. import fits_embed

from .helpers import assert_tree_match


def test_embed_asdf_in_fits_file(tmpdir):
    hdulist = fits.HDUList()
    hdulist.append(fits.ImageHDU(np.arange(512, dtype=np.float), name='SCI'))
    hdulist.append(fits.ImageHDU(np.arange(512, dtype=np.float), name='DQ'))

    tree = {
        'model': {
            'sci': {
                'data': hdulist['SCI'].data,
                'wcs': 'WCS info'
            },
            'dq': {
                'data': hdulist['DQ'].data,
                'wcs': 'WCS info'
            }
        }
    }

    with fits_embed.AsdfInFits(hdulist, tree) as ff:
        ff.write_to(os.path.join(str(tmpdir), 'test.fits'))

    with fits.open(os.path.join(str(tmpdir), 'test.fits')) as hdulist2:
        assert len(hdulist2) == 3
        assert [x.name for x in hdulist2] == ['SCI', 'DQ', 'ASDF']

        ff2 = fits_embed.AsdfInFits.read(hdulist)

        assert_tree_match(tree, ff2.tree)

        with asdf.AsdfFile(ff2.tree) as ff:
            ff.write_to('test.asdf')

        with asdf.AsdfFile.read('test.asdf') as ff:
            assert_tree_match(tree, ff.tree)
