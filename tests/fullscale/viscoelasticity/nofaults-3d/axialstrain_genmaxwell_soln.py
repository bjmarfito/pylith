# =================================================================================================
# This code is part of PyLith, developed through the Computational Infrastructure
# for Geodynamics (https://github.com/geodynamics/pylith).
#
# Copyright (c) 2010-2025, University of California, Davis and the PyLith Development Team.
# All rights reserved.
#
# See https://mit-license.org/ and LICENSE.md and for license information. 
# =================================================================================================
# @file tests/fullscale/viscoelasticity/nofaults-3d/axialstrain_genmaxwell_soln.py
#
# @brief Analytical solution to axial strain relaxation problem for a generalized Maxwell viscoelastic material.
#
# 3-D axial strain solution for linear generalized Maxwell viscoelastic material.
#
#             Uz=U0
#          ----------
#          |        |
# Ux=0     |        |  Ux=0
#          |        |
#          |        |
#          ----------
#            Uz=0
#
# Dirichlet boundary conditions
# Ux(-4000,y,z) = 0
# Ux(+4000,y,z) = 0
# Uy(x,-4000,z) = 0
# Uy(x,+4000,z) = 0
# Uz(x,y,-8000) = 0
# Uz(x,y,+0) = U0
#

import numpy

# Physical properties.
p_density = 2500.0
p_vs = 3464.1016
p_vp = 6000.0
p_viscosity_1 = 9.46728e17
p_viscosity_2 = 4.73364e17
p_viscosity_3 = 1.893456e18
p_shear_ratio_1 = 0.25
p_shear_ratio_2 = 0.25
p_shear_ratio_3 = 0.25

# Applied displacement.
U0 = 1.0

# Derived properties.
p_mu = p_density*p_vs*p_vs
p_lambda = p_density*p_vp*p_vp - 2.0*p_mu
p_youngs = p_mu*(3.0*p_lambda + 2.0*p_mu)/(p_lambda + p_mu)
p_poissons = 0.5*p_lambda/(p_lambda + p_mu)
p_shear_ratio_0 = 1.0 - p_shear_ratio_1 - p_shear_ratio_2 - p_shear_ratio_3
p_tau_1 = p_viscosity_1/(p_mu*p_shear_ratio_1)
p_tau_2 = p_viscosity_2/(p_mu*p_shear_ratio_2)
p_tau_3 = p_viscosity_3/(p_mu*p_shear_ratio_3)

# Time information.
year = 60.0*60.0*24.0*365.25
dt = 0.025*year
startTime = dt
endTime = 0.5*year
numSteps = 20
timeArray = numpy.linspace(startTime, endTime, num=numSteps, dtype=numpy.float64)

# Uniform strain field (3D).
e0 = U0/8000.0
exx = numpy.zeros(numSteps, dtype=numpy.float64)
eyy = numpy.zeros(numSteps, dtype=numpy.float64)
ezz = e0*numpy.ones(numSteps, dtype=numpy.float64)
exy = numpy.zeros(numSteps, dtype=numpy.float64)
eyz = numpy.zeros(numSteps, dtype=numpy.float64)
exz = numpy.zeros(numSteps, dtype=numpy.float64)

# Deviatoric strains.
eMean = (exx + eyy + ezz)/3.0
eDevxx = exx - eMean
eDevyy = eyy - eMean
eDevzz = ezz - eMean
eDevxy = exy
eDevyz = eyz
eDevxz = exz

# Deviatoric stresses.
timeFac1 = numpy.exp(-timeArray/p_tau_1)
timeFac2 = numpy.exp(-timeArray/p_tau_2)
timeFac3 = numpy.exp(-timeArray/p_tau_3)
sDevxx = 2.0*p_mu*eDevxx*(p_shear_ratio_0 + p_shear_ratio_1*timeFac1 + p_shear_ratio_2*timeFac2 + p_shear_ratio_3*timeFac3)
sDevyy = 2.0*p_mu*eDevyy*(p_shear_ratio_0 + p_shear_ratio_1*timeFac1 + p_shear_ratio_2*timeFac2 + p_shear_ratio_3*timeFac3)
sDevzz = 2.0*p_mu*eDevzz*(p_shear_ratio_0 + p_shear_ratio_1*timeFac1 + p_shear_ratio_2*timeFac2 + p_shear_ratio_3*timeFac3)
sDevxy = numpy.zeros_like(sDevxx)
sDevyz = numpy.zeros_like(sDevxx)
sDevxz = numpy.zeros_like(sDevxx)

