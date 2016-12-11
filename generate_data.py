from pymongo import MongoClient
import graphlab
import pandas as pd
import numpy as np  

def connect():
    connection = MongoClient("ds031257.mlab.com",31257)
    handle = connection["general_info_database"]
    handle.authenticate("admin","admin1")
    return handle
	
def main():
	handle = connect()
	db_user = handle.reviews
	cursor = db_user.find({})
	users = [res for res in cursor]
	outdata = {'user':[],'course':[],'rating':[]}
	for user in users:
		for sem in range(1,9):
			courses_list = user["courses"][str(sem)]
			for course in courses_list:
				outdata['user'].append(user["username"])
				outdata['course'].append(course)
				outdata['rating'].append(np.random.normal(8, 1,1)[0])
	#df = pd.DataFrame(outdata, columns = ['user', 'course', 'rating'])
	#df.to_excel('result.xlsx')
	sf = graphlab.SFrame(data = outdata)
	m = graphlab.recommender.ranking_factorization_recommender.create(sf, user_id='user', item_id='course', target ='rating') 
	recs = m.recommend()
	print(recs)
	user_recs = {}
	for i in range(0,len(recs['user'])):
		if recs['user'][i] not in user_recs:
			user_recs[recs['user'][i]] = []
		user_recs[recs['user'][i]].append(recs['course'][i])

	for user in user_recs:
		print(user + " ")
		print(user_recs[user])


main()
