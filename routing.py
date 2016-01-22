
# coding: utf-8

# In[12]:

import networkx as nx
import numpy as np
import pandas as pd
import json
import smopy
import matplotlib.pyplot as plt
import pickle
#get_ipython().magic(u'matplotlib inline')
import matplotlib as mpl
mpl.rcParams['figure.dpi'] = mpl.rcParams['savefig.dpi'] = 200



def get_full_path(path):
    """Return the positions along a path."""
    p_list = []
    curp = None
    for i in range(len(path)-1):
        p = get_path(path[i], path[i+1])
        if curp is None:
            curp = p
        if np.sum((p[0]-curp)**2) > np.sum((p[-1]-curp)**2):
            p = p[::-1,:]
        p_list.append(p)
        curp = p[-1]
    return np.vstack(p_list)
#Each edge in the graph contains information about the road, including a list of 
#points along this road. We first create a function that returns this array of 
#coordinates, for any edge in the graph.

def get_path(n0, n1):
    """If n0 and n1 are connected nodes in the graph, this function
    return an array of point coordinates along the road linking
    these two nodes."""
    return np.array(json.loads(sg[n0][n1]['Json'])['coordinates'])




#We will notably use the road path to compute its length. We first need to define a
# function that computes the distance between any two points in geographical 
#coordinates

EARTH_R = 6372.8
def geocalc(lat0, lon0, lat1, lon1):
    """Return the distance (in km) between two points in 
    geographical coordinates."""
    lat0 = np.radians(lat0)
    lon0 = np.radians(lon0)
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    dlon = lon0 - lon1
    y = np.sqrt(
        (np.cos(lat1) * np.sin(dlon)) ** 2
         + (np.cos(lat0) * np.sin(lat1) 
         - np.sin(lat0) * np.cos(lat1) * np.cos(dlon)) ** 2)
    x = np.sin(lat0) * np.sin(lat1) + np.cos(lat0) * np.cos(lat1) * np.cos(dlon)
    c = np.arctan2(y, x)
    return EARTH_R * c
#Now, we define a function computing a path's length.
def get_path_length(path):
    return np.sum(geocalc(path[1:,0], path[1:,1],
                          path[:-1,0], path[:-1,1]))  
sg= pickle.load( open("/Users/sahba/Dropbox/DSInsightProject/newyorkmap.p", "rb" ))

def routing(pos0, pos1):
  # In[24]:

  #g = nx.read_shp("/Users/sahba/Dropbox/DSInsightProject/data-2/tl_2013_06_prisecroads.shp")
  #g = nx.read_shp("/Users/sahba/Dropbox/DSInsightProject/brooklyn_new-york.imposm-shapefiles/brooklyn_new-york_osm_roads.shp")
  #g = nx.read_shp("/Users/sahba/Dropbox/DSInsightProject/los-angeles_california.imposm-shapefiles/los-angeles_california_osm_roads.shp")

################################PICKLE 
#g = nx.read_shp("/Users/sahba/Dropbox/DSInsightProject/new-york_new-york.imposm-shapefiles/new-york_new-york_osm_roads.shp")
  # In[25]:
# to pickle the sg file
#import pickle
#sg = max(nx.connected_component_subgraphs(pickled_g.to_undirected()),key=len)
#  len(sg)

#pickled_map  = pickle.dump(sg, open( "newyorkmap.p", "wb" ) )
##################################################
# Compute the length of the road segments.
 	for n0, n1 in sg.edges_iter():
 		path = get_path(n0, n1)
    	distance = get_path_length(path)
    	sg.edge[n0][n1]['distance'] = distance
 	nodes = np.array(sg.nodes())
	pos0_i = np.argmin(np.sum((nodes[:,::-1] - pos0)**2, axis=1))
  	pos1_i = np.argmin(np.sum((nodes[:,::-1] - pos1)**2, axis=1))
  	path = nx.dijkstra_path(sg, source=tuple(nodes[pos0_i]), target=tuple(nodes[pos1_i]), weight='distance')
#len(path)
#print path


  	roads = pd.DataFrame([sg.edge[path[i]][path[i + 1]] 
                      for i in range(len(path) - 1)], 
                     columns=['FULLNAME', 'MTFCC', 
                              'RTTYP', 'distance'])
  	print roads 
  	map = smopy.Map(pos0, pos1, z=6)


  	linepath = get_full_path(path)
  	x, y = (linepath[:,1], linepath[:,0])
  	path2 = [list(a) for a in zip(linepath[:,1],linepath[:,0])]
	return (x, y), path2



