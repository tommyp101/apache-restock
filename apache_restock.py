import requests
from bs4 import BeautifulSoup
import json
import time
import os



#######################################################################################################
#######################################################################################################



webhook_url = os.environ.get("WEBHOOK_URL")


nike = [
    ["https://www.nike.com/t/air-max-270-bowfin-mens-shoe-0x4rcw/AJ7200-005", ["6", "6.5", "7", "9"]],
    ["https://www.nike.com/t/zoom-kd11-basketball-shoe-ZKqRs9", []],
    ["https://www.nike.com/t/vapor-power-2-training-backpack-a0e338", []],
    ["https://www.nike.com/t/gym-club-training-duffel-bag-pvTjnpml/BA5490-652", []]
]

adidas = [
    ["https://www.adidas.com/us/pod-s3.1-shoes/AQ1059.html", []],
    ["https://www.adidas.com/us/badge-of-sport-cities-tee/DX0403.html", []],
    ["https://www.adidas.com/us/ultimate365-shorts/CE0449.html", []],
    ["https://www.adidas.com/us/daybreak-2-backpack/CK0290.html", []]
]

supreme = [
    ["https://www.supremenewyork.com/shop/jackets/zzlaqusmv/zoyc8fzxa", []],
    ["https://www.supremenewyork.com/shop/tops-sweaters/jkpuamv9q/qd87sp6tc", []],
    ["https://www.supremenewyork.com/shop/hats/usr9uodc8/j0mgc2qpb", []]
]



#######################################################################################################
#######################################################################################################








site_links = {
    "nike": [],
    "adidas": [],
    "supreme": []
}
for nike_link in nike:
    site_links["nike"].append({
        "link": nike_link[0],
        "wanted_sizes": nike_link[1],
        "last_in_stock_sizes": [],
        "last_in_stock": False
    })
for adidas_link in adidas:
    site_links["adidas"].append({
        "link": adidas_link[0],
        "wanted_sizes": adidas_link[1],
        "last_in_stock_sizes": [],
        "last_in_stock": False,
        "adidas_item_id": adidas_link[0][-11:-5]
    })
for supreme_link in supreme:
    site_links["supreme"].append({
        "link": supreme_link[0],
        "wanted_sizes": supreme_link[1],
        "last_in_stock_sizes": [],
        "last_in_stock": False
    })


cookie = os.environ.get("COOKIE")
user_agent = os.environ.get("USER_AGENT")
webscrape_data = {
    "proxies": {
        "http": "178.128.168.88",
        "http": "89.38.144.95",
        "http": "145.239.252.51",
        "http": "178.128.173.108",
        "http": "185.42.221.246"
    },
    "headers": {
        "nike": {
            "cookie": cookie
            "user-agent": user_agent
        },
        "adidas": {
            "user-agent": user_agent
        },
        "supreme": {
            "user-agent": user_agent
        }
    },
    "adidas_availability_link": "https://www.adidas.com/api/products/{0}/availability"
}






def send_embed(embed_data):
    global webscrape_data

    data = {
        "embeds": [embed_data]
    }
    send_attempts = 0
    while send_attempts < 3:
        embed_request = requests.post(webhook_url, json=data)
        if embed_request.status_code in [204, 200]:
            break
        else:
            print("Sending Embed Failed [RETRYING]: {0} because {1}\n\nData: {2}".format(embed_request.status_code, embed_request.reason, data))
            data = {
                "embeds": [{
                    "title": embed_data["title"],
                    "description": embed_data["description"],
                    "url": embed_data["url"],
                    "color": embed_data["color"]
                }]
            }
            if send_attempts != 0:
                time.sleep(30)
            send_attempts += 1






def get_nike_link_data(link):
    global webscrape_data

    request = requests.get(link, headers=webscrape_data["headers"]["nike"], proxies=webscrape_data["proxies"])
    if request.status_code != 200:
        print("Request Failed: {0} because {1}\n\nLink: {2}".format(request.status_code, request.reason, link))
    else:

        html_text = (request.text)
        soup = BeautifulSoup(html_text, features="lxml")

        image_element_list = soup.body.find("img", {"class": "css-10f9kvm u-full-width u-full-height css-1436l9y"})
        return ({
            "item_name": image_element_list["alt"],
            "image_url": image_element_list["src"]
        })



