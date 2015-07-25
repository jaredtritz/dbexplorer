
This project provides a web interface to explore database objects in a large relational database.
#################################################################################################

Assumptions
===========
* Foreign key relationships utilize column names which are consistent across all tables in the database
* Samples of DB objects are identified using either built in filtering capabilities, or uploaded as lists of FKs
* It's useful to see "all the data" on a single page, for a given database object
* It's useful to scroll forward/backward through a list of DB objects, seeing "all the data" for each
* It's useful to define a single method, which gets "all the data" for a given object hoisted into its context, and extracts properties
* Once an extraction method is defined, it's useful to easily re-run the extraction method against any other set of DB objects
* Property comparison, and other statistical techniques may be integrated, or performed on property extracts offline


