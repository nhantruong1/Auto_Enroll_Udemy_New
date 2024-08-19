import requests
from bs4 import BeautifulSoup
import json
from time import sleep
import os

try:
    ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
    CLIENT_ID = os.environ["CLIENT_ID"]
    DELAY_TIME = int(os.environ["DELAY_TIME"]) # Giây
except:
    print("Please import your secret environ")
    exit()

COUPON_DISCUDEMY_LINKS = [
    'https://www.discudemy.com/category/c',
    'https://www.discudemy.com/category/cpp',
    'https://www.discudemy.com/category/python',
    'https://www.discudemy.com/category/javascript',
    'https://www.discudemy.com/category/ios', 
    'https://www.discudemy.com/category/machine-learning',
    'https://www.discudemy.com/category/nodejs',
    'https://www.discudemy.com/category/vue',
    'https://www.discudemy.com/category/react-redux',
    'https://www.discudemy.com/category/mysql',
    'https://www.discudemy.com/category/django',
    'https://www.discudemy.com/category/ethical-hacking',
    'https://www.discudemy.com/category/debug-test'
] # Category links

class Auto_Enroll_Udemy:
    def __init__(self, access_token, client_id):
        self.access_token = access_token
        self.client_id = client_id
        self.list_enrroled = self.load_enrrolled()
        
    # Lấy id khóa học
    def get_id_course(self):
        # url = 'https://backen-udemycoupon.vercel.app/api/check-course-id'
        # data  = {
        #     "access_token" : self.access_token,
        #     "client_id" : self.client_id,
        #     "url_course" : self.url_course
        # }
        # headers = {
        #     'Content-Type': 'application/json'
        # }
        # response = requests.post(url=url, json=data, headers=headers) 
        # response_json = json.loads(response.text)
        # return response_json
        response = requests.get(url=self.url_course)
        soup = BeautifulSoup(response.text, 'html.parser')
        course_id = soup.find('body')['data-clp-course-id']
        return course_id
    
    # Mua khóa học
    def checkout_course(self):
        url = 'https://backen-udemycoupon.vercel.app/api/checkout'
        data = {
            "access_token" : self.access_token,
            "csrftoken" : self.client_id,
            "id_course" : self.id_course,
            "coupon_course" : self.coupon_course,
            "currency": "VND"
        }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url=url, json=data, headers=headers)
        response_json = json.loads(response.text)
        return True if response_json == 'Success' else False
                
    # Lấy danh sách khóa học đã mua
    def load_enrrolled(self):
        with open('enrolled.txt', 'r') as f:
            return f.read().split()

    # Ghi danh sách khóa học đã mua
    def write_enrrolled(self):
        with open('enrolled.txt', 'w') as f:
            f.write('\n'.join(self.list_enrroled))

    # Đăng ký khóa học
    def enrrol(self,url_course):
        if (url_course not in self.list_enrroled) and ('couponCode' in url_course):
            try:  
                self.url_course = url_course
                self.coupon_course = url_course.split('?couponCode=')[1]
                self.id_course = self.get_id_course()
                # Nếu khóa học mua thành công thì thêm vào danh sách đã mua
                if self.checkout_course():
                    self.list_enrroled.append(self.url_course)
                    self.write_enrrolled()
                    print(f'Enroll success: {self.url_course}')
                    # Đợi 5s để mua khóa học tiếp theo
                    sleep(DELAY_TIME)
            
            except:
                # Xử lý lỗi
                print(f'Enroll fail: {self.url_course}')

class Get_Coupon_Course:
    def __init__(self, auto_enroll):
        self.auto_enroll = auto_enroll
            
    # Gửi request lấy dữ liệu
    def get_requests(self, url):
        haaders = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        response = requests.get(url)
        return response.text

