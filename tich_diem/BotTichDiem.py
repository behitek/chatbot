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
        if self.parameters['p.customerName'] == "":
            customer = self.parameters.get('p.sample.customers').get(customer_id)
            if customer is None:
                print('customer_id {} not found!'.format(customer_id))
                return END_SIGNAL
            self.parameters['p.customerName'] = customer.get('name')
            self.parameters['p.gender'] = customer.get('gender')
            self.parameters['p.productName'] = self.products.get(customer.get('product')).get('name')
        if self.cur_node == -1:
            return END_SIGNAL
        if self.story[self.cur_node].get('type') == 'message':
            mess = get_random_item(self.story[self.cur_node].get('messages'))
            self.cur_node = self.story[self.cur_node]["next"]
            return self.fill_parameters(mess)
        else:
            for case in ['know', 'notKnow']:
                case = self.story[self.cur_node].get('cases').get(case)
                for re_str in case['regex']:
                    if re.match(".*{}.*".format(re_str), message, re.IGNORECASE):
                        if self.story[self.cur_node].get('paras') != "":
                            self.parameters[self.story[self.cur_node].get('paras')] = re.findall(re_str, message,
                                                                                                 re.IGNORECASE)[0]
                        self.cur_node = case.get('next')
                        return self.interactive(customer_id, message)
            # TH bot không thể xác định case
            self.cur_node = self.parameters['botCanNotSolve']
            return self.interactive(customer_id)

    def fill_parameters(self, message):

        paras = re.findall(self.regex_para, message)
        for para in paras:
            if para[1:-1] in self.parameters:
                message = re.sub(para, self.parameters.get(para[1:-1]), message)
        res = re.sub("\\s+", " ", message).strip()
        if self.cur_node == -1:
            res += END_SIGNAL
        return res


if __name__ == '__main__':
    bot = Bot()
    message = 'Mở đầu'
    while message != END_SIGNAL:
        message = input('User: ')
        message = bot.interactive('KH01', message)
        print(message)
