
from firebase import firebase

from config import config

firebase = firebase.FirebaseApplication(config.databaseURL, None)
result = firebase.get('/users', '')
file_name = open('OutputData/UserInformation.txt', "w")
file_name.write(str(result))
print(result)

