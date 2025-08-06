from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
from selenium import webdriver
import time
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo

application = Flask(__name__) # initializing a flask app
app=application

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "cPHDOP col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            print(prod_html)
           # commentboxes = prod_html.find_all('div', {'class': "cPHDOP col-12-12"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            driver = webdriver.Chrome()
            driver.get(productLink)
            time.sleep(3)
            soup = bs(driver.page_source, 'html.parser')
            names=[]
            comment_heads=[]
            ratings=[]
            comments=[]
            # 2. Find your containers as before
            comment_box = soup.find_all("div", {"class":"cPHDOP col-12-12"})
            for i in comment_box:
                try:
                    #name.encode(encoding='utf-8')
                    name = i.find_all('p', class_="_2NsDsF AwS1CA")
                    if name:
                        names.append(name)

                except:
                    name = 'No Name'

                try:
                    #rating.encode(encoding='utf-8')
                    rating = i.find_all('div', class_="XQDdHH Ga3i8K")
                    if rating:
                        ratings.append(rating)


                except:
                    rating = 'No Rating'

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = i.find_all('p', class_="z9E0IG")
                    if commentHead:
                        comment_heads.append(commentHead)

                except:
                    commentHead = 'No Comment Heading'
                try:
                    custComment = i.find_all('div', class_="ZmyHeo")
                    if custComment:
                        comments.append(custComment)
                except Exception as e:
                    print("Exception while creating dictionary: ",e)
            name_tag=[]
            comment_head_tag=[]
            rating_tag=[]
            comment_tag=[]
            a=len(names)
            for i in range(a):
                if comment_box:
                    name_tag = [tag.get_text(strip=True) for tag in names[0]]
                    comment_head_tag = [tag.get_text(strip=True) for tag in comment_heads[0]]
                    rating_tag = [tag.get_text(strip=True) for tag in ratings[0]]
                    comment_tag = [tag.get_text(strip=True) for tag in comments[0]]
                    #print(name_tag)
                    #print(comment_head_tag)
                    #print(rating_tag)
                    #print(comment_tag)
            b=len(name_tag)
            print(b)
            for i in range(b):
                if name_tag[i] or rating_tag[i] or comment_head_tag[i] or comment_tag[i]:
                    mydict = {
                            "Product": searchString,
                            "Name": name_tag[i],
                            "Rating": rating_tag[i],
                            "CommentHead": comment_head_tag[i],
                            "Comment": comment_tag[i]
                        }

                reviews.append(mydict)
                client = pymongo.MongoClient("mongodb+srv://pwskills:vkkymongo@cluster0.ln0bt5m.mongodb.net/?retryWrites=true&w=majority")
                db = client['review_scrap']
                review_col = db['review_scrap_data']
                review_col.insert_many(reviews)
            driver.quit()
            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
	#app.run(debug=True)
