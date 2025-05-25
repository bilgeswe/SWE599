"""
Tests for the OpenDRIVE validator.
"""

import os
import pytest
from pathlib import Path
import xml.etree.ElementTree as ET
from src.validation.validator import OpenDriveValidator, ValidationResult

@pytest.fixture
def validator():
    """Create a validator instance for testing."""
    return OpenDriveValidator()

@pytest.fixture
def test_data_dir(tmp_path):
    """Create a temporary directory with test files."""
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()
    return data_dir

@pytest.fixture
def valid_opendrive(test_data_dir):
    """Create a valid OpenDRIVE file for testing."""
    file_path = test_data_dir / "valid.xodr"
    content = '''<?xml version="1.0" encoding="UTF-8"?>
<OpenDRIVE>
    <header revMajor="1" revMinor="7" name="Test Road" version="1.0" date="2024-04-30" north="0" south="0" east="0" west="0"/>
    <road name="Road1" length="100.0" id="1" junction="-1">
        <link/>
        <planView>
            <geometry s="0.0" x="0.0" y="0.0" hdg="0.0" length="100.0">
                <line/>
            </geometry>
        </planView>
        <lanes>
            <laneSection s="0.0">
                <center>
                    <lane id="0" type="none" level="false">
                        <link/>
                    </lane>
                </center>
                <right>
                    <lane id="-1" type="driving" level="false">
                        <link/>
                        <width sOffset="0.0" a="3.5" b="0.0" c="0.0" d="0.0"/>
                    </lane>
                </right>
            </laneSection>
        </lanes>
    </road>
</OpenDRIVE>'''
    file_path.write_text(content)
    return file_path

@pytest.fixture
def invalid_opendrive(test_data_dir):
    """Create an invalid OpenDRIVE file for testing."""
    file_path = test_data_dir / "invalid.xodr"
    content = '''<?xml version="1.0" encoding="UTF-8"?>
<OpenDRIVE>
    <header revMajor="1" revMinor="7"/>
    <road name="Road1" length="100.0" id="1">
        <invalidTag/>
    </road>
</OpenDRIVE>'''
    file_path.write_text(content)
    return file_path

@pytest.fixture
def geometry_error_opendrive(test_data_dir):
    """Create an OpenDRIVE file with geometry errors for testing."""
    file_path = test_data_dir / "geometry_error.xodr"
    content = '''<?xml version="1.0" encoding="UTF-8"?>
<OpenDRIVE>
    <header revMajor="1" revMinor="7" name="Test Road" version="1.0" date="2024-04-30" north="0" south="0" east="0" west="0"/>
    <road name="Road1" length="150.0" id="1" junction="-1">
        <planView>
            <geometry s="0.0" x="0.0" y="0.0" hdg="0.0" length="100.0">
                <line/>
            </geometry>
        </planView>
        <lanes>
            <laneSection s="0.0">
                <right>
                    <lane id="-1" type="driving" level="false">
                        <width sOffset="0.0" a="3.5" b="0.0" c="0.0" d="0.0"/>
                        <width sOffset="50.0" a="4.0" b="0.0" c="0.0" d="0.0"/>
                    </lane>
                </right>
            </laneSection>
        </lanes>
    </road>
</OpenDRIVE>'''
    file_path.write_text(content)
    return file_path

def test_schema_validation_valid(validator, valid_opendrive):
    """Test schema validation with a valid OpenDRIVE file."""
    result = validator.validate_schema(str(valid_opendrive))
    assert result.is_valid
    assert not result.errors
    assert not result.warnings

def test_schema_validation_invalid(validator, invalid_opendrive):
    """Test schema validation with an invalid OpenDRIVE file."""
    result = validator.validate_schema(str(invalid_opendrive))
    assert not result.is_valid
    assert result.errors
    assert not result.warnings

def test_geometry_validation_length_mismatch(validator, geometry_error_opendrive):
    """Test geometry validation with length mismatch."""
    result = validator.validate_geometry(str(geometry_error_opendrive))
    assert not result.is_valid
    assert any("Length mismatch" in error for error in result.errors)

def test_geometry_validation_lane_width(validator, geometry_error_opendrive):
    """Test geometry validation for lane width discontinuities."""
    result = validator.validate_geometry(str(geometry_error_opendrive))
    assert any("width discontinuity" in warning for warning in result.warnings)

def test_visualization(validator, valid_opendrive, test_data_dir):
    """Test visualization of OpenDRIVE files."""
    output_file = test_data_dir / "comparison.png"
    validator.visualize_comparison(
        str(valid_opendrive),
        str(valid_opendrive),
        str(output_file)
    )
    assert output_file.exists()

def test_nonexistent_file(validator):
    """Test validation with a nonexistent file."""
    result = validator.validate_schema("nonexistent.xodr")
    assert not result.is_valid
    assert result.errors
    assert "Validation error" in result.errors[0]

def test_invalid_xml(test_data_dir, validator):
    """Test validation with invalid XML."""
    file_path = test_data_dir / "invalid_xml.xodr"
    file_path.write_text("This is not XML")
    result = validator.validate_schema(str(file_path))
    assert not result.is_valid
    assert result.errors 