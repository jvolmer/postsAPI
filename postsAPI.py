from flask import Flask, request, abort
from flask_restful import Api, Resource
import requests
import json
import werkzeug  # for some exceptions
# to get exception name: sys.exc_info()[0]

app = Flask(__name__)
api = Api(app)

class PostRankingAPI(Resource):
    def get(self):
        website = Website(self.getUrlName())
        posts = Posts(website.data)
        posts.sortBy('score', isReverseOrdering=True)
        return(posts.getShortHead(5), 200)

    def getUrlName(self):
        args = request.args
        try:
            linkString = args['name']
        except werkzeug.exceptions.BadRequestKeyError:
            abort(400, "You haven't specified any site that I should parse. Please specify a 'name' parameter.")
        return(linkString)

class Website:
    def __init__(self, urlName):
        self.url = ''
        self.data = {}
        self.createURL(urlName)
        self.readJsonData()

    def createURL(self, urlName):            
        linkIngredients = urlName.split('/')
        self.url = urlName
        if linkIngredients[0] != 'http:':
            self.url = 'http://' + self.url
        if linkIngredients[-1] != '.json':
            self.url = self.url + '/.json'

    def readJsonData(self):
        try:
            response = requests.get(self.url, headers={'User-agent': 'newUser'})
        except requests.exceptions.ConnectionError as e:
            abort(404, "I cannot connect to '" + link + "'.")
        except requests.exceptions.MissingSchema:
            abort(404, "The URL '"+ self.url + "' is invalid.")
                  
        try:
            datajson = json.loads(response.text)
        except ValueError:
            abort(400, "I cannot get JSON data from the given URL '" + self.url + "'.")

        self.data = datajson

class Posts:
    def __init__(self):
        self.data = {}

    def __init__(self, data):
        self.readPostDataFromJson(data)
    
    def readPostDataFromJson(self, data):
        try:
            posts = data['data']['children']
        except json.decoder.JSONDecodeError:
            abort(400, "The JSON data is not in the defined format.")

        self.data = []
        for post in posts:
            self.data.append(post['data'])

    def sortBy(self, sortingKey, isReverseOrdering=False):
        if sortingKey not in self.data[0].keys():
            abort(400, "The sorting key cannot be found in the JSON data.")

        sortedData = sorted(self.data, key=lambda i: i[sortingKey], reverse=isReverseOrdering)
        self.data = sortedData

    def getShortHead(self, N=10):
        outputData = []
        for i, postData in enumerate(self.data[:N]):
            outputData.append({'place' : i+1, 'title' : postData['title']})
        return(outputData)

    
api.add_resource(PostRankingAPI, "/posts")

app.run(debug=True)
