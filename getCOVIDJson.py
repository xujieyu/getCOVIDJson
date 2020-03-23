# 将省转换成拼音
PINYIN = ['hubei', 'guangdong', 'zhejiang', 'chongqing', 'hunan', 'anhui', 'beijing', 'shanghai', 'henan', 'sichuan', 'shandong', 'guangxi', 'jiangxi', 'fujian', 'jiangsu', 'hainan', 'liaoning', 'shanxi', 'yunnan', 'tianjin', 'heilongjiang', 'hebei', 'shanxi', 'xianggang', 'guizhou', 'jilin', 'gansu', 'ningxia', 'taiwan', 'xinjiang', 'aomen', 'neimenggu', 'qinghai', 'xizang']
NAME = ['湖北', '广东', '浙江', '重庆', '湖南', '安徽', '北京', '上海', '河南', '四川', '山东', '广西', '江西', '福建', '江苏', '海南', '辽宁', '陕西', '云南', '天津', '黑龙江', '河北', '山西', '香港', '贵州', '吉林', '甘肃', '宁夏', '台湾', '新疆', '澳门', '内蒙古', '青海', '西藏']
#NAME = ['湖北']
import json
import time
import requests

#通过url获取数据
import urllib.request
def get_record(url):
    resp = urllib.request.urlopen(url)
    ele_json = json.loads(resp.read())
    return ele_json

