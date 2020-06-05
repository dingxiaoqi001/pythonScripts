'''
@author: dingcui
@contact: dingcui@bupt.edu.cn
@file: dataManagement.py.py
@time: 2020/5/29 16:55
'''
import csv

from elasticsearch import Elasticsearch

es = Elasticsearch(["192.168.0.111:9200"], timeout=120)

def reprocessing_data(company, title, province, relation):
    offset1=len(company)
    offset2=len(title)
    for item in relation:
        if item[2] == '中标':
            item[0] = item[0]+offset1
        if item[2] == '位于':
            item[0] = item[0]+offset1+offset2
        if item[2] == '发布于':
            item[0] = item[0]+offset1+offset2
            item[1] = item[1]+offset1
    return relation

def item2csv(company, title, province):
    """
    每一行为一个key:value对
    :param data: dict
    """
    p_locals = ['company', 'title', 'province']
    flags = [(0, 0, 0), (1, 0, 0), (1, 1, 0)]
    for name, data, flag in zip(p_locals, [company, title, province], flags):
        with open('./' + name + '.csv', mode='a+', encoding='utf-8') as f:
            filenames = ["id:ID", "name"]
            w = csv.DictWriter(f, fieldnames=filenames)
            w.writeheader()
            for i in data.items():
                w.writerow({filenames[0]: i[1]+len(company)*flag[0]+len(title)*flag[1]+len(province)*flag[2], filenames[1]: i[0]})


def relation2csv(relation):
    p_locals = locals().copy()
    with open('./' + str(list(p_locals.keys())[0]) + '.csv', mode='a+', encoding='utf-8') as f:
        filenames = [":START_ID", ":END_ID", 'links']
        w = csv.DictWriter(f, fieldnames=filenames)
        w.writeheader()
        for i in relation:
            w.writerow({filenames[0]: i[0], filenames[1]: i[1], filenames[2]: i[2]})


def write2csv(company, title, province, relation):
    item2csv(company, title, province)
    relation2csv(relation)


def gather_data(company, company_id, title, title_id, province, province_id, relation, hits):
    for hit in hits:
        source = hit["_source"]

        company_len = len(company)
        company.setdefault(source["bid_company"]["name"], company_id)
        if len(company) != company_len:
            company_id += 1

        title_len = len(title)
        title.setdefault(source["title"], title_id)
        if len(title) != title_len:
            title_id += 1
        relation.append([title.get(source["title"]), company.get(source["bid_company"]["name"]), "中标"])
        try:
            province_len = len(province)
            province.setdefault(source["bid_company"]["province"], province_id)
            if province_len != len(province):
                province_id += 1
            relation.append(
                [province.get(source["bid_company"]["province"]), company.get(source["bid_company"]["name"]), "位于"])
        except:
            print('no bid company province')
        try:
            province_len = len(province)
            province.setdefault(source["project_province"], province_id)
            if province_len != len(province):
                province_id += 1
            relation.append([province.get(source["project_province"]), title.get(source["title"]), "发布于"])
        except:
            print('no project province')
    return company_id, title_id, province_id


def search_all_doc(total_count, company, company_id, title, title_id, province, province_id, relation):
    index_name = "data-warehouse-zhongzhao-common-bid-result-v3"
    page = es.search(
        index=index_name, scroll="2m", size=100,
    )
    sid = page["_scroll_id"]
    hits = page["hits"]["hits"]
    print(len(hits))
    while len(hits) > 0:
        # 处理hits的函数
        company_id, title_id, province_id = gather_data(company, company_id, title, title_id, province, province_id,
                                                        relation, hits)
        total_count += len(hits)
        if total_count >= 10000:
            break
        # 报错:RequestError(400, u'too_long_frame_exception', u'An HTTP line is larger than 4096 bytes.')解决方案:https://www.cnblogs.com/zbw911/p/11089171.html
        page = es.scroll(body={'scroll': '2m', 'scroll_id': sid},
                         request_timeout=30)
        sid = page["_scroll_id"]
        hits = page["hits"]["hits"]
        # print(flagg)

    relation = reprocessing_data(company, title, province, relation)

    # print(company, title, province, relation)
    write2csv(company, title, province, relation)


if __name__ == '__main__':
    total_count = 1
    company = {}
    company_id = 1
    title = {}
    title_id = 1
    province = {}
    province_id = 1
    relation = []
    search_all_doc(total_count, company, company_id, title, title_id, province, province_id, relation)
