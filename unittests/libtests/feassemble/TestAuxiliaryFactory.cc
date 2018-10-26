// -*- C++ -*-
//
// ----------------------------------------------------------------------
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
// ----------------------------------------------------------------------
//

#include <portinfo>

#include "TestAuxiliaryFactory.hh" // Implementation of class methods

#include "pylith/feassemble/AuxiliaryFactory.hh" // Test subject

#include "pylith/topology/Mesh.hh" // USES Mesh
#include "pylith/topology/MeshOps.hh" // USES MeshOps
#include "pylith/topology/Field.hh" // USES Field
#include "pylith/meshio/MeshIOAscii.hh" // USES MeshIOAscii

#include "spatialdata/spatialdb/UserFunctionDB.hh" // USES UserFunctionDB
#include "spatialdata/geocoords/CSCart.hh" // USES CSCart
#include "spatialdata/units/Nondimensional.hh" // USES Nondimensional

// ---------------------------------------------------------------------------------------------------------------------
CPPUNIT_TEST_SUITE_REGISTRATION(pylith::feassemble::TestAuxiliaryFactory);

// ---------------------------------------------------------------------------------------------------------------------
namespace pylith {
    namespace feassemble {
        class _TestAuxiliaryFactory {
public:

            static double density(const double x,
                                  const double y) {
                return x+y;
            } // density

            static const char* density_units(void) {
                return "kg/m**3";
            } // density_units

            static double velocity_x(const double x,
                                     const double y) {
                return 2.0*x - 0.5*y;
            } // velocity_x

            static double velocity_y(const double x,
                                     const double y) {
                return 0.4*x + 0.1*y;
            } // velocity_x

            static const char* velocity_units(void) {
                return "m/s";
            } // velocity_units

        }; // class _TestAuxiliaryFactory
    } // feassemble
} // pylith

// ---------------------------------------------------------------------------------------------------------------------
// Setup testing data.
void
pylith::feassemble::TestAuxiliaryFactory::setUp(void) {
    _factory = new AuxiliaryFactory();
} // setUp


// ---------------------------------------------------------------------------------------------------------------------
// Tear down testing data.
void
pylith::feassemble::TestAuxiliaryFactory::tearDown(void) {
    delete _factory;_factory = NULL;
} // tearDown


// ---------------------------------------------------------------------------------------------------------------------
// Test setQueryDB() and getQueryDB().
void
pylith::feassemble::TestAuxiliaryFactory::testQueryDB(void) {
    spatialdata::spatialdb::UserFunctionDB db;
    const std::string& dbLabel = "test database";
    db.label(dbLabel.c_str());

    CPPUNIT_ASSERT(_factory);
    CPPUNIT_ASSERT_MESSAGE("Default spatial database should be NULL.", !_factory->getQueryDB());
    _factory->setQueryDB(&db);

    const spatialdata::spatialdb::SpatialDB* dbTest = _factory->getQueryDB();
    CPPUNIT_ASSERT(dbTest);
    CPPUNIT_ASSERT_EQUAL(dbLabel, std::string(dbTest->label()));
} // testQueryDB


