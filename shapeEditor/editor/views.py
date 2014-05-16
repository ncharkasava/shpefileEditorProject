from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound
from django.shortcuts import render


from shapeEditor.shared.models import Shapefile
from shapeEditor.shared.models import Attribute
from shapeEditor.shared.models import AttributeValue
from shapeEditor.editor.forms import ImportShapefileForm
from shapeEditor.editor.forms import ChangeAttributeValueForm
from shapeEditor.editor.forms import AddAttributeValueForm
from shapeEditor.shapefileIO import importer
from shapeEditor.shapefileIO import exporter

import traceback
from django.contrib.gis.geos import Point
from shapeEditor.shared.models import Feature
from shapeEditor.shared import utils



def list_shapefiles(request):
    userid = request.user
    shapefiles = Shapefile.objects.filter(owner_id=userid.id).order_by("filename")
    #shapefiles = Shapefile.objects.all().order_by("filename")
    
    return render(request, "list_shapefiles.html",
		  {'shapefiles' : shapefiles,
		   'full_name': request.user.username})

#The import_shapefile() function is called with an HTTP GET request
def import_shapefile(request):
    userid = request.user	
    if request.method == "GET":
# create a new ImportShapefileForm object
        form = ImportShapefileForm(auto_id=False)
# call the render() function to display that form to the user.
        return render(request, "import_shapefile.html",
                      {'form'    : form,
                       'err_msg' : None,
		       'full_name': request.user.username})
# When the form is submitted, the import_shapefile() function is
# called with an HTTP POST request.  The ImportShapefileForm is 
# created with the submitted data (request.POST and request.FILES)
    elif request.method == "POST":
        form = ImportShapefileForm(request.POST,
                                   request.FILES)
# The form is checked to see that the entered data is valid.
# If so, extract the uploaded shapefile and the selected character
# encoding.
        if form.is_valid():
            shapefile = request.FILES['import_file']
            encoding = request.POST['character_encoding']

            err_msg = importer.import_data(request, shapefile,
                                                encoding)
# We then ask the shapefile importer to import the shapefile's data.
# This will return an error message if something goes wrong.
# If there is no error, we redirect the user back to the main /editor page
# so that the newly-imported shapefile can be shown.

            if err_msg == None:
                return HttpResponseRedirect("/editor")
   
        else:
            err_msg = None
# If the form was not valid, or if the import process failed 
# for some reason, again call the render() function to display
# the form to the user, this time with an appropriate error message.
# Note that Django will automatically display an error 
# message if there is a problem with the form.
        return render(request, "import_shapefile.html",
                      {'form'    : form,
                       'err_msg' : err_msg,
		       'full_name': request.user.username})





# This view function takes the record ID of the desired shapefile,
# loads the Shapefile object into memory, and passes it to the 
# export_data() function for processing. The resulting HttpResponse
# object is then returned to the caller, allowing the exported
# file to be downloaded to the user's computer.

def export_shapefile(request, shapefile_id):
    try:
        shapefile = Shapefile.objects.get(id=shapefile_id)
    except Shapefile.DoesNotExist:
        return HttpResponseNotFound()
    
    return exporter.export_data(shapefile)

#  obtain the desired Shapefile object, calculate the URL used to
# access our TMS server, and pass both on to a template called
# select_feature.html. See templates directory for
# select_feature.html (where all the hard work take place).
 

def edit_shapefile(request, shapefile_id):
    userid = request.user
    try:
        shapefile = Shapefile.objects.get(id=shapefile_id)
    except Shapefile.DoesNotExist:
        return HttpResponseNotFound()

    tms_url = "http://"+request.get_host()+"/tms/"

    find_feature_url = "http://" + request.get_host() \
                     + "/editor/find_feature"
    add_feature_url = "http://" + request.get_host() \
                    + "/editor/edit_feature/" \
                    + str(shapefile_id)

    return render(request, "select_feature.html",
                {'shapefile' : shapefile,
                 'find_feature_url' : find_feature_url,
                 'add_feature_url' : add_feature_url,
                 'tms_url' : tms_url,
		 'full_name': request.user.username})

def find_feature(request):
    try:
# extract the supplied query parameters, converting them from strings to
# numbers, load the desired Shapefile object, create a GeoDjango Point
# object out of the clicked-on coordinates, and calculate the search radius in degrees
# Note: hardwired search radius of 100 meters; this is enough to let the
# user select a point or line feature by clicking close to it,
# without being so large that the user might accidentally click on the wrong feature.
	shapefile_id = int(request.GET['shapefile_id'])
	#print shapefile_id
        latitude = float(request.GET['latitude'])
	longitude = float(request.GET['longitude'])
	
	shapefile = Shapefile.objects.get(id=shapefile_id)
	#print "Shapefile"
        #print shapefile
        #print "End"
	pt = Point(longitude, latitude)
	radius = utils.calc_search_radius(latitude, longitude, 100)
	