# Total stresses.
sMean = e0*(3.0*p_lambda + 2.0*p_mu)/3.0
sxx = sDevxx + sMean
syy = sDevyy + sMean
szz = sDevzz + sMean
sxy = sDevxy
syz = sDevyz
sxz = sDevxz

# Get viscous strains from initial deviatoric strains (strain rate = 0).
eVisxx_1 = eDevxx*timeFac1
eVisyy_1 = eDevyy*timeFac1
eViszz_1 = eDevzz*timeFac1
eVisxy_1 = eDevxy
eVisyz_1 = eDevyz
eVisxz_1 = eDevxz
eVisxx_2 = eDevxx*timeFac2
eVisyy_2 = eDevyy*timeFac2
eViszz_2 = eDevzz*timeFac2
eVisxy_2 = eDevxy
eVisyz_2 = eDevyz
eVisxz_2 = eDevxz
eVisxx_3 = eDevxx*timeFac3
eVisyy_3 = eDevyy*timeFac3
eViszz_3 = eDevzz*timeFac3
eVisxy_3 = eDevxy
eVisyz_3 = eDevyz
eVisxz_3 = eDevxz

# ----------------------------------------------------------------------
class AnalyticalSoln(object):
    """Analytical solution to axial extension problem.
    """
    SPACE_DIM = 3
    TENSOR_SIZE = 6

    def __init__(self):
        self.fields = {
            "displacement": self.displacement,
            "density": self.density,
            "shear_modulus": self.shear_modulus,
            "bulk_modulus": self.bulk_modulus,
            "shear_modulus_ratio": self.shear_modulus_ratio,
            "maxwell_time": self.maxwell_time,
            "cauchy_strain": self.strain,
            "cauchy_stress": self.stress,
            "viscous_strain": self.viscous_strain,
            "initial_amplitude": self.initial_displacement,
        }
        return

    def getField(self, name, mesh_entity, pts):
        field = self.fields[name](pts)
        return field

    def displacement(self, locs):
        """Compute displacement field at locations.
        """
        (npts, dim) = locs.shape
        disp = numpy.zeros((numSteps, npts, self.SPACE_DIM), dtype=numpy.float64)
        disp[:,:, 2] = numpy.dot(ezz.reshape(numSteps, 1), (locs[:, 2] + 8000.0).reshape(1, npts))
        above = numpy.where(locs[:, 2] > -0.1)
        below = numpy.where(locs[:, 2] < -7999.9)
        disp[:, above, 2] = U0
        disp[:, below, 2] = 0.0
        return disp

    def initial_displacement(self, locs):
        """Compute initial displacement field at locations.
        """
        (npts, dim) = locs.shape
        disp = numpy.zeros((1, npts, self.SPACE_DIM), dtype=numpy.float64)
        disp[0,:, 2] = e0*(locs[:, 2] + 8000.0).reshape(1, npts)
        above = numpy.where(locs[:, 2] > -0.1)
        below = numpy.where(locs[:, 2] < -7999.9)
        disp[0, above, 2] = U0
        disp[0, below, 2] = 0.0
        return disp

    def density(self, locs):
        """Compute density field at locations.
        """
        (npts, dim) = locs.shape
        density = p_density * numpy.ones((1, npts, 1), dtype=numpy.float64)
        return density

    def shear_modulus(self, locs):
        """Compute shear modulus field at locations.
        """
        (npts, dim) = locs.shape
        shear_modulus = p_mu * numpy.ones((1, npts, 1), dtype=numpy.float64)
        return shear_modulus

    def bulk_modulus(self, locs):
        """Compute bulk modulus field at locations.
        """
        (npts, dim) = locs.shape
        bulk_modulus = (p_lambda + 2.0 / 3.0 * p_mu) * numpy.ones((1, npts, 1), dtype=numpy.float64)
        return bulk_modulus

    def maxwell_time(self, locs):
        """Compute Maxwell time field at locations.
        """
        (npts, dim) = locs.shape
        maxwell_time = numpy.zeros((1, npts, 3), dtype=numpy.float64)
        maxwell_time[0,:, 0] = p_tau_1
        maxwell_time[0,:, 1] = p_tau_2
        maxwell_time[0,:, 2] = p_tau_3
        return maxwell_time

    def shear_modulus_ratio(self, locs):
        """Compute shear modulus ratio field at locations.
        """
        (npts, dim) = locs.shape
        shear_modulus_ratio = numpy.zeros((1, npts, 3), dtype=numpy.float64)
        shear_modulus_ratio[0,:, 0] = p_shear_ratio_1
        shear_modulus_ratio[0,:, 1] = p_shear_ratio_2
        shear_modulus_ratio[0,:, 2] = p_shear_ratio_3
        return shear_modulus_ratio

    def strain(self, locs):
        """Compute strain field at locations.
        """
        (npts, dim) = locs.shape
        strain = numpy.zeros((numSteps, npts, self.TENSOR_SIZE), dtype=numpy.float64)
        strain[:,:, 0] = exx.reshape(numSteps, 1)
        strain[:,:, 1] = eyy.reshape(numSteps, 1)
        strain[:,:, 2] = ezz.reshape(numSteps, 1)
        strain[:,:, 3] = exy.reshape(numSteps, 1)
        strain[:,:, 4] = eyz.reshape(numSteps, 1)
        strain[:,:, 5] = exz.reshape(numSteps, 1)
        return strain

    def stress(self, locs):
        """Compute stress field at locations.
        """
        (npts, dim) = locs.shape
        stress = numpy.zeros((numSteps, npts, self.TENSOR_SIZE), dtype=numpy.float64)
        stress[:,:, 0] = sxx.reshape(numSteps, 1)
        stress[:,:, 1] = syy.reshape(numSteps, 1)
        stress[:,:, 2] = szz.reshape(numSteps, 1)
        stress[:,:, 3] = sxy.reshape(numSteps, 1)
        stress[:,:, 4] = syz.reshape(numSteps, 1)
        stress[:,:, 5] = sxz.reshape(numSteps, 1)
        return stress

    def viscous_strain(self, locs):
        """Compute viscous strain field at locations.
        """
        (npts, dim) = locs.shape
        viscous_strain = numpy.zeros((numSteps, npts, 3*self.TENSOR_SIZE), dtype=numpy.float64)
        viscous_strain[:,:, 0] = eVisxx_1.reshape(numSteps, 1)
        viscous_strain[:,:, 1] = eVisyy_1.reshape(numSteps, 1)
        viscous_strain[:,:, 2] = eViszz_1.reshape(numSteps, 1)
        viscous_strain[:,:, 3] = eVisxy_1.reshape(numSteps, 1)
        viscous_strain[:,:, 4] = eVisyz_1.reshape(numSteps, 1)
        viscous_strain[:,:, 5] = eVisxz_1.reshape(numSteps, 1)
        viscous_strain[:,:, 6] = eVisxx_2.reshape(numSteps, 1)
        viscous_strain[:,:, 7] = eVisyy_2.reshape(numSteps, 1)
        viscous_strain[:,:, 8] = eViszz_2.reshape(numSteps, 1)
        viscous_strain[:,:, 9] = eVisxy_2.reshape(numSteps, 1)
        viscous_strain[:,:, 10] = eVisyz_2.reshape(numSteps, 1)
        viscous_strain[:,:, 11] = eVisxz_2.reshape(numSteps, 1)
        viscous_strain[:,:, 12] = eVisxx_3.reshape(numSteps, 1)
        viscous_strain[:,:, 13] = eVisyy_3.reshape(numSteps, 1)
        viscous_strain[:,:, 14] = eViszz_3.reshape(numSteps, 1)
        viscous_strain[:,:, 15] = eVisxy_3.reshape(numSteps, 1)
        viscous_strain[:,:, 16] = eVisyz_3.reshape(numSteps, 1)
        viscous_strain[:,:, 17] = eVisxz_3.reshape(numSteps, 1)
        return viscous_strain


# End of file
