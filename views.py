import sys
from flask import Flask
#app = Flask(__name__)
sys.path.append("/Users/sahba/Dropbox/DSInsightProject/app/areas")
from flask import render_template, request, redirect, url_for
from app import app
import pymysql as mdb
from routing import routing
from ManhattanYelp import *
from ast import literal_eval as make_tuple
import pdb
from ScrapingTheSkint import get_recom
from urllib2 import Request, urlopen, URLError



#============================
# Define global location
#=============================
global_Location = None
#=============================
# The website starter page
#=============================
@app.route('/')
def cities_start():
             return render_template("start.html")

#=============================================
# This is to render interest me list of events
#=============================================
@app.route('/interestme')
def interest_input():
                index = [ "show", "comedy", "festival","performances"]
                ClubsType= ["Nightlife","divebars", "cocktailbars", "pizza", "wine_bars", "beer_and_wine", "bars",\
                         "danceclbs", "newamerican", "Performing Arts", "jazz", "italian", "Lounges"]
                return render_template("interestme.html", index=index)

#=============================================
# This function render the template hot clubs nearby
# contain list of areas in Manhattan
#=============================================
@app.route('/nearme')
def near_input():
    areas = ["Hells Kitchen", "Koreatown", "Lower East Side", "Lower Manhattan", "Meatpacking District", "Midtown", "Noho", "Nolita Little Italy", "Soho", "Times Square"]

    ClubsType= ["Nightlife", "bars",\
             "new american", "jazz", "Lounges"]
    return render_template("nearme.html", areas=areas ,ClubsType=ClubsType)



#============================================
# A function render a template with the list of categories of the clubs in a given area
#=============================================
@app.route('/get_location')
def get_output_location():
	Location = request.args.get("location");
	Location2 = Location.replace(" ","")
	list_cat_ = list_cat(Location2)
	global global_Location
	global_Location = Location
	return render_template("get_location.html", Location=Location, ListCat=list_cat_)



#===========================================
# A function shows/render  the results of the clubs recommended for a specific area
#===============================================
@app.route('/nearme_output')
def nearme_output():
    try:
        clubtype = request.args.get("clubs");
        print global_Location, clubtype;
        Location = global_Location.replace(" ","")
        print Location
        club1, club2, club3 = recommend_by_location(str(Location), clubtype)
        print club1, club2, club3
        clublocation1  = (str(club1[1]), ',', str(club1[2])); clublocation1 =''.join(map(str, clublocation1))
        clublocation2  = (str(club2[1]), ',', str(club2[2])); clublocation2 =''.join(map(str, clublocation2))
        clublocation3  = (str(club3[1]), ',', str(club3[2])); clublocation3 =''.join(map(str, clublocation3))
        
        club1name = club1[0]
        club2name = club2[0]
        club3name = club3[0]
        club1Senti = club1[3]*100
        club2Senti = club2[3]*100
        club3Senti = club3[3]*100  
        pos0 = (club1[1], club1[2])
        pos1 = (club2[1],club2[2])
        
        #(x, y), path2= routing(pos0, pos1);
        #starting_point  = (str(x[0]), ',', str(y[0])); starting_point =''.join(map(str, starting_point))
        #end_point  = (str(x[-1]), ',', str(y[-1])); end_point =''.join(map(str, end_point))
        print '+++++++++++==========================================================++++++++++++++++++++++'
        print str(clublocation1),str(clublocation2), str(clublocation3)
        return render_template("output_nearme.html",
                               #start=str(starting_point),
                               #end=str(end_point),
                               Clublocation1=(clublocation1),
                               Clublocation2=(clublocation2),
                               Clublocation3=(clublocation3),
                               Club1name=club1name,
                               Club2name=club2name,
                               Club3name=club3name,
                               club1Senti=club1Senti,
                               club2Senti=club2Senti,
                               club3Senti=club3Senti)
    except:
        	### if it didn't work, return a generic error message
        	error = 'Sorry, This type of club is not avaliable in this area :(. Please try again.'
        	return render_template("except.html",  the_result = error)



#==============================================
# A function that shows/render a template with
# the recommeded events given the interest or event type.
#================================================
@app.route('/output', methods=['GET', 'POST'])
def cities_output():
	try:
    		event_type = request.args.get('events');
    		event1, event2, event3 = get_recom(event_type);
    		print event1, event2, event3;
    		return render_template('output_interestme.html',
                           event1 =event1.decode('UTF-8'),
                           event2=event2.decode('UTF-8'),
                           event3=event3.decode('UTF-8'))
	except:
                ### if it didn't work, return a generic error message
                error = 'Sorry, This type of event is not avaliable today :(. Please try again.'
                return render_template("except.html",  the_result = error)