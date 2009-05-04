#!/usr/bin/env python
#
# ======================================================================
#
#                           Brad T. Aagaard
#                        U.S. Geological Survey
#
# {LicenseText}
#
# ======================================================================
#

## @file unittests/pytests/materials/TestElasticStress1D.py

## @brief Unit testing of ElasticStress1D object.

import unittest

from pylith.materials.ElasticStress1D import ElasticStress1D

# ----------------------------------------------------------------------
class TestElasticStress1D(unittest.TestCase):
  """
  Unit testing of ElasticStress1D object.
  """

  def setUp(self):
    """
    Setup test subject.
    """
    self.material = ElasticStress1D()
    return
  

  def test_constructor(self):
    """
    Test constructor.
    """
    self.assertEqual(1, self.material.dimension())
    return


  def test_useElasticBehavior(self):
    """
    Test useElasticBehavior().
    """
    self.material.useElasticBehavior(False)
    return


  def testHasStateVars(self):
    self.failIf(self.material.hasStateVars())
    return


  def testTensorSize(self):
    self.assertEqual(1, self.material.tensorSize())
    return


  def testNeedNewJacobian(self):
    """
    Test needNewJacobian().
    """
    # Default should be False.
    self.failIf(self.material.needNewJacobian())

    # Changing time step should not require new Jacobian.
    self.material.timeStep(1.0)
    self.material.timeStep(2.0)
    self.failIf(self.material.needNewJacobian())
    return
  

# End of file 
