from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import random
import re
import sys
def login_to_instagram(driver, username_str, password_str):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(3)  #tunggu pagenya load
    
    #makasi om marc, kita hrs login dlu <3
    username_input = driver.find_element(By.NAME, 'username')
    password_input = driver.find_element(By.NAME, 'password')
    
    username_input.send_keys(username_str)
    password_input.send_keys(password_str)
    password_input.send_keys(Keys.RETURN)
    
    time.sleep(10) #tunggu load

    if "two_factor" in driver.current_url or "challenge" in driver.current_url:
        # print("Two-factor authentication or challenge required. Please resolve manually.")
        time.sleep(30)
    elif "login" in driver.current_url:
        # print("Login failed. Check credentials.")
        driver.quit()
        return False

    # print("Login successful!")
    return True

def fetch_google_search_results(keyword, max_links=5):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    #ke home page gugel dlu
    driver.get("https://www.google.com")
    time.sleep(3)

    #cari search bar & masukin keyword query
    search_bar = driver.find_element(By.NAME, "q")
    search_bar.send_keys(f"{keyword} site:instagram.com")
    search_bar.send_keys(Keys.RETURN)
    time.sleep(random.uniform(5, 7))
    
    # print("Search completed!")

    #ambil link websitenya
    links = []
    results = driver.find_elements(By.CSS_SELECTOR, 'a')

    #regex buat filter website yg mengandung /p/ doang --> post
    pattern = r"^https://www\.instagram\.com/[^/]+/p/[a-zA-Z0-9_-]+/?$"

    for result in results:
        href = result.get_attribute("href")
        if href and re.match(pattern, href) and href not in links and len(links) < max_links:
            links.append(href)
    
    return links

def fetch_instagram_posts_with_details(username, password, keyword):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    #klo ga berhasil login
    if not login_to_instagram(driver, username, password):
        return []

    #klo crawl link ga berhasil
    post_urls = fetch_google_search_results(keyword)
    if not post_urls:
        # print("No valid Instagram links found.")
        driver.quit()
        return []

    #crawl isi per post
    posts = []
    for post_url in post_urls:
        # print(f"Processing Instagram post: {post_url}")
        driver.get(post_url)
        time.sleep(5)

        #USERNAME
        try:
            #crawl username
            username_element = driver.find_element(By.CSS_SELECTOR, "header a[href]")
            username = username_element.text
        #NoSuchElementException ini muncul kalo div di find_element ga ditemukan
        except NoSuchElementException:
            username = "Unknown"

        #CAPTION (sama mentions & hashtag)
        try:
            caption_element = driver.find_element(By.CSS_SELECTOR, "h1._ap3a._aaco._aacu._aacx._aad7._aade")
            caption = caption_element.text.strip() #ini buat captionnya doang

            #hapus semua enter
            caption = ''.join(caption.splitlines())
            
        except NoSuchElementException:
            caption = "No caption"

        # COMMENTS
        comments = []
        max_comments = 5 
        max_replies = 15
        comment_count = 0
        reply_count = 0 

        try:
            comment_elements = driver.find_elements(By.CSS_SELECTOR, "span._ap3a._aaco._aacu._aacx._aad7._aade")

            #kalo gaada komen di postnya
            if not comment_elements:
                comments.append({'comment': "No comments found", 'is_reply': False})
            else:
                for comment_element in comment_elements:
                    #maks 10 komen yg di crawl, klo lebih, break
                    if comment_count >= max_comments:
                        break

                    comment_text = comment_element.text
                    #is_reply ini status apakah comment yg dicrawl itu comment utama atau comment dari more replies
                    comments.append({'comment': comment_text, 'is_reply': False})
                    comment_count += 1

                    try:
                        #MORE REPLIES
                        #hrus click button view replies dlu baru muncul
                        view_replies = comment_element.find_element(By.XPATH, ".//a[contains(text(), 'View replies')]")
                        view_replies.click()
                        time.sleep(2)

                        reply_elements = comment_element.find_elements(By.XPATH, ".//following-sibling::ul//span[@class='_ap3a _aaco _aacu _aacx._aad7._aade']")
                        for reply_element in reply_elements:
                            if reply_count >= max_replies:
                                break
                            comments.append({'comment': reply_element.text, 'is_reply': True})
                            reply_count += 1
                    except NoSuchElementException:
                        pass
        except NoSuchElementException:
            comments.append("No comments found")

        posts.append({
            'username': username,
            'caption': caption,
            #'hashtags': hashtags,
            'comments': comments,
            'post_url': post_url
        })
    
    driver.quit()
    # print(f"Crawled {len(posts)} posts.")
    return posts

