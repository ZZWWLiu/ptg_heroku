
import logging
db_name = "parktogodb"

def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

def make_pipeline(latitude, longitude, num = 3):
    # complete the aggregation pipeline
    pipeline = [ {
    	"$geoNear" : {
    		"near" : [longitude, latitude],
    		"distanceField": "distance",
    		"num": num
    	}
    }]

    pipeline1 = [ {
    	"$geoNear" : {
    		"near" : [longitude, latitude],
    		"distanceField": "distance",
    		"num": 1
    	}
    }]
    return pipeline, pipeline1

def aggregate(db, pipeline, pipeline1, class_id):
	result = []
	if class_id == 0:
		# db.parkclass1.createIndex({"loc":"2d"})
		# db.Nationalparkclass1.createIndex({"coords":"2d"})
		result.append(db.Nationalparkclass1.aggregate(pipeline1))
		result.append(db.parkclass1.aggregate(pipeline))
	elif class_id == 1:
		# db.parkclass2.createIndex({"loc":"2d"})
		# db.Nationalparkclass2.createIndex({"coords":"2d"})
		result.append(db.Nationalparkclass2.aggregate(pipeline1))
		result.append(db.parkclass2.aggregate(pipeline))
	elif class_id == 2:
		# db.parkclass3.createIndex({"loc":"2d"})
		# db.Nationalparkclass3.createIndex({"coords":"2d"})
		result.append(db.Nationalparkclass3.aggregate(pipeline1))
		result.append(db.parkclass3.aggregate(pipeline))
	elif class_id == 3:
		# db.parkclass4.createIndex({"loc":"2d"})
		# db.Nationalparkclass4.createIndex({"coords":"2d"})
		result.append(db.Nationalparkclass4.aggregate(pipeline1))
		result.append(db.parkclass4.aggregate(pipeline))
	elif class_id == 4:
		# db.parkclass5.createIndex({"loc":"2d"})
		# db.Nationalparkclass5.createIndex({"coords":"2d"})
		result.append(db.Nationalparkclass5.aggregate(pipeline1))
		result.append(db.parkclass5.aggregate(pipeline))
	return result


def recommend(class_id, latitude, longitude):
	db = get_db(db_name)
	pipeline,pipeline1 = make_pipeline(latitude,longitude)
	result = aggregate(db, pipeline,pipeline1, class_id)
	return result