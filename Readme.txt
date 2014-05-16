 ***********************************************************
 ******************ShapeEditor Project *********************
 ***********************************************************
 
 ***********************************************************
 **********************Acknowledgments**********************
 ***********************************************************
Special thanks to Erik Westa, author of the book Python Geospatial Development, which is the base for this project
The project is based upon work supported by the National Science Foundation under Grant No. 1156827

 
 ***********************************************************
 ********************** Objectives *************************
 ***********************************************************

- Designing a web  application based on open source software tools for viewing and editing shapefile data
- Translating that design into code by creating a GeoDjango project and its applications for:
	- Importing and exporting any shapefiles
	- Displaying shapefile features 
	- Selecting features
	- Editing feature geometry and attribute values


ShapeEditor’s main components:
 User signup and login. It  uses Gjango built-in admin authentication system and allows to each user has his or her own private set of shapefiles. 

 Importing the geometrical features, attributes and attribute values from a shapefile. Importer uploads ZIP archive, decompresses the archive,  extracts the individual files that make up the shapefile, reads through the shapefile to find its attributes, and create the appropriate Attribute objects,  Feature, and AttributeValue objects. Each imported shapefile is represented by a single Shapefile object in the database and has ID of the user who uploaded it

 Displaying information stored in shapefiles  and selecting a feature to be edited. Tile Map Server (TMS) is built on top of a Mapnik-based map renderer to display the shapefile's features stored in the database. OpenLayers uses it as a source of map tiles to display.  JavaScript “Click handler“  intercepts clicks on the map and sends off an AJAX request to the server to see which feature the user clicked on. If the user does click on a feature, the user's web browser is redirected to the "Edit Feature" page so that the user can edit the clicked-on feature (See Image 1)

 Displaying the editor to allow the user to edit the feature's geometry. GeoDjango's built-in geometry editing widget is used for implementing  this part of the project. Edit feature also allows user to delete feature, add new ones and edit attributes’ values. (See Image  2)

 Exporting the geometrical features and attributes back into a shapefile.  Exporter creates a new shapefile on disk, defines the various attributes that will be stored in the shapefile, processes all the features and their attributes, writing them out  to the shapefile, creates a ZIP archive from the contents of the shapefile, and tells the user's web browser to download that ZIP archive to the user's hard disk.

 ***********************************************************
 ***************** Tools and libraries used:****************
 ***********************************************************


 Python is an open-source programming language. It has become one of the key languages used for GIS. 

 GeoDjango is a free and open source Web application framework, written in Python, which follows the model–view–controller architectural pattern. Its goal to make it as easy as possible to build GIS Web applications.

 PostGIS is a spatial database extender for PostgreSQL object-relational database. It adds support for geographic objects allowing location queries to be run in SQL. 

 Geospatial Data Abstraction Library (GDAL) /OGR Simple Features Library  are used for reading and writing raster  and vector geospatial data formats.

 Pyproj is a Python "wrapper" around another library called PROJ.4. "PROJ.4" is an abbreviation for Version 4 of the PROJ library. PROJ was originally written by the United States Geological Survey for dealing with map projections, and has been widely used in geospatial software for many years. The pyproj library makes it possible to access the functionality of PROJ.4 from within your Python programs.

 Mapnik is a freely-available toolkit for building mapping applications. It takes geospatial data from a PostGIS database, shapefile, or any other format supported by GDAL/OGR, and turns it into clearly-rendered, good-looking images. 

 OpenLayers is a pure JavaScript library for displaying map data in most modern web browsers, with no server-side dependencies. OpenLayers implements a JavaScript API for building rich web-based geographic applications.