# Perform the spatial query (built based on the geometry's type)
# In each case, choose the appropriate geometry field, and use __dwithin
# to perform a spatial query on the appropriate field in the Feature object.
        sh_id = shapefile_id
        q = Feature.objects.raw('SELECT * from shared_feature where shapefile_id=%s', [sh_id])
        for p in q:
            print p.id, p.shapefile_id
	
        if shapefile.geom_type == "Point":
		query = Feature.objects.filter(
			geom_point__dwithin=(pt, radius))
		print query, shapefile_id
	elif shapefile.geom_type in ["LineString", "MultiLineString"]:
		query = Feature.objects.filter(
			geom_multilinestring__dwithin=(pt, radius))
		print query, shapefile_id
	elif shapefile.geom_type in ["Polygon", "MultiPolygon"]:
		query = Feature.objects.filter(
			geom_multipolygon__dwithin=(pt, radius))
		print query, shapefile_id
	elif shapefile.geom_type == "MultiPoint":
		query = Feature.objects.filter(
			geom_multipoint__dwithin=(pt, radius))
		#print query, shapefile_id
	elif shapefile.geom_type == "GeometryCollection":
		query = feature.objects.filter(
			geom_geometrycollection__dwithin=(pt, radius))
		#print query, shapefile_id
	
	else:
	  print "Unsupported geometry: " + shapefile.geom_type
	  return HttpResponse("")
#  Check to see if the query returned exactly one Feature.
# If not, return an empty string back to the AJAX handler's callback
# function, to tell it that the user did not click on a feature
	a = []
        for n in query:
        	if n in q:
                  a.append(n)
	print a	
        if len(a) != 1:
	  print "count "
	  print query.count()
	  return HttpResponse("")

# If there was exactly one matching feature, get the clicked-on feature and
# use it to build a URL redirecting the user's web browser to the "edit
# feature" URL for the clicked-on feature
        


	feature = a[0]
	return HttpResponse("/editor/edit_feature/" +
			    str(shapefile_id)+"/"+str(feature.id))
    except:
	traceback.print_exc()
	return HttpResponse("")


# Functon load the Shapefile object for the current shapefile,
# and the Feature object for the feature we are editing.
# Load into memory a list of that feature's attributes,
# so these can be displayed to the user

def edit_feature(request, shapefile_id, feature_id=None, attributevalue=None):
    userid = request.user
    if request.method == "POST" and "delete" in request.POST:
      return HttpResponseRedirect("/editor/delete_feature/" +
                                  shapefile_id+"/"+feature_id)

    try:
      shapefile = Shapefile.objects.get(id=shapefile_id)
    except ShapeFile.DoesNotExist:
      return HttpResponseNotFound()
      
      
    if request.method == "POST" and "attributevalue" in request.POST:
      print attributevalue	    
      return HttpResponseRedirect("/editor/edit_attributevalue/" +
                                  shapefile_id+"/"+attributevalue)

    try:
      shapefile = Shapefile.objects.get(id=shapefile_id)
    except ShapeFile.DoesNotExist:
      return HttpResponseNotFound()
      
      
    if request.method == "POST" and "addattributevalue" in request.POST:
      print feature_id	    
      return HttpResponseRedirect("/editor/add_attributevalue/" +
                                  str(shapefile_id)+"/"+str(feature_id))

    try:
      shapefile = Shapefile.objects.get(id=shapefile_id)
    except ShapeFile.DoesNotExist:
      return HttpResponseNotFound()
      
      
      
# Create a new Feature object if the feature_id is not specified,
# but fail if an invalid feature ID was specified.

    if feature_id == None:
      feature = Feature(shapefile=shapefile)
           
    else:
      try:
        feature = Feature.objects.get(id=feature_id)
        
      except Feature.DoesNotExist:
        return HttpResponseNotFound()