username = "xxx"
password = "xxx"
#keyword = "prabowo gibran"
keyword = sys.argv[1]
keyword=keyword.replace("#"," ")

posts = fetch_instagram_posts_with_details(username, password, keyword)

crawling_result = []

for post in posts:
    # Tambahkan caption ke dalam crawling_result
    crawling_result.append(post['caption'])
    
    # Tambahkan semua komentar ke dalam crawling_result
    for comment in post['comments']:
        crawling_result.append(comment['comment'])

# Print the collected posts
# print("Posts collected:")
# for post in posts:
#     print(f"Post URL: {post['post_url']}")
#     print(f"Username: {post['username']}")
#     print(f"Caption: {post['caption']}")
# #print(f"Hashtags: {', '.join(post['hashtags'])}")
#     print("Comments:")
#     for comment in post['comments']:
#          print(f"  {comment}")
#     print("-" * 100)


#Preprocessing
import json
import validators
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

# Inisialisasi Sastrawi Stemmer dan Stopword Remover
stemmer = StemmerFactory().create_stemmer()
stopword_remover = StopWordRemoverFactory().create_stop_word_remover()

def preprocess(text):
    split_text = text.split()
    
    #pemrosesan untuk hashtag
    patternUnderscore = r"(#.*_.*)" #luar_biasa_indah => luar biasa indah
    patternLowUpCase = r"(#[A-Z].*[a-z][A-Z])" #luarbiasaindah => luarbiasaindah
    splitterLowUpCase = r'(?<=[a-z])(?=[A-Z])' #LuarBiasaIndah => Luar Biasa Indah

    preprocessed_text = []
    for word in split_text:
        #pemrosesan hashtag
        if word.startswith("#"):
            word = word.replace("#", "")
            if re.search(patternUnderscore, word): #klo underscore
                word = word.replace("_", " ") #hastag di replace jadi kosong, _ jadi spasi
            elif re.search(patternLowUpCase, word):
                word = " ".join(re.split(splitterLowUpCase, word))
        preprocessed_text.append(word)

    #case folding
    preprocessed_text = [word.lower() for word in preprocessed_text]

    #hapus mention
    preprocessed_text = [word.replace("@", "") if word.startswith("@") else word for word in preprocessed_text]

    #penghapusan link-link
    preprocessed_text = [word for word in preprocessed_text if not validators.url(word)]

    #penghapusan simbol
    preprocessed_text = [re.sub(r'[^a-zA-Z0-9\s]', ' ', word) for word in preprocessed_text]

    #gabung
    text = ' '.join(preprocessed_text).strip()
    text = re.sub(' +', ' ', text)

    #stemming dan stopwords removal
    stem_text = stemmer.stem(text)
    stop_text = stopword_remover.remove(stem_text)

    return stop_text

#preprocess hasil crawling
preprocessed_crawling = []
for text in crawling_result:
    preprocessed_crawling.append(preprocess(text))
preprocessed_crawling = [preprocess(text) for text in crawling_result]

#TF-IDF dan Similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import jaccard_score
from sklearn.preprocessing import Binarizer

#tambahkan query pencarian
#search_query = "prabowo gibran bersama bertugas"
search_query = keyword
preprocessed_crawling.append(preprocess(search_query))

#buat objek TF-IDF
tfidf = TfidfVectorizer(norm=None, sublinear_tf=True)
vector_tfidf = tfidf.fit_transform(preprocessed_crawling)

#metode similarity: cosine dan jaccard
#method = "cosine" #misal, bisa diganti
method = sys.argv[2]
distances = []
if method == "cosine":
    for i in range(len(preprocessed_crawling) - 1):
        dist = cosine_similarity(vector_tfidf[i].toarray(), vector_tfidf[-1].toarray())
        distances.append(dist[0][0]) #akses skalarnya krn output array 2D
elif method == "jaccard":
    binarizer = Binarizer()
    vector_tfidf_binarized = binarizer.fit_transform(vector_tfidf.toarray())
    for i in range(len(preprocessed_crawling) - 1):
        dist = jaccard_score(vector_tfidf_binarized[i], vector_tfidf_binarized[-1], average='binary')
        distances.append(dist)

#masukkan ke list buat dikirim ke user
crawling_instagram = []
for i in range(len(crawling_result)):
    crawling_instagram.append({
        'ori': crawling_result[i],
        'preprocessed': preprocessed_crawling[i],
        'sim': distances[i]
    })

# output json
output = json.dumps(crawling_instagram, indent=2) #supaya lebih mudah dibaca makanya pake indent=2
print(output)
