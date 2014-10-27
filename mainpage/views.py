# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from mainpage.models import UserParkForm, LocationForm
import urllib2
from xml.dom import minidom
import logging
import time
import json
from core_algorithm import weather, recommend,pyipinfodb
from django.core.cache import cache
# set test to False when deploy
test = False
# import re
# import hashlib
# photo url = http://www.reserveamerica.com/webphotos/CO/pid50032/5/180x120.jpg
# src = http://www.reserveamerica.com + webphoto

def getResDetail(res):
	key = 'd2rttztqpfhbqjz42buq6duc'
	baseUrl = 'http://www.reserveamerica.com'
	# iconUrl = 'http://openweathermap.org/img/w/'
	resDetail = []
	for idx,r in enumerate(res):
		detail = {}
		query = 'contractCode='+r['state']+'&parkId='+r['facilityID']
		camp_detail = 'http://api.amp.active.com/camping/campground/details?'+query+'&api_key='+key
		urlfile = urllib2.urlopen(camp_detail)
		data = urlfile.read()
		urlfile.close()
		dom = minidom.parseString(data)
		detailDescription = dom.getElementsByTagName('detailDescription')
		detail['description'] = detailDescription[0].attributes['description'].value
		detail['facility'] = detailDescription[0].attributes['facility'].value
		detail['importantInformation'] = detailDescription[0].attributes['importantInformation'].value
		photoUrls = []
		photos = dom.getElementsByTagName('photo')
		for p in photos:
			realUrl = p.attributes['realUrl'].value
			# logging.error(realUrl)
			if realUrl != '':
				photoUrls.append(baseUrl+realUrl)
		detail['imgs'] = photoUrls
		detail['state'] = r['state']
		detail['coords'] = {'lat': r['latitude'], 'lon':r['longitude']}
		wkey = r['latitude']+r['longitude']

		weatherList = cache.get(wkey)
		if weatherList is None:
			weatherList = weather.getWeather(r['latitude'], r['longitude'])
			cache.set(wkey, weatherList, 900)
			logging.error('using weather api')
		logging.error(weatherList[0])
		detail['weather'] = weatherList
		resDetail.append(detail)
		time.sleep(0.6)
	return resDetail

# helper function
def getLatLong(s):
	coord = s.split(',')
	lat = float(coord[0])
	lon = float(coord[1])
	return (lat, lon)

def getCoord(request, test = False):
	if test == False:
		ra = 'REMOTE_ADDR'
		s = "HTTP_X_AppEngine_CityLatLong"
		# HTTP_X_APPENGINE_CITYLATLONG
		coord = request.META[s.upper()]
		ip = request.META[ra]
		cache.set(ip, coord, 300)
	else:
		ip_api_key = '97f4d203b989b3fe87045b255e7a29d42f403cafc8726c45172079dbaa60fbfe'
		ipinfo = pyipinfodb.IPInfo(ip_api_key)
		ip = '67.169.27.214'
		coord = cache.get(ip)
		if coord is None:
			dataDict = ipinfo.GetCity(ip = ip)
			coord = dataDict["latitude"] +', '+dataDict["longitude"]
			cache.set(ip, coord,300)
			logging.error(coord)
		cache.set('ip', ip,300)
		logging.error(cache.get('ip'))
	return coord


def homepage(request):
	if request.method == 'GET':
		coord = getCoord(request, test = test)
		lat, lon = getLatLong(coord)
		API_KEY = 'AIzaSyAnEt9j1iiUDG6X2cRxQ2GUfotwoe4vCCY'
		google_maps = "https://maps.googleapis.com/maps/api/js?key="+API_KEY+"&sensor=false"
		content = {'google_maps_src': google_maps ,
		           'latitude' : lat,
		           'longitude' : lon
		           }
		return render(request, 'mainpage/userform.html', content)

def submit(request):
	if request.method == 'POST':
		form = LocationForm(request.POST)
		if form.is_valid():
			user_need = form.cleaned_data
			if test == False:
				ra = 'REMOTE_ADDR'
				ip = request.META[ra]
			else:
				ip = cache.get('ip')
				# logging.error(ip)
			if user_need['coordinates'] == 'current':
				coord = cache.get(ip)
				lat, lon = getLatLong(coord)
				# logging.error('default coord')
				# logging.error(coord)
			else:
				lat, lon = getLatLong(user_need['coordinates'])
			class_id = int(user_need['parktype'])
			# logging.error("printing the result1")
			# logging.error(res)
			resList = recommend.recommend(class_id, lat, lon)
			res = resList[1]["result"]
			# logging.error("printing the result")
			# logging.error(res)
			resN = resList[0]["result"][0]
			# logging.error(resN)
			NweatherList = weather.getWeather(str(resN['coords']['lat']), str(resN['coords']['lon']))
			resN['weather'] = NweatherList
			resDetail = getResDetail(res)
			API_KEY = 'AIzaSyAnEt9j1iiUDG6X2cRxQ2GUfotwoe4vCCY'
			google_maps = "https://maps.googleapis.com/maps/api/js?key="+API_KEY+"&sensor=false"
			content = {'results': resDetail,
			           'Nresult': resN,
					   'google_maps_src': google_maps ,
		               'latitude' : lat,
		               'longitude' : lon,
		               'lat0': float(resN['coords']['lat']),
		               'lon0': float(resN['coords']['lon'])
		               }
			return render(request, 'mainpage/recommend.html', content)













