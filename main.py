# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def get_lat_lng(address):
    import urllib.request
    import json
    api_key = "AgtO8gDTfV7Cky0guuiXkfSyWaUw3fhxo6VMhlxGeAH62-jOjofWVD35gwnDKELX"
    encodeaddress = urllib.parse.quote(address, safe='')
    url = "http://dev.virtualearth.net/REST/v1/Locations?query=%s&key=%s" % (encodeaddress, api_key)
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    r = response.read().decode(encoding="utf-8")
    result = json.loads(r)
    latitude = result['resourceSets'][0]['resources'][0]['point']['coordinates'][0]
    longtitude = result['resourceSets'][0]['resources'][0]['point']['coordinates'][1]
    return str(latitude), str(longtitude)


def get_resturants(lat, long):
    import requests
    restaurants = list()
    name = dict()
    location_url_from_lat_long = "https://developers.zomato.com/api/v2.1/geocode?lat=" + lat + "&lon=" + long
    header = {"User-agent": "curl/7.43.0", "Accept": "application/json", "user_key": "ba6f342216e547eb88005d4a09e3754f"}
    response = requests.get(location_url_from_lat_long, headers=header)
    data = response.json()

    for restaurant in data["nearby_restaurants"]:
        details = {}
        details = {"id": restaurant["restaurant"]["id"],"name": restaurant["restaurant"]["name"],"url":restaurant["restaurant"]["url"],"address":restaurant["restaurant"]["location"]["address"],"user_rating":restaurant["restaurant"]["user_rating"]["aggregate_rating"],"cost_for_two":restaurant["restaurant"]["average_cost_for_two"],"cuisines":restaurant["restaurant"]["cuisines"]}
        restaurants.append(details)


    return restaurants


def get_reviews(restaurant):
    import requests
    review_corpus=""
    reviews = list()
    location_url_from_lat_long = "https://developers.zomato.com/api/v2.1/reviews?res_id=" + str(restaurant["id"])
    header = {"User-agent": "curl/7.43.0", "Accept": "application/json", "user_key": "ba6f342216e547eb88005d4a09e3754f"}
    response = requests.get(location_url_from_lat_long, headers=header)
    data = response.json()
    for review in data["user_reviews"]:
        review_corpus= review_corpus + review["review"]["review_text"]

    return review_corpus.lower()


def final_resturants_list(location):
    lat, long = get_lat_lng(location)
    restaurants = get_resturants(lat, long)
    for restaurant in restaurants:

        reviews = get_reviews(restaurant)
        restaurant["review_corpus"] = reviews
    return restaurants


def get_dataframe(restaurants):
    import pandas as pd
    df=pd.DataFrame(restaurants)
    df.set_index('id')
    return df

def remove_accented_chars(text):
    import unicodedata
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    return text

def remove_special_characters(text, remove_digits=False):
    import re
    pattern = r'[^a-zA-z\s]'
    text = re.sub(pattern, '', text)
    return text

def word_tokenise(text):
    from nltk.tokenize import word_tokenize
    text= word_tokenize(text)
    return text

def lemmatize_text(text):
    from nltk.stem.wordnet import WordNetLemmatizer

    lemmatizer = WordNetLemmatizer()
    text=lemmatizer.lemmatize(text)

    return text

def wordcloud(text):
    from wordcloud import WordCloud, STOPWORDS
    import matplotlib.pyplot as plt
    review=''
    for word in text:
        review=review + word+ " "


    wordcloud = WordCloud(stopwords=STOPWORDS, background_color='white', width=3000, height=3000).generate(review)


    return wordcloud

def word_cloud_all(df):
    df["word_cloud"]=df["review_corpus"].apply(wordcloud)
    return df



def clean_corpus (df):
    import pandas as pd
    df["review_corpus"] = df["review_corpus"].apply(remove_accented_chars)
    df["review_corpus"] = df["review_corpus"].apply(remove_special_characters)
    df["review_corpus"] = df["review_corpus"].apply(word_tokenise)
    #df["review_corpus"] = df["review_corpus"].apply(lemmatize_text)

    return df

def json_dumps(df):
    json=df.to_json()
    return json

if __name__ == '__main__':
    import pandas as pd
    import matplotlib.pyplot as plt
    location = input("Enter the location :")
    restaurants=final_resturants_list(location)
    df=get_dataframe(restaurants)
    df=clean_corpus(df)
    df=word_cloud_all(df)
    plt.imshow(df.at[0,"word_cloud"])
    plt.axis("off")
    plt.show()



