from django.http import HttpResponse
import traceback
from django.http import Http404
from shapeEditor.shared.models import Shapefile
from shapeEditor.shared.models import Feature
import math
from django.conf import settings
import mapnik2
from shapeEditor.shared import utils


# constants to define the size of each map tile, zoom levels supported
MAX_ZOOM_LEVEL = 10
TILE_WIDTH = 256
TILE_HEIGHT = 256

def root(request):
# This view function returns an XML-format response describing the one-and-only Tile Map Service supported by our TMS server. This Tile Map Service is identified by a version number, 1.0 (Tile Map Services are typically identified by version number). OpenLayers will use this to access our Tile Map Service.
# By wrapping our Python code in a try...except statement, we can catch any exceptions in our Python code and print them out. This is a useful technique to use whenever you write AJAX request handlers in Python.
 
    try:
        baseURL = request.build_absolute_uri()
        xml = []
        xml.append('<?xml version="1.0" encoding="utf-8" ?>')
        xml.append('<Services>')
        xml.append(' <TileMapService ' +
                   'title="ShapeEditor Tile Map Service" ' +
                   'version="1.0" href="' + baseURL + '/1.0"/>')
        xml.append('</Services>')
        return HttpResponse("\n".join(xml), mimetype="text/xml")
    except:
        traceback.print_exc()
        return HttpResponse("Error")

# Assuming the version number is correct, we iterate over the various Shapefile
# objects in the database, listing each uploaded shapefile as a Tile Map.

def service(request, version):
    try:
        if version != "1.0":
            raise Http404

        baseURL = request.build_absolute_uri()
        xml = []
        xml.append('<?xml version="1.0" encoding="utf-8" ?>')
        xml.append('<TileMapService version="1.0" services="' +
                   baseURL + '">')
        xml.append('    <Title>ShapeEditor Tile Map Service' +
                   '</Title>')
        xml.append('    <Abstract></Abstract>')
        xml.append('    <TileMaps>')
        for shapefile in Shapefile.objects.all():
            id = str(shapefile.id)
            xml.append('    <TileMap title="' +
                       shapefile.filename + '"')
            xml.append('        srs="EPSG:4326"')
            xml.append('        href="'+baseURL+'/'+id+'"/>')
        xml.append(' </TileMaps>')
        xml.append('</TileMapService>')
        return HttpResponse("\n".join(xml), mimetype="text/xml")
    except:
        traceback.print_exc()
        return HttpResponse("Error2")


# start with some basic error checking on the version and shapefile ID, 
# and then iterate through the available zoom levels to provide information about the available Tile Sets

def tileMap(request, version, shapefile_id):
    if version != "1.0":
        raise Http404
    try:
        shapefile = Shapefile.objects.get(id=shapefile_id)
    except Shapefile.DoesNotExist:
        raise Http404
    
    try:
        baseURL = request.build_absolute_uri()
        xml = []
        xml.append('<?xml version="1.0" encoding="utf-8" ?>')
        xml.append('<TileMap version="1.0" ' +
                   'tilemapservice="' + baseURL + '">')
        xml.append(' <Title>' + shapefile.filename + '</Title>')
        xml.append(' <Abstract></Abstract>')
        xml.append(' <SRS>EPSG:4326</SRS>')
        xml.append(' <BoundingBox minx="-180" miny="-90" ' +
                   'maxx="180" maxy="90"/>')
        xml.append(' <Origin x="-180" y="-90"/>')
        xml.append(' <TileFormat width="' + str(TILE_WIDTH) +
                   '" height="' + str(TILE_HEIGHT) + '" ' +
                   'mime-type="image/png" extension="png"/>')
        xml.append(' <TileSets profile="global-geodetic">')
        for zoomLevel in range(0, MAX_ZOOM_LEVEL+1):
            unitsPerPixel = _unitsPerPixel(zoomLevel)
            xml.append('    <TileSet href="' +
                       baseURL + '/' + str(zoomLevel) +
                       '" units-per-pixel="'+str(unitsPerPixel) +
                       '" order="' + str(zoomLevel) + '"/>')
        xml.append(' </TileSets>')
        xml.append('</TileMap>')
        return HttpResponse("\n".join(xml), mimetype="text/xml")
    except:
        traceback.print_exc()
        return HttpResponse("Error1")

# Function generates the appropriate map tile and return the rendered image back to the caller

def tile(request, version, shapefile_id, zoom, x, y):
    try:
        if version != "1.0":
            raise Http404
        try:
            shapefile = Shapefile.objects.get(id=shapefile_id)
        except Shapefile.DoesNotExist:
            raise Http404

        zoom = int(zoom)
        x = int(x)
        y = int(y)
        if zoom < 0 or zoom > MAX_ZOOM_LEVEL:
            raise Http404