def get_adidas_link_data(link):
    global webscrape_data

    request = requests.get(link, headers=webscrape_data["headers"]["adidas"], proxies=webscrape_data["proxies"])
    if request.status_code != 200:
        print("Request Failed: {0} because {1}\n\nLink: {2}".format(request.status_code, request.reason, link))
    else:

        html_text = (request.text)
        soup = BeautifulSoup(html_text, features="lxml")

    image_element_list = soup.body.find("div", {"class": "images_container___3KxTB"}).img
    return ({
        "item_name": image_element_list["alt"],
        "image_url": image_element_list["src"]
    })



def get_supreme_link_data(link):
    global webscrape_data

    request = requests.get(link, headers=webscrape_data["headers"]["supreme"], proxies=webscrape_data["proxies"])
    if request.status_code != 200:
        print("Request Failed: {0} because {1}\n\nLink: {2}".format(request.status_code, request.reason, link))
    else:

        html_text = (request.text)
        soup = BeautifulSoup(html_text, features="lxml")

        image_element_list = soup.body.find("img", {"id": "img-main"})
        return ({
            "item_name": image_element_list["alt"],
            "image_url": image_element_list["src"]
        })





def get_nike_link_stock(link):
    global webscrape_data
    request = requests.get(link, headers=webscrape_data["headers"]["nike"], proxies=webscrape_data["proxies"])
    if request.status_code != 200:
        print("Getting Nike Stock Request Failed: {0} because {1}\n\nLink: {2}".format(request.status_code, request.reason, link))
    else:
        html_text = (request.text)
        soup = BeautifulSoup(html_text, features="lxml")

        if soup.body.find("button", {"aria-label": "Add to Cart"}) == None:
            return {
                "item_in_stock": False,
                "in_stock": [],
                "out_of_stock": []
            }

        if soup.body.find("div", {"name": "skuAndSize"}) == None:
            return {
                "item_in_stock": True,
                "in_stock": [],
                "out_of_stock": []
            }
        element_list = soup.body.find("div", {"name": "skuAndSize"}).find_all()
        nike_stock_attributes = {
            "in_stock": ["data-css-1iiusdt", "data-css-lv2huc", "data-css-ikkzrh"],
            "out_of_stock": ["data-css-yyh50b", "data-css-137acxc", "data-css-y50moq"]
        }
        stock_list = {
            "item_in_stock": True,
            "in_stock": [],
            "out_of_stock": []
        }
        for element in element_list:
            if str(element).startswith("<label"):
                if any(attribute in element.attrs for attribute in nike_stock_attributes["in_stock"]):
                    stock_list["in_stock"].append(element.text)
                elif any(attribute in element.attrs for attribute in nike_stock_attributes["out_of_stock"]):
                    stock_list["out_of_stock"].append(element.text)
        return stock_list



def get_adidas_link_stock(link_code):
    global webscrape_data
    link = webscrape_data["adidas_availability_link"].format(link_code)
    request = requests.get(link, headers=webscrape_data["headers"]["adidas"], proxies=webscrape_data["proxies"])
    if request.status_code != 200:
        print("Getting Adidas Stock Request Failed: {0} because {1}\n\nLink: {2}".format(request.status_code, request.reason, link))
    else:

        sizes_dict = request.json()
        if sizes_dict["availability_status"] != "IN_STOCK":
            return {
                "item_in_stock": False,
                "in_stock": [],
                "out_of_stock": []
            }

        adidas_stock_attributes = {
            "in_stock": ["IN_STOCK"],
            "out_of_stock": ["NOT_AVAILABLE"]
        }
        stock_list = {
            "item_in_stock": True,
            "in_stock": [],
            "out_of_stock": []
        }
        for sizes in sizes_dict["variation_list"]:
            if sizes["size"] == "ONE SIZE":
                return stock_list
            elif sizes["availability_status"] in adidas_stock_attributes["in_stock"]:
                stock_list["in_stock"].append(sizes["size"])
            elif sizes["availability_status"] in adidas_stock_attributes["out_of_stock"]:
                stock_list["out_of_stock"].append(sizes["size"])
        return stock_list



