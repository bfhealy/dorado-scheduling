#
# Copyright © 2021 United States Government as represented by the Administrator
# of the National Aeronautics and Space Administration. No copyright is claimed
# in the United States under Title 17, U.S. Code. All Other Rights Reserved.
#
# SPDX-License-Identifier: NASA-1.3
#
"""Configuration for different missions."""
from collections.abc import Collection
from dataclasses import dataclass
from importlib import resources

import astroplan
from astropy import units as u
import numpy as np

from . import data
from .constraints import (BrightEarthLimbConstraint, EarthLimbConstraint,
                          TrappedParticleFluxConstraint, get_field_of_regard)
from .fov import FOV
from .orbit import Orbit, Spice, TLE
from ._slew import slew_separation, slew_time

__all__ = ('Mission', 'dorado', 'ultrasat', 'uvex')


def _read_orbit(filename):
    with resources.path(data, filename) as p:
        return TLE(p)


@dataclass
class Mission:
    """Container for mission configuration."""

    constraints: Collection
    """Observing constraint."""

    fov: FOV
    """Field of view."""

    orbit: Orbit
    """The orbit."""

    min_overhead: u.Quantity
    """Minimum overhead between observations (readout and settling time)."""

    max_angular_velocity: u.Quantity
    """Maximum angular velocity for slews."""

    max_angular_acceleration: u.Quantity
    """Maximum angular acceleration for slews."""

    def get_field_of_regard(self, *args, **kwargs):
        return get_field_of_regard(self.orbit, self.constraints,
                                   *args, **kwargs)

    def overhead(self, *args, **kwargs):
        return np.maximum(self.min_overhead,
                          slew_time(slew_separation(*args, **kwargs),
                                    self.max_angular_velocity,
                                    self.max_angular_acceleration))


dorado = Mission(
    constraints=(
        TrappedParticleFluxConstraint(flux=1*u.cm**-2*u.s**-1,
                                      energy=20*u.MeV,
                                      particle='p', solar='max'),
        TrappedParticleFluxConstraint(flux=100*u.cm**-2*u.s**-1,
                                      energy=1*u.MeV,
                                      particle='e', solar='max'),
        BrightEarthLimbConstraint(28 * u.deg),
        EarthLimbConstraint(6 * u.deg),
        astroplan.SunSeparationConstraint(46 * u.deg),
        astroplan.MoonSeparationConstraint(23 * u.deg),
        astroplan.GalacticLatitudeConstraint(10 * u.deg)),
    fov=FOV.from_rectangle(7.1 * u.deg),
    orbit=_read_orbit('dorado-625km-sunsync.tle'),
    min_overhead=0 * u.s,
    max_angular_velocity=0.872 * u.deg / u.s,
    max_angular_acceleration=0.244 * u.deg / u.s**2
)
"""Configuration for Dorado.

Notes
-----
* The first trapped particle flux constraint is based on parameters for an
  `investigation that was done for Fermi LAT
  <https://inspirehep.net/literature/759859>`_.

* The second trapped particle flux constraint is designed to eliminate
  observations within the polar horns.

* Earth, Sun, and Moon constraints are based on the `Swift Technical Handbook
  <https://swift.gsfc.nasa.gov/proposals/tech_appd/swiftta_v14/node24.html>`_

* The orbit one of four synthetic plausible orbits generated by Craig
  Markwardt. It is a nearly circular sun-synchronous orbit at an altitude of
  625 km.

* The maximum angular acceleration and angular velocity about its three
  principal axes were given to us by the spacecraft vendor, but to be
  conservative we are using the smallest values.

* There is effectively no readout overhead because the Dorado uses frame
  transfer CCDs, so the previous image can be read out during an exposure.
"""


ultrasat = Mission(
    constraints=(
        EarthLimbConstraint(28 * u.deg),
        astroplan.SunSeparationConstraint(46 * u.deg),
        astroplan.MoonSeparationConstraint(23 * u.deg),
        astroplan.GalacticLatitudeConstraint(10 * u.deg)),
    fov=FOV.from_rectangle(14.1 * u.deg),
    orbit=_read_orbit('goes17.tle'),
    min_overhead=0 * u.s,
    max_angular_velocity=0.872 * u.deg / u.s,
    max_angular_acceleration=0.244 * u.deg / u.s**2
)
"""Configuration for ULTRASAT.

Notes
-----
* ULTRASAT is a proposed Israeli ultraviolet satellite. See the `ULTRASAT web
  site <http://www.weizmann.ac.il/ultrasat>`_ for details.

* The Earth, Sun, Moon, and Galactic plane constraints are assumed to be the
  same as those for Dorado.

* The ULTRASAT field of view has an area of 200 deg2, here assumed to be a
  square.

* ULTRASAT will be in a geosynchronous orbit. Here, we are using the orbital
  elements of GOES-17, a real geosynchronous weather satellite that is
  currently on orbit.

* Maximum angular acceleration, maximum angular velocity, and overhead time are
  assumed to be the same as for Dorado.
"""


uvex = Mission(
    constraints=(
        EarthLimbConstraint(25 * u.deg),
        astroplan.SunSeparationConstraint(46 * u.deg),
        astroplan.MoonSeparationConstraint(25 * u.deg)
    ),
    fov=FOV.from_rectangle(3.3 * u.deg),
    orbit=Spice(
        'MGS SIMULATION',
        'https://archive.stsci.edu/missions/tess/models/TESS_EPH_PRE_LONG_2021252_21.bsp',  # noqa: E501
        'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/earth_latest_high_prec.bpc',  # noqa: E501
        'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00010.tpc'),  # noqa: E501
    min_overhead=0 * u.s,
    max_angular_velocity=0.872 * u.deg / u.s,
    max_angular_acceleration=0.244 * u.deg / u.s**2
)
"""Configuration for UVEX.

Notes
-----
* UVEX is a MIDEX concept that is under development by Caltech.

* The Earth, Sun, and Moon constraints come from the baffle design
  (Brian Grefenstette, private communication). These constraints are
  appropriate for ToOs but not for the survey. The survey has stricter Earth
  and Moon constraints due to foreground sensitivity requirements.

* There is no Galactic plane constraints, because the UVEX mission will survey
  the Galactic plane.

* The orbit used is that of TESS, valid from 2021-10-09 13:00 to
  2023-03-11 13:00 UTC.

* Maximum angular acceleration, maximum angular velocity, and overhead time are
  assumed to be the same as for Dorado.
"""