# Convert the supplied x and y parameters into the minimum and maximum latitude and longitude values covered by the tile. This requires us to use the _unitsPerPixel() function defined earlier to calculate the amount of the Earth's surface covered by the tile for the current zoom level
    	xExtent = _unitsPerPixel(zoom) * TILE_WIDTH
    	yExtent = _unitsPerPixel(zoom) * TILE_HEIGHT
    	minLong = x * xExtent - 180.0
    	minLat = y * yExtent - 90.0
    	maxLong = minLong + xExtent
    	maxLat = minLat + yExtent

	if (minLong < -180 or maxLong > 180 or
	    minLat < -90 or maxLat > 90):
            raise Http404
# Create mapnik.Map object
        map = mapnik2.Map(TILE_WIDTH, TILE_HEIGHT,
                        "+proj=longlat +datum=WGS84")
        map.background = mapnik2.Color("#8aa3ec")

# Define the layer which draws the base map by setting up a mapnik.PostGIS datasource for the layer
        dbSettings = settings.DATABASES['default']
        datasource = \
            mapnik2.PostGIS(user=dbSettings['USER'],
                           password=dbSettings['PASSWORD'],
                           dbname=dbSettings['NAME'],
                           table='tms_basemap',
                           srid=4326,
                           geometry_field="geometry",
                           geometry_table='tms_basemap')
# Create the baselayer itself   
        baseLayer = mapnik2.Layer("baseLayer")
        baseLayer.datasource = datasource
        baseLayer.styles.append("baseLayerStyle")
# Set up the layer's style. In this case, we'll use a single rule with two symbolizers: a PolygonSymbolizer which draws the interior of the base map's polygons, and a LineSymbolizer to draw the polygon outlines


        #labelStyle = mapnik2.Style()
        rule = mapnik2.Rule()
        #symbol = mapnik2.TextSymbolizer(mapnik2.Expression("[name]"),"DejaVu Sans Book", 12, mapnik2.Color("#000000"))
        #rule.symbols.append(symbol)
        #labelStyle.rules.append(rule)



       # rule = mapnik2.Rule()
        rule.symbols.append(
            mapnik2.PolygonSymbolizer(mapnik2.Color("#f0e9e6")))
        rule.symbols.append(
            mapnik2.LineSymbolizer(mapnik2.Color("#807878"), 0.2))
              
        
        
        style = mapnik2.Style()
        style.rules.append(rule)
# Add the base layer and its style to the map
        map.append_style("baseLayerStyle", style)
        map.layers.append(baseLayer)
# Add another layer to draw the shapefile's features onto the map.
# Once again, set up a mapnik.PostGIS datasource for the new layer
        geometryField = utils.calc_geometry_field(shapefile.geom_type)
        #print geometryField
        


        if geometryField=='geom_point':
            query = '(select geom_point from shared_feature where shapefile_id=' + str(shapefile.id) + ') as geom'
        else:
            query = '(select ' + geometryField \
              + ' from "shared_feature" where' \
              + ' shapefile_id=' + str(shapefile.id) + ') as geom'
              
        
        
        print query
                
        datasource = \
            mapnik2.PostGIS(user=dbSettings['USER'],
                            password=dbSettings['PASSWORD'],
                            dbname=dbSettings['NAME'],
                            table=query,
                            srid=4326,
                            geometry_table='shared_feature',
                            geometry_field=geometryField)
        print datasource    
# Create the new layer itself
    	featureLayer = mapnik2.Layer("featureLayer")
    	featureLayer.datasource = datasource
    	featureLayer.styles.append("featureLayerStyle")
# Define the styles used by the feature layer
    	rule = mapnik2.Rule()
    
    	if shapefile.geom_type in ["Point", "MultiPoint"]:
            rule.symbols.append(mapnik2.PointSymbolizer())
    	elif shapefile.geom_type in ["LineString", "MultiLineString"]:
            rule.symbols.append(
                 mapnik2.LineSymbolizer(mapnik2.Color("#404040"), 0.5))
        elif shapefile.geom_type in ["Polygon", "MultiPolygon"]:
            rule.symbols.append(
                mapnik2.PolygonSymbolizer(mapnik2.Color("#f7edee")))
            rule.symbols.append(
                mapnik2.LineSymbolizer(mapnik2.Color("#000000"), 0.5))
        style = mapnik2.Style()
        style.rules.append(rule)
# Add new feature layer to the map
        map.append_style("featureLayerStyle", style)
        map.layers.append(featureLayer)
# Rendering the map tile. Create a mapnik.Image object, convert it into raw image data in PNG format, and return that data back to the caller using an HttpResponse object
        map.zoom_to_box(mapnik2.Box2d(minLong, minLat,
                                     maxLong, maxLat))
        image = mapnik2.Image(TILE_WIDTH, TILE_HEIGHT)
        mapnik2.render(map, image)
        imageData = image.tostring('png')
   
        return HttpResponse(imageData, mimetype="image/png")

# Error-catching 
    except:
        traceback.print_exc()
        return HttpResponse("Error")

def _unitsPerPixel(zoomLevel):
    return 0.703125 / math.pow(2, zoomLevel)
