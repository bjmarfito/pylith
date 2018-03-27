// -*- C++ -*-
//
// ======================================================================
//
// Brad T. Aagaard, U.S. Geological Survey
// Charles A. Williams, GNS Science
// Matthew G. Knepley, University of Chicago
//
// This code was developed as part of the Computational Infrastructure
// for Geodynamics (http://geodynamics.org).
//
// Copyright (c) 2010-2017 University of California, Davis
//
// See COPYING for license information.
//
// ======================================================================
//

// SWIG interface
%module meshio

// Header files for module C++ code
%{
#include "pylith/meshio/MeshIO.hh"
#include "pylith/meshio/MeshIOAscii.hh"
#include "pylith/meshio/MeshIOLagrit.hh"
#if defined(ENABLE_CUBIT)
#include "pylith/meshio/MeshIOCubit.hh"
#endif

#include "pylith/meshio/VertexFilter.hh"
#include "pylith/meshio/VertexFilterDecimateP1.hh"
#include "pylith/meshio/CellFilter.hh"
#include "pylith/meshio/DataWriter.hh"
#include "pylith/meshio/DataWriterVTK.hh"
#include "pylith/meshio/OutputSolnSubset.hh"
#include "pylith/meshio/OutputSolnPoints.hh"
#if defined(ENABLE_HDF5)
#include "pylith/meshio/DataWriterHDF5.hh"
#include "pylith/meshio/DataWriterHDF5Ext.hh"
#endif
#include "pylith/meshio/OutputManager.hh"
#include "pylith/meshio/OutputSoln.hh"

#include "pylith/utils/arrayfwd.hh"
%}

%include "exception.i"
%exception {
  try {
    $action
  } catch (const std::exception& err) {
    SWIG_exception(SWIG_RuntimeError, err.what());
  } // try/catch
 } // exception

%include "std_string.i"
%include "typemaps.i"
%include "../include/scalartypemaps.i"
%include "../include/chararray.i"

// Numpy interface stuff
%{
#define SWIG_FILE_WITH_INIT
%}
%include "../include/numpy.i"
%init %{
import_array();
%}

// Interfaces
%include "MeshIOObj.i"
%include "MeshIOAscii.i"
%include "MeshIOLagrit.i"
#if defined(ENABLE_CUBIT)
%include "MeshIOCubit.i"
#endif

%include "VertexFilter.i"
%include "VertexFilterDecimateP1.i"
%include "CellFilter.i"
%include "DataWriter.i"
%include "DataWriterVTK.i"
%include "OutputSolnSubset.i"
%include "OutputSolnPoints.i"
#if defined(ENABLE_HDF5)
%include "DataWriterHDF5.i"
%include "DataWriterHDF5Ext.i"
#endif
%include "../utils/PyreComponent.i"
%include "OutputManager.i"
%include "OutputSoln.i"

// End of file