def get_supreme_link_stock(link):
    global webscrape_data
    request = requests.get(link, headers=webscrape_data["headers"]["supreme"], proxies=webscrape_data["proxies"])
    if request.status_code != 200:
        print("Getting Supreme Stock Request Failed: {0} because {1}\n\nLink: {2}".format(request.status_code, request.reason, link))
    else:
        html_text = (request.text)
        soup = BeautifulSoup(html_text, features="lxml")

        if soup.body.find("fieldset", {"id": "add-remove-buttons"}).input == None:
            return {
                "item_in_stock": False,
                "in_stock": [],
                "out_of_stock": []
            }
        if soup.body.find("select", {"name": "size"}) == None:
            return {
                "item_in_stock": True,
                "in_stock": [],
                "out_of_stock": []
            }

        element_list = soup.body.find("select", {"name": "size"}).find_all()
        stock_list = {
            "item_in_stock": True,
            "in_stock": [],
            "out_of_stock": []
        }
        for element in element_list:
            stock_list["in_stock"].append(element.text)
        return stock_list




#START


data_list = get_supreme_link_data("https://www.supremenewyork.com/shop/jackets/zzlaqusmv/zoyc8fzxa")
send_embed({
    "title": "SUPREME Item Restock (click here)",
    "description": data_list["item_name"],
    "color": 0x1872e0,
    "image": {"url": "https:" + data_list["image_url"]},
    "url": "https://www.supremenewyork.com/shop/jackets/zzlaqusmv/zoyc8fzxa"
})



for index, nike_link in enumerate(site_links["nike"]):
    stock_list = get_nike_link_stock(nike_link["link"])

    if stock_list["item_in_stock"] == False:
        site_links["nike"][index]["last_in_stock"] = False
    else:
        site_links["nike"][index]["last_in_stock"] = True
        if nike_link["wanted_sizes"] == []:
            site_links["nike"][index]["last_in_stock_sizes"] = stock_list["in_stock"]
        else:
            for size in nike_link["wanted_sizes"]:
                if size in stock_list["in_stock"]:
                    site_links["nike"][index]["last_in_stock_sizes"].append(size)




for index, adidas_link in enumerate(site_links["adidas"]):
    stock_list = get_adidas_link_stock(adidas_link["adidas_item_id"])

    if stock_list["item_in_stock"] == False:
        site_links["adidas"][index]["last_in_stock"] = False
    else:
        site_links["adidas"][index]["last_in_stock"] = True
        if adidas_link["wanted_sizes"] == []:
            site_links["adidas"][index]["last_in_stock_sizes"] = stock_list["in_stock"]
        else:
            for size in adidas_link["wanted_sizes"]:
                if size in stock_list["in_stock"]:
                    site_links["adidas"][index]["last_in_stock_sizes"].append(size)




for index, supreme_link in enumerate(site_links["supreme"]):
    stock_list = get_supreme_link_stock(supreme_link["link"])

    if stock_list["item_in_stock"] == False:
        site_links["supreme"][index]["last_in_stock"] = False
    else:
        site_links["supreme"][index]["last_in_stock"] = True
        if supreme_link["wanted_sizes"] == []:
            site_links["supreme"][index]["last_in_stock_sizes"] = stock_list["in_stock"]
        else:
            for size in supreme_link["wanted_sizes"]:
                if size in stock_list["in_stock"]:
                    site_links["supreme"][index]["last_in_stock_sizes"].append(size)



    # stock_list = get_nike_link_stock(nike_link[0])
    #
    # if nike_link[1] == []:
    #     site_links["nike"][index][2] = stock_list["in_stock"]
    # else:
    #     for size in nike_link[1]:
    #         if size in stock_list["in_stock"]:
    #             site_links["nike"][index][2].append(size)



