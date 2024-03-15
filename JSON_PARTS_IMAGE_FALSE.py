
import urllib
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from collections import Counter
import urllib.request, json
import objectpath
from serpapi import GoogleSearch
import nltk, string
import firebase_admin
from firebase_admin import credentials, storage
import requests
from datetime import datetime, timedelta

API_search = "FALSE"

# Initialize Firebase Admin SDK with service account key file
cred = credentials.Certificate('./underwater-capture-a4325-firebase-adminsdk-ea2lo-60515c0d0b.json')  # Path to your service account key file
firebase_admin.initialize_app(cred, {
    'storageBucket': 'underwater-capture-a4325.appspot.com'  # Replace 'your-storage-bucket' with your actual storage bucket
})

image_urls = []

# Retrieve image URLs from Firebase Storage
def get_image_urls():
    try:
        bucket = storage.bucket()
        blobs = bucket.list_blobs()

        for blob in blobs:
            if blob.content_type.startswith('image/'):
                image_urls.append(blob.generate_signed_url(timedelta(seconds=300), method='GET'))
                # urllib.request.urlretrieve(blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET'),".\\img.png")
                # image_urls.append(blob.public_url)

        return image_urls
    except Exception as e:
        print('Error retrieving image URLs:', e)
        return []


def save_results_to_json(results, filename):
    with open(filename, 'w') as json_file:
        json.dump(results, json_file, indent=4)


if __name__ == '__main__':
    image_urls = get_image_urls()
    if image_urls:
        for url in image_urls:
            print("Real image URL: ",end = '')
            print(url)
            params = {
                "engine": "google_lens",
                "url": url,
                "api_key": "684a70bb30d8e232062576c6881429981a99ece0d28d8301b5b9b313d865b8b0"
            }
            # don't waste the API searches unless needed
            if API_search == "TRUE":
                search = GoogleSearch(params)
                result = search.get_dict()
                jsonnn_tree = objectpath.Tree(result)
                result_tuple = tuple(jsonnn_tree.execute('$..json_endpoint'))
                all_json = str(result_tuple)
                all_json = all_json[2:]
                head, sep, tail = all_json.partition("'")
            elif API_search == "FALSE":
                head = "https://serpapi.com/searches/1cfe6ae7a633dcdc/65f438925b54eff485cbef38.json"
                print("Bluehead JSON: ",end = "")

            print(head)
            with urllib.request.urlopen(head) as url:
                data = json.load(url)
                # print(data.keys())
                search_results = data["visual_matches"]
                # print(search_results)
                # Aggregate all titles
                all_titles = ""
                for result in search_results:
                    title = result["title"]
                    # print(title)
                    all_titles = all_titles + " " + title
                    # remove some punctuation
                mapping_table = str.maketrans("/\,;.:-?!()[]{}-|#", "                  ")
                all_titles = all_titles.translate(mapping_table)
                all_titles = all_titles.lower()
                # print(all_titles)
                # search for most common phrases

                tokens = word_tokenize(all_titles)
                # print(tokens)


                #remove words like in out etc not to appear in most common
                nonsense_words = ["in","and","background","as","we","us","images","image","out","on","off","top","at","a","turn","into","of","some","for","the","who","what","-","that", "can","this","1","2","3","4","5","6","7","8","9","0","now" ]
                for word in nonsense_words:
                    tokens = list(filter(word.__ne__, tokens))
                # print(tokens)


                phrases_1 = ngrams(tokens, 1)  # different phrase lengths
                phrases_2 = ngrams(tokens, 2)
                phrases_3 = ngrams(tokens, 3)
                phrases_4 = ngrams(tokens, 4)
                phrase_freq_1 = Counter(phrases_1)
                phrase_freq_2 = Counter(phrases_2)
                phrase_freq_3 = Counter(phrases_3)
                phrase_freq_4 = Counter(phrases_4)

                # get (and print) the prases
                set1 = phrase_freq_1.most_common(10)
                set2 = phrase_freq_2.most_common(8)
                set3 = phrase_freq_3.most_common(3)
                set4 = phrase_freq_4.most_common(2)
                set = set1 + set2 + set3 + set4

                # dictionary of phrases
                Dict = {}
                for phrase in set:
                    Dict.update({phrase[0]: phrase[1]})
                for entry4 in set4:
                    phrase4 = entry4[0]
                    for entry3 in set3:
                        phrase3 = entry3[0]
                        if phrase3 <= phrase4:
                            Dict[phrase3] += 50
                        for entry2 in set2:
                            phrase2 = entry2[0]
                            if phrase2 <= phrase3:
                                Dict[phrase2] += 25
                            for entry1 in set1:
                                phrase1 = entry1[0]
                                if phrase1 <= phrase2:
                                    Dict[phrase1] += 2
                # highest value phrase
                max_score = 0
                for key in Dict:
                    if Dict[key] > max_score:
                        max_score = Dict[key]
                        max_word = key

                print("")
                print("Image recognition from google lens:")
                print(max_word)
                print("")

                test = phrase_freq_4.most_common(4)
                #print(type(test))


            # read the JSON result from API search