# Store attributes and attributes' values in an array
    attributes = []
    for attr_value in feature.attributevalue_set.all():
      attributes.append([attr_value.attribute.name,
                         attr_value.value,
                         attr_value.id])
    attributes.sort()



   # get all attributes for shapefile
    q = []
    q = Feature.objects.raw('SELECT * from shared_attribute where shapefile_id=%s', [shapefile_id])
    all_attr = []
    for p in q:
        all_attr.append(p.id)
            
  # get only attributes that have values
    q1 = []
    set_attr = []
    q1 = Feature.objects.raw('SELECT * from shared_attributevalue where feature_id=%s', [feature_id])
    for p in q1:
        set_attr.append(p.attribute_id) 	  
  
    attributes1 = []
    attr1 = []
    for n in all_attr:
        	if n not in set_attr:
                  #print n
                  attr = Attribute.objects.get(id=n)
                  attr1.append(attr.name)
                  attr1.append(attr.id)
                  attributes1.append(attr1)
                  attr1=[]
    attributes1.sort()  
    print attributes1
 
    geometry_field = \
            utils.calc_geometry_field(shapefile.geom_type)
    form_class = utils.get_map_form(shapefile)

    if request.method == "GET":
      wkt = getattr(feature, geometry_field)
      form = form_class({'geometry' : wkt})

      return render(request, "edit_feature.html",
                  {'shapefile' : shapefile,
                   'form' : form,
                   'feature': feature_id,
                   'attributes' : attributes,
                   'available': attributes1,
		   'full_name': request.user.username})
      
    elif request.method == "POST":
      form = form_class(request.POST)
      try:
        if form.is_valid():
          wkt = form.cleaned_data['geometry']
          setattr(feature, geometry_field, wkt)
          feature.save()

          return HttpResponseRedirect("/editor/edit_feature/" +
			    str(shapefile_id)+"/"+str(feature.id))
      except ValueError:
        pass

    return render(request, "edit_feature.html",
                  {'shapefile' : shapefile,
                   'form' : form,
                   'feature': feature_id,
                   'attributes' : attributes,
                   'available': attributes1,
		   'full_name': request.user.username})


# This function permanently deletes feature from database 
def delete_feature(request, shapefile_id, feature_id):
  userid = request.user
  try:
    feature = Feature.objects.get(id=feature_id)
  except Feature.DoesNotExist:
    return HttpResponseNotFound()
  if request.method == "POST":
    if request.POST['confirm'] == "1":
      feature.delete()
    return HttpResponseRedirect("/editor/edit/" +
                                shapefile_id)
  return render(request, "delete_feature.html",
  	       {'full_name': request.user.username})



# This function permanently deletes shapefile from database
def delete_shapefile(request, shapefile_id):
  userid = request.user
  try:
    shapefile = Shapefile.objects.get(id=shapefile_id)
  except Shapefile.DoesNotExist:
    return HttpResponseNotFound()

  if request.method == "GET":
    return render(request, "delete_shapefile.html",
                  {'shapefile' : shapefile,
		   'full_name': request.user.username})
  elif request.method == "POST":
    if request.POST['confirm'] == "1":
     shapefile.delete()
    return HttpResponseRedirect("/editor")



#??????????????????????/
# This function edit attributes values of shapefile feature's 
def edit_attributevalue(request, shapefile_id, attributevalue_id):
  userid = request.user
  attributeval = AttributeValue.objects.get(id=attributevalue_id)
  if request.method == "POST":
      print 'Changing value...'     
      form = ChangeAttributeValueForm(request.POST)
      if form.is_valid():
         newvalue = request.POST['attribute_value']
         #print newvalue
         attributeval.value = newvalue
         attributeval.save()
               
      
  return render(request, "edit_attributevalue.html",  
                  {'shapefile' : shapefile_id,
                   'name': attributeval.attribute.name,
                   'value': attributeval.value,
                   'feature': attributeval.feature,
                   'attributeid' : attributevalue_id,
		   'full_name': request.user.username})


#
def add_attributevalue(request, shapefile_id, feature_id):
  userid = request.user
  
  feature = feature_id
  shapefile = Shapefile.objects.get(id=shapefile_id)
  
  # get all attributes for shapefile
  q = []
  q = Feature.objects.raw('SELECT * from shared_attribute where shapefile_id=%s', [shapefile_id])
  all_attr = []
  for p in q:
      all_attr.append(p.id)
            
  # get only attributes that have values
  q1 = []
  set_attr = []
  q1 = Feature.objects.raw('SELECT * from shared_attributevalue where feature_id=%s', [feature_id])
  for p in q1:
      set_attr.append(p.attribute_id) 	  
  
  attributes1 = []
  attr1 = []
  for n in all_attr:
        	if n not in set_attr:
                  #print n
                  attr = Attribute.objects.get(id=n)
                  attr1.append(attr.name)
                  attr1.append(attr.id)
                  attributes1.append(attr1)
                  attr1=[]
  attributes1.sort()  
  
  if request.method == "POST":
     print 'Adding value'     
     form = AddAttributeValueForm(request.POST)
     if form.is_valid():
     	 newattribute = request.POST['attribute']    
         newvalue = request.POST['attribute_value']
         print newvalue
         print newattribute
         attributeval = AttributeValue(feature_id=feature, attribute_id=newattribute, value=newvalue)
  #  attributeval.value = newvalue
         attributeval.save()
               
      
  return render(request, "add_attributevalue.html",  
                  {'shapefile' : shapefile_id,
                   'attributes': attributes1,
                   'feature': feature_id,
		   'full_name': request.user.username})



