from flask import Flask, jsonify
from flask_httpauth import HTTPBasicAuth
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
    "user1": "password1",
    "user2": "password2"
}

def geturl(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'DNT': '1',
        'Sec-GPC': '1',
        'Connection': 'keep-alive',
        'Cookie': '__ddg8_=IGcLC6E0Q7JxPRtF; __ddg9_=36.68.218.222; __ddg10_=1728400237; __ddg1_=CqvhdxWyxM9fVwRVUTia',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Priority': 'u=0, i',
        'TE': 'trailers'
    }

    # Make the GET request
    response = requests.get(url, headers=headers)
    return response

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

@auth.error_handler
def unauthorized():
    return jsonify({"status": "bad", "error": "Unauthorized"}), 401

@app.route('/new', methods=['GET'])
#@auth.login_required
def new():
    url = "https://komiku.id/"
    response = geturl(url)
    if response.status_code != 200:
        return jsonify({"status": "bad","error": "Failed to retrieve data"}), 500

    soup = BeautifulSoup(response.content, 'html.parser')
    titles = []
    link = []
    chapter = []
    for div in soup.find_all('div', class_='ls4j'):
        h3 = div.find('h3')
        if h3:
            titles.append(h3.get_text(strip=True))
        
        linkhref = div.find('a', class_='ls24')
        if linkhref:
            link.append(linkhref['href'])
            chapter.append(linkhref.get_text(strip=True))
    
    image = []
    for div in soup.find_all('div', class_='ls4v'):
        img = div.find('img')
        if img:
            image.append(img['src'])
    
    arr_group = []
    num=0
    for item in titles:
        linkrep = link[num].replace('https://komiku.id','')
        arr_group.append({'title':item, 'detail':linkrep, 'chapter': chapter[num], 'image':image[num]})
        num = num + 1
    return jsonify({"status": "ok", "data":arr_group})


@app.route('/<string:item_id>/', methods=['GET'])
#@auth.login_required
def detail(item_id):
    url = "https://komiku.id/"+item_id+'/'
    response = geturl(url)
    if response.status_code != 200:
        return jsonify({"status": "bad","error": "Failed to retrieve data"}), 500
    
    soup = BeautifulSoup(response.content, 'html.parser')
    image = []
    baca_komik = soup.find(id='Baca_Komik')
    if baca_komik:
        for img in baca_komik.find_all('img'):
            image.append(img['src'])
    return jsonify({"status": "ok", "data":{'content':image}})


@app.route('/manga/<string:item_id>/', methods=['GET'])
#@auth.login_required
def komik(item_id):
    url = "https://komiku.id/manga/"+item_id+'/'
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"status": "bad","error": "Failed to retrieve data"}), 500
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    image = ""
    for item in soup.find_all('div', class_='ims'):
        img = item.find('img')
        if img:
            image = img['src']

    arr_group = []
    for div in soup.find_all('td', class_='judulseries'):
        linkhref = div.find('a')
        if linkhref:
            link = linkhref['href'].replace('https://komiku.id','')
            chapter = linkhref.get_text(strip=True)
            arr_group.append({'chapter':chapter, 'detail':link})

    title = soup.find('h1').get_text(strip=True).replace('Komik ','')
    
    arr_genre = []
    for div in soup.find_all('li', class_='genre'):
        linkhref = div.find('a')
        if linkhref:
            link = linkhref['href'].replace('https://komiku.id','')
            genre = linkhref.get_text(strip=True)
            arr_genre.append({'genre':genre, 'detail':link})

    # arr_group = []
    # num=0
    # for item in titles:
    #     linkrep = link[num].replace('https://komikindo.lol','')
    #     arr_group.append({'title':item, 'detail':linkrep, 'image':image[num]})
    #     num = num + 1
    return jsonify({"status": "ok", "data":{'content':arr_group, 'image': image, 'title': title, 'genre': arr_genre}})

if __name__ == '__main__':
    app.run(debug=True,port=4000)