while True:
    time.sleep(60)


    for index, nike_link in enumerate(site_links["nike"]):
        new_stock_list = get_nike_link_stock(nike_link["link"])
        new_last_stock_list = []
        if new_stock_list["item_in_stock"] == False:
            site_links["nike"][index]["last_in_stock"] = False
        else:
            if new_stock_list["in_stock"] == []:
                if nike_link["last_in_stock"] == False:
                    link_data = get_nike_link_data(nike_link["link"])
                    send_embed({
                        "title": "Item Restock (click here)",
                        "description": link_data["item_name"],
                        "color": 0x1872e0,
                        "image": {"url": link_data["image_url"]},
                        "url": nike_link["link"]
                    })
            else:
                for size in new_stock_list["in_stock"]:
                    if (size in nike_link["wanted_sizes"]) or (nike_link["wanted_sizes"] == []):
                        new_last_stock_list.append(size)
                        if not size in nike_link["last_in_stock_sizes"]:
                            link_data = get_nike_link_data(nike_link["link"])
                            send_embed({
                                "title": "Item Restock Size {0} (click here)".format(size),
                                "description": link_data["item_name"],
                                "color": 0x1872e0,
                                "image": {"url": link_data["image_url"]},
                                "url": nike_link["link"]
                            })
        site_links["nike"][index]["last_in_stock_sizes"] = new_last_stock_list




    for index, adidas_link in enumerate(site_links["adidas"]):
        new_stock_list = get_adidas_link_stock(adidas_link["adidas_item_id"])
        new_last_stock_list = []
        if new_stock_list["item_in_stock"] == False:
            site_links["adidas"][index]["last_in_stock"] = False
        else:
            if new_stock_list["in_stock"] == []:
                if adidas_link["last_in_stock"] == False:
                    link_data = get_adidas_link_data(adidas_link["link"])
                    send_embed({
                        "title": "Item Restock (click here)",
                        "description": link_data["item_name"],
                        "color": 0x1872e0,
                        "image": {"url": link_data["image_url"]},
                        "url": adidas_link["link"]
                    })
            else:
                for size in new_stock_list["in_stock"]:
                    if (size in adidas_link["wanted_sizes"]) or (adidas_link["wanted_sizes"] == []):
                        new_last_stock_list.append(size)
                        if not size in adidas_link["last_in_stock_sizes"]:
                            link_data = get_adidas_link_data(adidas_link["link"])
                            send_embed({
                                "title": "Item Restock Size {0} (click here)".format(size),
                                "description": link_data["item_name"],
                                "color": 0x1872e0,
                                "image": {"url": link_data["image_url"]},
                                "url": adidas_link["link"]
                            })
        site_links["adidas"][index]["last_in_stock_sizes"] = new_last_stock_list




    for index, supreme_link in enumerate(site_links["supreme"]):
        new_stock_list = get_supreme_link_stock(supreme_link["link"])
        new_last_stock_list = []
        if new_stock_list["item_in_stock"] == False:
            site_links["supreme"][index]["last_in_stock"] = False
        else:
            if new_stock_list["in_stock"] == []:
                if supreme_link["last_in_stock"] == False:
                    link_data = get_supreme_link_data(supreme_link["link"])
                    send_embed({
                        "title": "Item Restock (click here)",
                        "description": link_data["item_name"],
                        "color": 0x1872e0,
                        "image": {"url": link_data["image_url"]},
                        "url": supreme_link["link"]
                    })
            else:
                for size in new_stock_list["in_stock"]:
                    if (size in supreme_link["wanted_sizes"]) or (supreme_link["wanted_sizes"] == []):
                        new_last_stock_list.append(size)
                        if not size in supreme_link["last_in_stock_sizes"]:
                            link_data = get_supreme_link_data(supreme_link["link"])
                            send_embed({
                                "title": "Item Restock Size {0} (click here)".format(size),
                                "description": link_data["item_name"],
                                "color": 0x1872e0,
                                "image": {"url": link_data["image_url"]},
                                "url": supreme_link["supreme"]
                            })
        site_links["supreme"][index]["last_in_stock_sizes"] = new_last_stock_list