class Coupon_Discudemy_By_Category(Get_Coupon_Course):
    def __init__(self, url, auto_enroll):
        super().__init__(auto_enroll)
        self.url = url

    # Lấy danh sách các pages
    # Trả về mảng [1,2,3]    
    def get_list_page(self):
        html_content = self.get_requests(self.url)
        # Phân tích cú pháp HTML bằng BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Tìm phần tử chứa các trang
        pagination_section = soup.find('ul', class_='pagination3')

        # Tìm tất cả các thẻ <a> trong phần tử đó
        page_links = pagination_section.find_all('a')

        # Lấy giá trị bắt đầu và kết thúc
        start_page = None
        end_page = None

        for link in page_links:
            page_number = link.text.strip()
            if page_number.isdigit():
                page_number = int(page_number)
                if start_page is None:
                    start_page = page_number
                end_page = page_number

        # Tạo mảng từ giá trị bắt đầu đến giá trị kết thúc
        if start_page is not None and end_page is not None:
            pages = list(range(start_page, end_page + 1))
        else:
            pages = []
        
        return pages
        
    # Lấy danh sách link khóa học
    # Trả về mảng chứa các link khóa học trong 1 page
    def get_list_link(self, url):
        html_content = self.get_requests(url)
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all the 'section' elements with the class 'card'
        cards = soup.find_all('section', class_='card')
        
        # Extract and print the links
        links = []
        for card in cards:
            a_tag = card.find('a', class_='card-header')
            if a_tag and a_tag.get('href'):
                links.append("https://www.discudemy.com/go/" + a_tag['href'].split('/')[-1])
                
        return links
    
    # Lấy link khóa học udemy
    # Trả về link khóa học udemy
    def get_coupon(self,url):
        html_content = self.get_requests(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        link = soup.find('div', class_='ui segment').find('a', target='_blank').get('href')
        return link
    
    # Chạy chương trình
    def run(self):
        pages = self.get_list_page()
        for page in pages:
            page_url = self.url + f'/{page}'
            links = self.get_list_link(page_url)
            for link in links:
                coupon = self.get_coupon(link)
                self.auto_enroll.enrrol(coupon)

class Coupon_Discudemy(Get_Coupon_Course):
    def __init__(self, auto_enroll):
        super().__init__(auto_enroll)
        self.url = "https://www.discudemy.com/all"

    # Lấy danh sách các pages
    # Trả về mảng [1,2,3]    
    def get_list_page(self):
        max_page = 3
        pages = list(range(1, max_page + 1))
        return pages
        
    # Lấy danh sách link khóa học
    # Trả về mảng chứa các link khóa học trong 1 page
    def get_list_link(self, url):
        html_content = self.get_requests(url)
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all the 'section' elements with the class 'card'
        cards = soup.find_all('section', class_='card')
        
        # Extract and print the links
        links = []
        for card in cards:
            a_tag = card.find('a', class_='card-header')
            if a_tag and a_tag.get('href'):
                links.append("https://www.discudemy.com/go/" + a_tag['href'].split('/')[-1])
                
        return links
    
    # Lấy link khóa học udemy
    # Trả về link khóa học udemy
    def get_coupon(self,url):
        html_content = self.get_requests(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        link = soup.find('div', class_='ui segment').find('a', target='_blank').get('href')
        return link
    
    # Chạy chương trình
    def run(self):
        pages = self.get_list_page()
        for page in pages:
            page_url = self.url + f'/{page}'
            links = self.get_list_link(page_url)
            for link in links:
                coupon = self.get_coupon(link)
                self.auto_enroll.enrrol(coupon)


class Coupon_Udemy_Freebies(Get_Coupon_Course):
    def __init__(self, auto_enroll):
        super().__init__(auto_enroll)
        self.auto_enroll = auto_enroll
        self.url = 'https://www.udemyfreebies.com'
    
    def get_list_page(self):
        pages = list(range(1, 4)) # 53
        return pages

    def get_list_link(self,url):
        html_content = self.get_requests(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        cards = soup.find_all('div', class_='theme-block')
        links = []
        for card in cards:
            a_tag = card.find('a')
            if a_tag and a_tag.get('href'):
                links.append(self.url + "/out/" + a_tag['href'].split('/')[-1])
        return links

    def get_coupon(self,url):
        try:
            response = requests.head(url, allow_redirects=True)
            return response.url
        except requests.RequestException as e:
            return str(e)

    def run(self):
        pages = self.get_list_page()
        for page in pages:
            page_url = self.url + f'/free-udemy-courses/{page}'
            links = self.get_list_link(page_url)
            for link in links:
                coupon = self.get_coupon(link)
                self.auto_enroll.enrrol(coupon)

class Coupon_Udemy_Coupon(Get_Coupon_Course):
    def __init__(self, auto_enroll):
        super().__init__(auto_enroll)
        self.auto_enroll = auto_enroll
        self.url = 'https://udemycoupon-gamma.vercel.app'
    
    def get_list_coupon(self):
        max_course = 30
        url = f'https://backen-udemycoupon.vercel.app/api/fetchcoupon/1-{max_course}'
        html_content = self.get_requests(url)
        return json.loads(html_content)
    
    def run(self):
        coupons = self.get_list_coupon()
        for coupon in coupons:
            self.auto_enroll.enrrol(coupon['url'])

class Coupon_Real_Discount(Get_Coupon_Course):
    def __init__(self, auto_enroll):
        super().__init__(auto_enroll)
        self.auto_enroll = auto_enroll
        self.url = 'https://www.real.discount/'
        
    def get_list_coupon(self):
        max_course = 30
        url = f'https://www.real.discount/api-web/all-courses/?store=Udemy&page=1&per_page={max_course}&orderby=undefined&free=0&search=&language=&cat='
        response = self.get_requests(url)
        return json.loads(response)['results']
    
    def get_coupon(self,url):
        if not url.startswith('https://www.udemy.com'):
            return url.split('RD_PARM1=')[1]
        else:
            return url

    def run(self):
        coupons = self.get_list_coupon()
        for coupon in coupons:
            if "category" in coupon:
                url_udemy = self.get_coupon(coupon['url'])
                self.auto_enroll.enrrol(url_udemy)

if __name__ == '__main__':
    # Khởi tạo đối tượng auto_enroll
    auto_enroll = Auto_Enroll_Udemy(ACCESS_TOKEN, CLIENT_ID)

    print("[+] Enroll from discudemy")
    # Lấy coupon từ discudemy
    for link in COUPON_DISCUDEMY_LINKS:
        discudemy = Coupon_Discudemy(auto_enroll)
        discudemy.run()

    print("[+] Enroll from udemyfreebies")
    # Lấy coupon từ udemyfreebies
    freebies = Coupon_Udemy_Freebies(auto_enroll)
    freebies.run()

    print("[+] Enroll from udemycoupon")
    # Lấy coupon từ udemycoupon
    udemycoupon = Coupon_Udemy_Coupon(auto_enroll)
    udemycoupon.run()

    print("[+] Enroll from realdiscount")
    # Lấy coupon từ realdiscount
    real_discount = Coupon_Real_Discount(auto_enroll)
    real_discount.run()
