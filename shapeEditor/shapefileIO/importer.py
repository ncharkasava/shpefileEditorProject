# This function reads the contents of the UploadedFile object 
# and stores it in a temporary file on disk so that we can work with it

# It uses the tempfile module from the Python standard library to
# create a temporary file, and then copy the contents of the shapefile
# object into it.

# Import Python standard library modules used in this code
import os, os.path, tempfile, zipfile

# Use the traceback library module to display
# debugging information in the web server's log, 
# while returning a friendly error message that will be shown to the user.

import shutil, traceback
from osgeo import ogr
from osgeo import osr

from shapeEditor.shared.models import Shapefile
from shapeEditor.shared.models import Attribute
from shapeEditor.shared.models import Feature
from shapeEditor.shared.models import AttributeValue
from shapeEditor.shared import utils

from django.contrib.gis.geos.geometry import GEOSGeometry


from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.core.context_processors import csrf




def import_data(request, shapefile, character_encoding):
    #return "More to come..."
    fd,fname = tempfile.mkstemp(suffix=".zip")

# tempfile.mkstemp() returns both a file descriptor and a filename, we call
# os.close(fd) to close the file descriptor. This allows us to reopen the
# file using open() and write to it in the normal way.
    os.close(fd)

    f = open(fname, "wb")
    for chunk in shapefile.chunks():
        f.write(chunk)
    f.close()

# Use the Python standard library's zipfile module to check the
# contents of the uploaded ZIP archive, and return a suitable error message
# if something is wrong

    if not zipfile.is_zipfile(fname):
        os.remove(fname)
        return "Not a valid zip archive."
    zip = zipfile.ZipFile(fname)
    required_suffixes = [".shp", ".shx", ".dbf", ".prj"]
    has_suffix = {}
    for suffix in required_suffixes:
        has_suffix[suffix] = False

    for info in zip.infolist():
        extension = os.path.splitext(info.filename)[1].lower()
        if extension in required_suffixes:
            has_suffix[extension] = True

    for suffix in required_suffixes:
        if not has_suffix[suffix]:
            zip.close()
# Delete the temporary file before returning
# an error message, so that we don't leave temporary files lying around
            os.remove(fname)
            return "Archive missing required "+suffix+" file."
# When it's known that the uploaded file is a valid ZIP archive containing
# the files that make up a shapefile, extract these files and store them
# into a temporary directory

    shapefile_name = None
    dst_dir = tempfile.mkdtemp()
    for info in zip.infolist():
        if info.filename.endswith(".shp"):
            shapefile_name = info.filename
        dst_file = os.path.join(dst_dir, info.filename)
        f = open(dst_file, "wb")
        f.write(zip.read(info.filename))
        f.close()
    zip.close()

    
# Open the shapefile
    try:
        datasource = ogr.Open(os.path.join(dst_dir, shapefile_name))
        layer = datasource.GetLayer(0)
        shapefileOK = True
    except:
        traceback.print_exc()
        shapefileOK = False

# if something goes wrong - clean up our temporary files and return a
# suitable error message. 
        if not shapefileOK:
            os.remove(fname)
            shutil.rmtree(dst_dir)
            return "Not a valid shapefile."

# If the shapefile was opened sucessfully - read the data out
# of it. Create the Shapefile object to represent this imported shapefile.
# Get the spatial reference from the shapefile's layer, and then store
# the shapefile's name, spatial reference, and encoding into a Shapefile
# object. The geom_type field is supposed to hold the name of the geometry
# type that this shapefile holds but can't get the name of the geometry
# directly using OGR. Need to implement our own version of
# OGRGeometryTypeToName(). See utils.py module in shared app directory


    src_spatial_ref = layer.GetSpatialRef()
    geometry_type = layer.GetLayerDefn().GetGeomType()
    geometry_name = utils.ogr_type_to_geometry_name(geometry_type)
    curr_user = request.user

    shapefile = Shapefile(filename=shapefile_name,
                          srs_wkt=src_spatial_ref.ExportToWkt(),
                          geom_type=geometry_name,
                          encoding=character_encoding,
                          owner=curr_user)
    shapefile.save()

# Create Attribute objects describing the shapefile's attributes
# Save the Attribute objects into a database and create a
# separate list of these attributes in a variable named attributes.
# Needed for import the attribute values for each feature.

    attributes = []
    layer_def = layer.GetLayerDefn()
    for i in range(layer_def.GetFieldCount()):
        field_def = layer_def.GetFieldDefn(i)
        attr = Attribute(
                shapefile=shapefile,
                name=field_def.GetName(),
                type=field_def.GetType(),
                width=field_def.GetWidth(),
                precision=field_def.GetPrecision())
        attr.save()
        attributes.append(attr)

# Extract the shapefile's features and store them as Feature objects
# in the database. Because the shapefile's features can be in any spatial
# reference, we need to transform them into our internal spatial reference
# system (EPSG 4326, unprojected latitude, and longitude values) before we
# can store them. To do this, use an OGR CoordinateTransformation() object.
# GEOS geometry object caan be stored into the Feature object.

    dst_spatial_ref = osr.SpatialReference()
    dst_spatial_ref.ImportFromEPSG(4326)
    coord_transform = osr.CoordinateTransformation(src_spatial_ref,
                                     dst_spatial_ref)
    for i in range(layer.GetFeatureCount()):
        src_feature = layer.GetFeature(i)
        # src_name = src_feature.name;
        src_geometry = src_feature.GetGeometryRef()
        src_geometry.Transform(coord_transform)
        geometry = GEOSGeometry(src_geometry.ExportToWkt())
# See wrap geometry in utils: it distinguish polygons and multipoligon,
# linestring and multilinestrings
        geometry = utils.wrap_geos_geometry(geometry)

# Can't simply use the geometry name to identify the field because
# sometimes have to wrap up geometries. See utils.py.

        geometry_field = utils.calc_geometry_field(geometry_name)

# Store the feature's geometry into a Feature object within the database
# Note: Use keyword arguments (**args) to create the Feature object.
# This lets to store the geometry into the correct field of the Feature
# object with a minimum of fuss. 

        args = {}
        args['shapefile'] = shapefile
        args[geometry_field] = geometry
        feature = Feature(**args)
        feature.save()

        for attr in attributes:
            success,result = utils.getOGRFeatureAttribute(
                    attr,
                    src_feature,
                    character_encoding)
            if not success:
               os.remove(fname)
               shutil.rmtree(dst_dir)
               shapefile.delete()
               return result

            attr_value = AttributeValue(
                    feature=feature,
                    attribute=attr,
                    value=result)
            attr_value.save()

    os.remove(fname)
    shutil.rmtree(dst_dir)
    return None