def getJson():
    filename = 'Wuhan-2019-nCoV.json'
    data = []
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)

    #先筛选出我们需要的数据
    dt = "2020-02-18"
    timeArray = time.strptime(dt, "%Y-%m-%d")
    chooseTime = time.mktime(timeArray)
    resultView = []#筛选view页面需要的数据
    resultHome = []#筛选home（index)页面需要的数据
    resultHubei = []#赛选曲线图需要的数据
    for item in data:
        tempArray = time.strptime(item['date'], "%Y-%m-%d")
        tempTime = time.mktime(tempArray)
        item['date'] = item['date'][5:]
        if(tempTime >= chooseTime):
            if(item['province'][0:3] == '黑龙江' or item['province'][0:3] == '内蒙古'):
                item['province'] = item['province'][0:3]
            else:
                item['province'] = item['province'][0:2]
            if(item['countryCode'] == 'CN'):
                resultView.append(item)
                if(item['city'] == ''):
                    resultHome.append(item)
                    if(item['province'] == '' or item['provinceCode'] == '420000'):
                        resultHubei.append(item)


     # 处理index页面需要的数据
    index_info = {}
    times = 2
    today = 0
    yesterday = 0
    be_yesterday = 0
    for index in range(len(resultHome)-1,-1,-1):
        if(resultHome[index]['country'] == '中国' and resultHome[index]['province'] == '' and times == 0):
            be_yesterday = index
            break
        if(resultHome[index]['country'] == '中国' and resultHome[index]['province'] == '' and times == 1):
            yesterday = index
            times =0
        if(resultHome[index]['country'] == '中国' and resultHome[index]['province'] == '' and times == 2):
            today = index
            times = 1
    index_info['updateTime'] = resultHome[today]['date']
    index_info['china_total'] = resultHome[today]
    add_data = {}
    add_data['confirmed'] = resultHome[yesterday]['confirmed'] - resultHome[be_yesterday]['confirmed']
    add_data['suspected'] =resultHome[yesterday]['suspected'] - resultHome[be_yesterday]['suspected']
    add_data['cured'] = resultHome[yesterday]['cured'] - resultHome[be_yesterday]['cured']
    add_data['dead'] = resultHome[yesterday]['dead'] - resultHome[be_yesterday]['dead']
    index_info['china_add'] = add_data
    list = []
    list2 = []
    list3 = []
    for item in resultHome:
        if(item['date'] == resultHome[today]['date'] and item['province'] != '' and item['city'] == ''):
            list.append(item)
        elif(item['date'] == resultHome[yesterday]['date'] and item['province'] != '' and item['city'] == ''):
            list2.append(item)
        elif(item['date'] == resultHome[be_yesterday]['date'] and item['province'] != '' and item['city'] == ''):
            list3.append(item)
    table = []
    mapInfo = []
    for item in list:
        temp_children = {}
        temp_map = {}
        temp_children['name'] = item['province']
        temp_map['name'] =item['province']
        yesterdayItem = {}
        beYesterdayItem = {}
        for item2 in list2:
            if(item2['province'] == item['province']):
                yesterdayItem = item2
                break
        for item3 in list3:
            if(item3['province'] == item['province']):
                beYesterdayItem = item3
                break

        temp_children['add'] = yesterdayItem['confirmed'] - beYesterdayItem['confirmed']
        temp_children['confirm'] = item['confirmed']
        temp_children['dead'] = item['dead']
        temp_children['heal'] = item['cured']
        temp_map['value'] = item['confirmed'] - item['dead'] - item['cured']
        table.append(temp_children)
        mapInfo.append(temp_map)
    index_info['table'] = table
    index_info['mapInfo'] = mapInfo
    outHome = 'resultHome.json'
    with open(outHome, 'w', encoding='utf-8') as f:
        json.dump(index_info, f, ensure_ascii=False)
    f.close()

    #处理view中的数据，对每个省分别处理
    for indexName, name in enumerate(NAME):
        dataName = []
        result = {}
        for item in resultView:
            if(item['province'] == name):
                dataName.append(item)
        today = 0
        yesterday = 0
        be_yesterday = 0
        times = 2
        for index in range(len(dataName) - 1, -1, -1):
            if (dataName[index]['city'] == '' and times == 0):
                be_yesterday = index
                break
            if (dataName[index]['city'] == '' and times == 1):
                yesterday = index
                times = 0
            if (dataName[index]['city'] == '' and times == 2):
                today = index
                times = 1
        result['updateTime'] = dataName[today]['date']
        total = {}
        total['addNum'] = dataName[yesterday]['confirmed'] - dataName[be_yesterday]['confirmed']
        total['confirm'] = dataName[today]['confirmed']
        total['suspect'] = dataName[today]['suspected']
        total['dead'] = dataName[today]['dead']
        total['heal'] = dataName[today]['cured']
        result['total'] = total
        province_info = {}
        provinceDate = []
        provinceConfirm = []
        provinceSuspect = []
        provinceDead = []
        provinceHeal = []
        list1 = []
        list2 = []
        list3 = []
        for item in dataName:
            if(item['city'] == ''):
                provinceDate.append(item['date'])
                provinceConfirm.append(item['confirmed'])
                provinceSuspect.append(item['suspected'])
                provinceHeal.append(item['cured'])
                provinceDead.append(item['dead'])
            if (item['date'] == dataName[today]['date'] and item['city'] != ''):
                list1.append(item)
            elif (item['date'] == dataName[yesterday]['date'] and item['city'] != ''):
                list2.append(item)
            elif (item['date'] == dataName[be_yesterday]['date']  and item['city'] != ''):
                list3.append(item)
        province_info['provinceDate'] = provinceDate
        province_info['provinceConfirm'] = provinceConfirm
        province_info['provinceSuspect'] = provinceSuspect
        province_info['provinceHeal'] = provinceHeal
        province_info['provinceDead'] = provinceDead
        table = []
        mapInfo = []
        for item in list1:
            temp = {}
            tempMap = {}
            temp['name'] = item['city']
            tempMap['name'] = item['city']
            yesterdayItem = {}
            beYesterdayItem = {}
            for item2 in list2:
                if(item2['city'] == item['city']):
                    yesterdayItem = item2
                    break
            for item3 in list3:
                if(item3['city'] == item['city']):
                    beYesterdayItem = item3
                    break
            if(yesterdayItem == {}):
                temp['add'] = 0
            elif(beYesterdayItem == {}):
                temp['add'] = yesterdayItem['confirmed']
            else:
                temp['add'] = yesterdayItem['confirmed'] - beYesterdayItem['confirmed']
            temp['confirm'] = item['confirmed']
            temp['dead'] = item['dead']
            temp['heal'] = item['cured']
            tempMap['value'] = item['confirmed'] - item['dead'] - item['cured']
            mapInfo.append(tempMap)
            if(len(temp['name']) < 4):
                table.append(temp)
        result['table'] = table
        result['mapInfo'] = mapInfo

        province_add_info = {}
        provinceAddConfirm = []
        provinceAddSuspect = []
        provinceAddDead = []
        provinceAddHeal = []
        for i in range(1, len(provinceDate)):
            provinceAddConfirm.append(provinceConfirm[i] - provinceConfirm[i - 1])
            provinceAddSuspect.append(provinceSuspect[i] - provinceSuspect[i - 1])
            provinceAddHeal.append(provinceHeal[i] - provinceHeal[i - 1])
            provinceAddDead.append(provinceDead[i] - provinceDead[i - 1])
        provinceDate = provinceDate[1:]
        province_add_info['provinceDate'] = provinceDate
        province_add_info['provinceAddConfirm'] = provinceAddConfirm
        province_add_info['provinceAddSuspect'] = provinceAddSuspect
        province_add_info['provinceAddHeal'] = provinceAddHeal
        province_add_info['provinceAddDead'] = provinceAddDead
        result['province_add_info'] = province_add_info
        outFile = ''
        if(name == '陕西'):
            outFile = 'province\\shanxi1.json'
        else:
            outFile = 'province\\' + PINYIN[indexName] + '.json'
        with open(outFile, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False)
        f.close()

    #处理曲线图数据
    resultTrend = {}
    #全国数据
    date = []#数据的日期
    dataConfirm = []#每天累计的确诊病例
    dataSuspect = []#每天累计的疑似病例
    dataDead = []#每天累计的死亡病例
    dataHeal = []#每天累计的死亡病例
    todayConfirm = []#每天现存的确诊病例
    todaySuspect = []#每天现存的疑似病例
    addConfirm = []#每天新增的确诊病例
    addSuspect = []#每天新增的疑似病例
    addDead = []#每天新增的死亡病例
    addHeal = []#每天新增的死亡病例
    #湖北与全国对比数据
    #hubeiAllConfirm = []#全国每日累计确诊病例
    hubeiAddConfirm = []#湖北每日新增确诊病例
    #hubeiAllDead = []#湖北每日累计死亡病例
    #hubeiAllHeal = []#湖北每日累计治愈病例
    #hubeiDate = []
    hubei = []
    notHubei = []
    hubeiDead = []
    notHubeiDead = []
    hubeiHeal = []
    notHubeiHeal = []
    #addHubeiDate = []
    addHubei = []
    addNotHubei = []
    for item in resultHubei:
        if(item['provinceCode'] == ''):
            date.append(item['date'])
            dataConfirm.append(item['confirmed'])
            dataSuspect.append(item['suspected'])
            dataDead.append(item['dead'])
            dataHeal.append(item['cured'])
            todayConfirm.append(item['confirmed'] - item['dead'] - item['cured'])
            todaySuspect.append(item['suspected'])
        if(item['provinceCode'] == '420000' and item['city'] == ''):
            #hubeiDate.append(item['date'])
            hubei.append(item['confirmed'])
            hubeiDead.append(item['dead'])
            hubeiHeal.append(item['cured'])
    for i in range(1, len(date)):
        addConfirm.append(dataConfirm[i] - dataConfirm[i - 1])
        addSuspect.append(dataSuspect[i] - dataSuspect[i - 1])
        addDead.append(dataDead[i] - dataDead[i - 1])
        addHeal.append(dataHeal[i] - dataHeal[i - 1])
    for i in range(0, len(date)):
        notHubei.append(dataConfirm[i] - hubei[i])
        notHubeiDead.append(dataDead[i] - hubeiDead[i])
        notHubeiHeal.append(dataHeal[i] - hubeiHeal[i])
        #hubeiAllConfirm.append(dataConfirm[i])
        #hubeiAllDead.append(dataDead[i])
        #hubeiAllHeal.append(dataHeal[i])
        if (i > 0):
            hubeiAddConfirm.append(addConfirm[i-1])
            #addHubeiDate.append(date[i])
            addHubei.append(hubei[i] - hubei[i - 1])
            addNotHubei.append(notHubei[i] - notHubei[i - 1])
    chinaOption = {}
    chinaOption['date'] = date
    chinaOption['confirm'] = dataConfirm
    chinaOption['dead'] = dataDead
    chinaOption['heal'] = dataHeal
    resultTrend['chinaOption']= chinaOption
    todayOption = {}
    todayOption['date'] = date
    todayOption['confirm'] = todayConfirm
    todayOption['suspect'] = todaySuspect
    resultTrend['todayOption'] = todayOption
    deadOption = {}
    deadOption['date'] = date
    deadOption['heal'] = dataHeal
    deadOption['dead'] = dataDead
    resultTrend['deadOption'] = deadOption
    chinaAddOption = {}
    chinaAddOption['date'] = date[1:]
    chinaAddOption['confirm'] = addConfirm
    chinaAddOption['suspect'] = addSuspect
    chinaAddOption['dead'] = addDead
    chinaAddOption['heal'] = addHeal
    resultTrend['chinaAddOption'] = chinaAddOption
    hubeiOption = {}
    hubeiOption['date'] = date
    hubeiOption['allConfirm'] = dataConfirm
    hubeiOption['hubeiConfirm'] = hubei
    hubeiOption['notHubeiConfirm'] = notHubei
    resultTrend['hubeiConfirmOption'] = hubeiOption
    hubeiAddConfirmOption = {}#addHubeiOption
    hubeiAddConfirmOption['date'] = date[1:]
    hubeiAddConfirmOption['allConfirm'] = hubeiAddConfirm
    hubeiAddConfirmOption['hubeiConfirm'] = addHubei
    hubeiAddConfirmOption['notHubeiConfirm'] = addNotHubei
    resultTrend['hubeiAddConfirmOption'] = hubeiAddConfirmOption
    hubeiDeadOption = {}
    hubeiDeadOption['date'] = date
    hubeiDeadOption['allDead'] = dataDead
    hubeiDeadOption['hubeiDead'] = hubeiDead
    hubeiDeadOption['notHubeiDead'] = notHubeiDead
    resultTrend['hubeiDeadOption'] = hubeiDeadOption
    hubeiHealOption = {}
    hubeiHealOption['date'] = date
    hubeiHealOption['allHeal'] = dataHeal
    hubeiHealOption['hubeiHeal'] = hubeiHeal
    hubeiHealOption['notHubeiHeal'] = notHubeiHeal
    resultTrend['hubeiHealOption'] = hubeiHealOption
    hubeiHome = 'resultHubei.json'
    with open(hubeiHome, 'w', encoding='utf-8') as f:
        json.dump(resultTrend, f, ensure_ascii=False)
    f.close()



if __name__ == '__main__':
    getJson()



