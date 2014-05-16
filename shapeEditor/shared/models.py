from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import User


class Shapefile(models.Model):
    owner = models.ForeignKey(User)
    filename = models.CharField(max_length=255)
    srs_wkt = models.CharField(max_length=255)
    geom_type = models.CharField(max_length=50)
    encoding = models.CharField(max_length=20)

# Returns the string representation of the model.
# On Python 3: def __str__(self):
    def __unicode__(self):
    	#print self.filename    
        return self.filename

class Attribute(models.Model):
    shapefile = models.ForeignKey(Shapefile)
    name = models.CharField(max_length=255)
    type = models.IntegerField()
    width = models.IntegerField()
    precision = models.IntegerField()
# Returns the string representation of the model.
# On Python 3: def __str__(self):
    def __unicode__(self):
        return self.name



class Feature(models.Model):
    shapefile = models.ForeignKey(Shapefile)
    geom_point = models.PointField(srid=4326,
				   blank=True, null=True)
    geom_multipoint = \
           models.MultiPointField(srid=4326,
                                  blank=True, null=True)
    geom_multilinestring = \
	   models.MultiLineStringField(srid=4326,
				       blank=True, null=True)
    geom_multipolygon = \
	   models.MultiPolygonField(srid=4326,
				   blank=True, null=True)
    geom_geometrycollection = \
	   models.GeometryCollectionField(srid=4326,
				         blank=True,
				         null=True)
    objects = models.GeoManager()
# Returns the string representation of the model.
# On Python 3: def __str__(self):
    def __unicode__(self):
        return str(self.id)


class AttributeValue(models.Model):
    feature = models.ForeignKey(Feature)
    attribute = models.ForeignKey(Attribute)
    value = models.CharField(max_length=255,
			     blank=True, null=True)
# Returns the string representation of the model.
# On Python 3: def __str__(self):
    def __unicode__(self):
        return self.value