// ---------------------------------------------------------------------------------------------------------------------
// Test setSubfieldDiscretization() and getSubfieldDiscretization().
void
pylith::feassemble::TestAuxiliaryFactory::testSubfieldDiscretization(void) {
    pylith::topology::FieldBase::Discretization feDisp(2, 2, true, pylith::topology::FieldBase::POLYNOMIAL_SPACE);
    pylith::topology::FieldBase::Discretization feVel(3, 2, false, pylith::topology::FieldBase::POINT_SPACE);

    CPPUNIT_ASSERT(_factory);
    _factory->setSubfieldDiscretization("displacement", feDisp.basisOrder, feDisp.quadOrder, feDisp.isBasisContinuous, feDisp.feSpace);
    _factory->setSubfieldDiscretization("velocity", feVel.basisOrder, feVel.quadOrder, feVel.isBasisContinuous, feVel.feSpace);

    { // Check displacement discretization
        const pylith::topology::FieldBase::Discretization& feTest = _factory->getSubfieldDiscretization("displacement");
        CPPUNIT_ASSERT_EQUAL(feDisp.basisOrder, feTest.basisOrder);
        CPPUNIT_ASSERT_EQUAL(feDisp.quadOrder, feTest.quadOrder);
        CPPUNIT_ASSERT_EQUAL(feDisp.isBasisContinuous, feTest.isBasisContinuous);
        CPPUNIT_ASSERT_EQUAL(feDisp.feSpace, feTest.feSpace);
    } // Check displacement discretization

    { // Check velocity discretization
        const pylith::topology::FieldBase::Discretization& feTest = _factory->getSubfieldDiscretization("velocity");
        CPPUNIT_ASSERT_EQUAL(feVel.basisOrder, feTest.basisOrder);
        CPPUNIT_ASSERT_EQUAL(feVel.quadOrder, feTest.quadOrder);
        CPPUNIT_ASSERT_EQUAL(feVel.isBasisContinuous, feTest.isBasisContinuous);
        CPPUNIT_ASSERT_EQUAL(feVel.feSpace, feTest.feSpace);
    } // Check velocity discretization
} // testSubfieldDiscretization


// ---------------------------------------------------------------------------------------------------------------------
// Test initialize().
void
pylith::feassemble::TestAuxiliaryFactory::testInitialize(void) {
    pylith::topology::Mesh mesh;
    pylith::topology::Field field(mesh);

    const int spaceDim = 2;
    spatialdata::units::Nondimensional normalizer;
    normalizer.lengthScale(10.0);

    pylith::topology::Field::Description description;
    description.label = "displacement";
    description.alias = "disp";
    description.vectorFieldType = pylith::topology::Field::SCALAR;
    description.numComponents = 1;
    description.componentNames.resize(1);
    description.componentNames[0] = "displacement_x";
    description.scale = normalizer.lengthScale();

    CPPUNIT_ASSERT(_factory);
    _factory->initialize(&field, normalizer, spaceDim, &description);

    CPPUNIT_ASSERT_EQUAL(&field, _factory->_field);
    CPPUNIT_ASSERT_EQUAL(spaceDim, _factory->_spaceDim);
    CPPUNIT_ASSERT_EQUAL(normalizer.lengthScale(), _factory->_normalizer->lengthScale());

    const pylith::topology::Field::Description* descriptionTest = _factory->_defaultDescription;
    CPPUNIT_ASSERT_EQUAL(description.label, descriptionTest->label);
    CPPUNIT_ASSERT_EQUAL(description.alias, descriptionTest->alias);
    CPPUNIT_ASSERT_EQUAL(description.vectorFieldType, descriptionTest->vectorFieldType);
    CPPUNIT_ASSERT_EQUAL(description.numComponents, descriptionTest->numComponents);
    CPPUNIT_ASSERT_EQUAL(description.numComponents, descriptionTest->componentNames.size());
    CPPUNIT_ASSERT_EQUAL(description.componentNames[0], descriptionTest->componentNames[0]);
    CPPUNIT_ASSERT_EQUAL(description.scale, descriptionTest->scale);
    CPPUNIT_ASSERT_EQUAL(description.validator, descriptionTest->validator);

    CPPUNIT_ASSERT(_factory->_fieldQuery);
} // testInitialize


