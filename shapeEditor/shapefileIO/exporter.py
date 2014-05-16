# This function takes a desired Shapefile object, 
# and return an HttpResponse that can be returned by the view function.
# This HttpResponse object will send the contents of the 
# exported shapefile back to the user's web browser,
# where it can be saved to disk.

from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from osgeo import osr
from osgeo import ogr
import os, os.path, tempfile, zipfile
from shapeEditor.shared import utils
import shutil, traceback

def export_data(shapefile):
# return "More to come..."
# Create a temporary directory to hold the shapefile's contents
    dst_dir = tempfile.mkdtemp()
    dst_file = str(os.path.join(dst_dir, shapefile.filename))
# Create a spatial reference for the shapefile to use, and 
# set up the shapefile's datasource and layer
    dst_spatial_ref = osr.SpatialReference()
    dst_spatial_ref.ImportFromWkt(shapefile.srs_wkt)
    driver = ogr.GetDriverByName("ESRI Shapefile")
    datasource = driver.CreateDataSource(dst_file)
    layer = datasource.CreateLayer(str(shapefile.filename),
                                   dst_spatial_ref)

# Define the various fields which will hold the shapefile's attributes.
# Django makes iterating over the shapefile's attributes 

    for attr in shapefile.attribute_set.all():
        field = ogr.FieldDefn(str(attr.name), attr.type)
        field.SetWidth(attr.width)
        field.SetPrecision(attr.precision)
        layer.CreateField(field)


# To transform the shapefile's features from the spatial reference 
# used internally (EPSG 4326) into the shapefile's own spatial reference.
# First, need to set up an osr.CoordinateTransformation object to do the transformation
    src_spatial_ref = osr.SpatialReference()
    src_spatial_ref.ImportFromEPSG(4326)
    coord_transform = osr.CoordinateTransformation(
                           src_spatial_ref, dst_spatial_ref)
#  Determine which geometry field in the Feature object holds the feature's geometry data
    geom_field = \
          utils.calc_geometry_field(shapefile.geom_type)

#  Exporting the shapefile's features
    for feature in shapefile.feature_set.all():
        geometry = getattr(feature, geom_field)

#  Need to unwrap the geometry so that features that have only one Polygon
#  or LineString in their geometries are saved as Polygons and LineStrings
#  rather than MultiPolygons and MultiLineStrings.
#  See utils.py function for unwrapping
        geometry = utils.unwrap_geos_geometry(geometry)

# Convert feature's geometry back into an OGR geometry again, 
# transform it into the shapefile's own spatial reference system, 
# and create an OGR feature using that geometry:
        dst_geometry = ogr.CreateGeometryFromWkt(geometry.wkt)
        dst_geometry.Transform(coord_transform)
        dst_feature = ogr.Feature(layer.GetLayerDefn())
        dst_feature.SetGeometry(dst_geometry)


# Save the attribute values associated with each feature by
# storing the string value into the OGR attribute field. See utils.py

        for attr_value in feature.attributevalue_set.all():
            utils.set_ogr_feature_attribute(
                        attr_value.attribute,
                        attr_value.value,
                        dst_feature,
                        shapefile.encoding)


# Add the feature to the layer and call the Destroy() method to
# save the feature (and then the layer) into the shapefile

        layer.CreateFeature(dst_feature)
        dst_feature.Destroy()
    datasource.Destroy()


# Compress exported data into an OGR shapefile into a ZIP archive
# Note: a temporary file, named temp, is used to store the ZIP
# archive's contents. It'll be returned to the user's web browser
# once the export process has finished


    temp = tempfile.TemporaryFile()
    zip = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
    
    shapefile_base = os.path.splitext(dst_file)[0]
    shapefile_name = os.path.splitext(shapefile.filename)[0]
    
    for fName in os.listdir(dst_dir):
        zip.write(os.path.join(dst_dir, fName), fName)
    zip.close()

# Deleting the shapefile that was created earlier
    shutil.rmtree(dst_dir)

# Send the ZIP archive to the user's web browser so that it can be
# downloaded onto the user's computer. To do this: create an
# HttpResponse object which includes a Django FileWrapper object
# to attach the ZIP archive to the HTTP response

    f = FileWrapper(temp)
    response = HttpResponse(f, content_type="application/zip")
    response['Content-Disposition'] = \
        "attachment; filename=" + shapefile_name + ".zip"
    response['Content-Length'] = temp.tell()
    temp.seek(0)
    return response
