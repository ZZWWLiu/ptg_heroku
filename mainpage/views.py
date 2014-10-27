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
TEST = False
# photo url = http://www.reserveamerica.com/webphotos/CO/pid50032/5/180x120.jpg
# src = http://www.reserveamerica.com + webphoto



def homepage(request):
	if request.method == 'GET':
		coord = getCoord(request)
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
			ip = request.META['REMOTE_ADDR'] if not TEST else "67.169.27.214"
			if user_need['coordinates'] == 'current':
				coord = cache.get(ip)
				if coord:
					lat, lon = getLatLong(coord)
				else: # in case the cache failed
					coord = getCoord(request)
					lat, lon = getLatLong(coord)
					logging.error('using api to get coord --- cache failed')
			else:
				lat, lon = getLatLong(user_need['coordinates'])
			class_id = int(user_need['parktype'])
			resList = recommend.recommend(class_id, lat, lon)
			res = resList[1]["result"]
			resN = resList[0]["result"][0]
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


# helper function should belong in controllers
def getLatLong(s):
	coord = s.split(',')
	lat = float(coord[0])
	lon = float(coord[1])
	return (lat, lon)

def getCoord(request):
	ip_api_key = '97f4d203b989b3fe87045b255e7a29d42f403cafc8726c45172079dbaa60fbfe'
	ipinfo = pyipinfodb.IPInfo(ip_api_key)
	ip = request.META['REMOTE_ADDR'] if not TEST else "67.169.27.214"
	coord = cache.get(ip)
	# logging.error("ip is " + ip)
	if coord is None: # if coord is not in the cache
		dataDict = ipinfo.GetCity(ip = ip)
		coord = dataDict["latitude"] +', '+dataDict["longitude"]
		# logging.error("coord is : "+ coord)
		cache.set(ip, coord, 300)
	return coord

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
		# logging.error(weatherList[0])
		detail['weather'] = weatherList
		resDetail.append(detail)
		time.sleep(0.6)
	return resDetail