// ---------------------------------------------------------------------------------------------------------------------
// Test setValuesFromDB().
void
pylith::feassemble::TestAuxiliaryFactory::testSetValuesFromDB(void) {
    const int spaceDim = 2;
    spatialdata::units::Nondimensional normalizer;
    normalizer.lengthScale(10.0);
    normalizer.densityScale(2.0);

    spatialdata::geocoords::CSCart cs;
    cs.setSpaceDim(spaceDim);
    cs.initialize();

    const int numSubfields = 2;
    static const char* subfields[2] = { "density", "velocity" };
    static const pylith::topology::Field::Discretization subfieldDiscretizations[2] = {
        pylith::topology::Field::Discretization(1, 2), // density
        pylith::topology::Field::Discretization(2, 2), // velocity
    };

    pylith::topology::Field::Description descriptionDensity;
    descriptionDensity.label = "density";
    descriptionDensity.alias = "density";
    descriptionDensity.vectorFieldType = pylith::topology::Field::SCALAR;
    descriptionDensity.numComponents = 1;
    descriptionDensity.componentNames.resize(1);
    descriptionDensity.componentNames[0] = "density";
    descriptionDensity.scale = normalizer.densityScale();

    pylith::topology::Field::Description descriptionVelocity;
    descriptionVelocity.label = "velocity";
    descriptionVelocity.alias = "velocity";
    descriptionVelocity.vectorFieldType = pylith::topology::Field::VECTOR;
    descriptionVelocity.numComponents = 2;
    descriptionVelocity.componentNames.resize(2);
    descriptionVelocity.componentNames[0] = "velocity_x";
    descriptionVelocity.componentNames[1] = "velocity_y";
    descriptionVelocity.scale = normalizer.lengthScale() / normalizer.timeScale();

    pylith::topology::Field::Description subfieldDescriptions[2];
    subfieldDescriptions[0] = descriptionDensity;
    subfieldDescriptions[1] = descriptionVelocity;

    spatialdata::spatialdb::UserFunctionDB auxiliaryDB;
    auxiliaryDB.addValue("density", _TestAuxiliaryFactory::density, _TestAuxiliaryFactory::density_units());
    auxiliaryDB.addValue("velocity_x", _TestAuxiliaryFactory::velocity_x, _TestAuxiliaryFactory::velocity_units());
    auxiliaryDB.addValue("velocity_y", _TestAuxiliaryFactory::velocity_y, _TestAuxiliaryFactory::velocity_units());
    auxiliaryDB.coordsys(cs);

    pylith::topology::Mesh mesh;
    pylith::meshio::MeshIOAscii iohandler;
    iohandler.filename("data/tri.mesh");
    iohandler.read(&mesh);
    mesh.coordsys(&cs);
    pylith::topology::MeshOps::nondimensionalize(&mesh, normalizer);

    CPPUNIT_ASSERT_MESSAGE("Test mesh does not contain any cells.", mesh.numCells() > 0);
    CPPUNIT_ASSERT_MESSAGE("Test mesh does not contain any vertices.", mesh.numVertices() > 0);

    CPPUNIT_ASSERT(_factory);
    _factory->setQueryDB(&auxiliaryDB);

    pylith::topology::Field auxiliaryField(mesh);
    _factory->initialize(&auxiliaryField, normalizer, spaceDim);
    for (int i = 0; i < numSubfields; ++i) {
        auxiliaryField.subfieldAdd(subfieldDescriptions[i], subfieldDiscretizations[i]);
        _factory->_setSubfieldQueryFn(subfields[i], pylith::topology::FieldQuery::dbQueryGeneric);
    } // for
    auxiliaryField.subfieldsSetup();
    auxiliaryField.allocate();
    auxiliaryField.zeroLocal();

    _factory->setValuesFromDB();

    // Verify auxiliary field
    PylithReal norm = 0.0;
    PylithReal t = 0.0;
    const PetscDM dmField = auxiliaryField.dmMesh();CPPUNIT_ASSERT(dmField);
    pylith::topology::FieldQuery query(auxiliaryField);
    query.initializeWithDefaultQueryFns();
    query.openDB(&auxiliaryDB, normalizer.lengthScale());
    PetscErrorCode err = DMPlexComputeL2DiffLocal(dmField, t, query.functions(), (void**)query.contextPtrs(), auxiliaryField.localVector(), &norm);CPPUNIT_ASSERT(!err);
    query.closeDB(&auxiliaryDB);
    const PylithReal tolerance = 1.0e-6;
    CPPUNIT_ASSERT_DOUBLES_EQUAL_MESSAGE("Test of auxiliary field values failed.", 0.0, norm, tolerance);
} // testSetValuesFromDB


// End of file
