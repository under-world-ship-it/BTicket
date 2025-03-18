import requests
import yaml
from hashlib import md5 
KEY_PATH ="resources/KeyConfig.yaml"
with open(KEY_PATH, "r", encoding="utf-8") as f:
        config=yaml.safe_load(f)
CHAOJIYING_USERNAME = config['CHAOJIYING_USERNAME']
CHAOJIYING_PASSWORD = config['CHAOJIYING_PASSWORD']
CHAOJIYING_SOFT_ID =  config['CHAOJIYING_SOFT_ID']
class Chaojiying:
    def __init__(self):
        self.username = CHAOJIYING_USERNAME
        self.password =  md5(CHAOJIYING_PASSWORD.encode('utf8')).hexdigest()
        self.soft_id = CHAOJIYING_SOFT_ID
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files, headers=self.headers)
        return r.json()

    def ReportError(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()

def get_points(captcha_result):
    """
    解析识别结果
    :param captcha_result: 识别结果
    :return: 转化后的结果
    """
    groups = captcha_result.get('pic_str').split('|')
    locations = [[int(number) for number in item.split(',')] for item in groups]
    return locations
