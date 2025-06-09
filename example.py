import requests

url = 'http://apis.data.go.kr/B553881/newRegistInfoService/newRegistInfoService'
params ={'serviceKey' : 'ClZAKel5nFb8HPJ4SJUQDpkwSfgeZUgGTrvb%2FWvHfYs8BmlXNFm8BZgPu68JclaJNI4xg73oVQGxj%2BfUJcf5AA%3D%3D', 'registYy' : '2017', 'registMt' : '11', 'vhctyAsortCode' : '1', 'registGrcCode' : '1', 'useFuelCode' : '2', 'cnmCode' : '000004', 'prposSeNm' : '1', 'sexdstn' : '남자', 'agrde' : '3', 'dsplvlCode' : '2', 'hmmdImpSeNm' : '국산', 'prye' : '2010' }

response = requests.get(url, params=params)
print(response.content)