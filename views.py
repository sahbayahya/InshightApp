from flask import render_template, request
from app import app
import pymysql as mdb
from routing import routing
from ast import literal_eval as make_tuple

@app.route('/')
@app.route('/index')
def index():
	return render_template("index.html",
		title ='Home',
		user = {'nickname' : 'Miguel'},
		)

@app.route('/db')
def cities_page():
	db = mdb.connect(user="root", host="localhost", passwd= "", db="world",
	charset='utf8')
	
	with db:
		cur = db.cursor()
		cur.execute("SELECT name FROM city LIMIT 15;")
		query_results = cur.fetchall()
	cities = ""
	for result in query_results:
		cities += result[0]
		cities += "<br>"
	return cities

@app.route("/db_fancy")
def cities_page_fancy():
        db = mdb.connect(user="root", host="localhost", passwd= "", db="world",
        charset='utf8')
	with db:
		cur = db.cursor()
		cur.execute("SELECT Name, CountryCode, Population FROM City ORDER BY Population LIMIT 15;")
		query_results = cur.fetchall()
	cities = []
	for result in query_results:
		cities.append(dict(name=result[0], country=result[1], population=result[2]))
	return render_template('cities.html', cities=cities) 

@app.route('/input')
def cities_input():
  return render_template("input.html")

# pos0 = (40.746581, -73.997552)
# pos1 = (40.7127, -74.0059) 
	#from routing import routing
	#city = request.args.get('ID')
	#(x, y) = routing('my location', 'ID')

@app.route('/output')
def cities_output():
	pos0 = request.args.get('ID')#pos0 = (40.746581, -73.997552)
	pos0 =make_tuple(pos0)
	#pos0 = pos0.split(",")
	#pos0  = (str(pos0[0]), ',', str(pos0[2]));
	#pos0 = (40.746581, -73.997552)
	print "Pos0", pos0
	pos1 = (40.7127, -74.0059)
	(x, y), path2= routing(pos0, pos1);
	#print "SRRORTTTTTTTTTT"
	print path2
	starting_point  = (str(x[0]), ',', str(y[0])); starting_point =''.join(map(str, starting_point)) 
	end_point  = (str(x[-1]), ',', str(y[-1])); end_point =''.join(map(str, end_point)) 
	return render_template("output.html",
						  start=str(starting_point),
						  end=str(end_point),
						  path = path2)
  
  
 
#  cities = []
#  for result in query_results:
#    cities.append(dict(name=result[0], country=result[1], population=result[2]))
#  the_result = ''
#  return render_template("output.html", cities = cities, the_result = the_result)


#@app.route('/output')
#def cities_output():
#  #pull 'ID' from input field and store it
#  city = request.args.get('ID')
#  db = mdb.connect(user="root", host="localhost", passwd= "", db="world",
#        charset='utf8')
#  with db:
#    cur = db.cursor()
#    #just select the city from the world database that the user inputs
#    cur.execute("SELECT Name, CountryCode,  Population FROM City WHERE Name='%s';" % city)
#    query_results = cur.fetchall()
#
#  cities = []
#  for result in query_results:
#    cities.append(dict(name=result[0], country=result[1], population=result[2]))
#  the_result = ''
#  return render_template("output.html")


