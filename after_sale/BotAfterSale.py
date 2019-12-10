import json
import os
import random

import regex as re

dir_path = os.path.dirname(os.path.realpath(__file__))

END_SIGNAL = "_END_."


def get_random_item(messages):
    if messages is None or len(messages) == 0:
        return None
    return random.choice(messages)


class Bot:
    def __init__(self, config_file=os.path.join(dir_path, 'bot.config.json')):
        configurations = json.load(open(config_file, encoding='utf8'))
        self.story = configurations.get('story')
        self.parameters = configurations.get('parameters')
        self.cur_node = 0
        self.regex_para = configurations['regexPara']
        self.products = configurations.get('products')

    def interactive(self, customer_id, message=None):
        if self.parameters['p.logTime'] == "":
            customer = self.parameters.get('p.sample.customers').get(customer_id)
            if customer is None:
                print('customer_id {} not found!'.format(customer_id))
                return END_SIGNAL
            self.parameters['p.logTime'] = customer.get('logTime')
            self.parameters['p.productName'] = self.products.get(customer.get('product')).get('name')
            self.parameters['p.productUsage'] = self.products.get(customer.get('product')).get('use')
        if self.cur_node == -1:
            return END_SIGNAL
        if self.story[self.cur_node].get('type') == 'message':
            mess = get_random_item(self.story[self.cur_node].get('messages'))
            if mess == "{p.checkDosage}":
                self.cur_node = -1
                return self.check_dosage(message) + END_SIGNAL
            self.cur_node = self.story[self.cur_node]["next"]
            res = self.fill_parameters(mess)
            if self.cur_node == -1:
                res += END_SIGNAL
            return res
        else:
            for case in self.story[self.cur_node].get('cases'):
                case = self.story[self.cur_node].get('cases').get(case)
                for re_str in case['regex']:
                    if re.match(".*{}.*".format(re_str), message, re.IGNORECASE):
                        if self.story[self.cur_node].get('paras') != "":
                            self.parameters[self.story[self.cur_node].get('paras')] = re.findall(re_str, message,
                                                                                                 re.IGNORECASE)[0]
                        self.cur_node = case.get('next')
                        res = self.interactive(customer_id, message)
                        if self.cur_node == -1:
                            res += END_SIGNAL
                        return res
            # TH bot không thể xác định case
            self.cur_node = self.parameters['botCanNotSolve']
            return self.interactive(customer_id)

    def fill_parameters(self, message):

        paras = re.findall(self.regex_para, message)
        for para in paras:
            if para[1:-1] in self.parameters:
                message = re.sub(para, self.parameters.get(para[1:-1]), message)
        return re.sub("\\s+", " ", message).strip()

    def check_dosage(self, message):
        try:
            usage_check = re.findall('(?:một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười) viên', message)[0]
            if self.parameters['p.productUsage'] in usage_check:
                return "Quý khách đã dùng đúng liều. Mình nhớ uống thuốc đầy đủ để có hiệu quả tốt nhất ạ. Khi cần quý khách có thể gọi lại tổng đài vào giờ hành chính từ 8 - 17h các ngày trong tuần. Chúc quý khách một ngày tốt lành"
            else:
                return "Em thầy mình đã dùng sai liều rồi ạ. Mình nhớ uống {} viên mỗi ngày để có hiệu quả tốt nhất ạ. Khi cần quý khách có thể gọi lại tổng đài vào giờ hành chính từ 8 - 17h các ngày trong tuần. Chúc quý khách một ngày tốt lành".format(
                    self.parameters['p.productUsage'])
        except:
            return self.story[self.parameters.get('botCanNotSolve')]['messages'][0]


if __name__ == '__main__':
    bot = Bot()
    message = 'Mở đầu'
    while message != END_SIGNAL:
        message = input('User: ')
        message = bot.interactive('KH01', message)
        print(message)
