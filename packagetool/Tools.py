from settings import settingfile as sets
import pandas as pd


def get_not_ten(standard):
    """四舍五入十位 返回 0.2*标仓 """
    return round(sets.stock_position_number * standard / 100) * 100


def gerenate_candealcode(element, connect, today):
    """生成标准的交易类型"""
    df = callsql_price(connect=connect, date=today, code_str=element[0])
    if 0 != len(df):
        # 获取该股票的标仓
        stander = math_stander(open=df["open"][0])
    else:
        return []
    # 生成列表 [0-code,1-该code的标仓,2-历史仓位]
    return [element[0], stander, 1]


def get_everdaycode(connect, today, code, everdaycode_list):
    """
    在建仓日这一天，生成
    获取每日需要交易的 code_list
    一个code如果建仓之后，在新的信号日再次出现，就把名字转换成 1@2016-02-02
    :return: [['839', 37800, 143000.0],...]
    """
    code_str = code
    # 先判断和之前code 是否相同
    if len(everdaycode_list) != 0:  # 第一天的list为空
        for i in range(len(everdaycode_list)):
            if str(code) == str(everdaycode_list[i][0]):
                code_str = str(code_str) + "@" + str(today)
    # 先判断 返回值是否等于 “sql1”
    df = callsql_price(connect=connect, date=today, code_str=code)
    if 0 != len(df):
        # 获取该股票的标仓
        stander = math_stander(open=df["open"][0])
        # 获取该股票的收盘价
        close = df["close"][len(df["close"]) - 1]
    else:
        return []
    # 生成列表 [0-code,1-该code的标仓,2-建仓的收盘价]
    return [code_str, stander, close]


def math_stander(open):
    """
    根据open,计算出标准仓位
    :param openlist:
    :return:
    """
    frist_open = int(open)
    frist_open = frist_open / 10000
    frist_open = sets.one_code_money / frist_open

    baiwei = int(frist_open)
    if baiwei > 99:
        baiwei = baiwei // 100  # 整除

    gewei = baiwei % 10
    # print("个位是：",gewei)
    if gewei == 1 or gewei == 3 or gewei == 5 or gewei == 7 or gewei == 9:
        baiwei = baiwei - 1
        stander = baiwei * 100
    else:
        stander = baiwei * 100
    return stander


def get_sixcode(code):
    """
    返回一个标准6位的编码 带后缀
    :param code:
    :return:
    """
    code = str(code)
    # 补齐code 并且判断是.SZ  or .SH
    if len(code) == 1 or len(code) == 2 or len(code) == 3 or len(code) == 3 or len(code) == 4 or len(code) == 5:
        code = code.zfill(6)
    if int(code[0]) == 6:
        code = code + ".SH"
    else:
        code = code + ".SZ"
    return code


def get_hist_postion(everdayinfor_dict, yestday, code):
    """
    获得一个code 上一天的历史仓位
    """
    elementlist = everdayinfor_dict[str(yestday)]
    for i in elementlist:
        if str(i[0]) == str(code):
            return i[2]


def if_newcode(connect, all_code, today, stop_dicts):
    """
    判断建仓日的code 是否是一字板、停牌，是就不加入list
    :param newcode_lists:
    :param today:
    :return: list
    """
    del_one_list = []
    # find 一字板
    tmp = []
    for index in range(len(all_code)):
        df = callsql_price(connect, today, all_code[index])
        if len(df) == 0:  # 等于0有多种情况 1.一字板 2.停牌 3.数据库没有这个数据
            tmp.append(all_code[index])
        else:
            if df['open'][0] == df['close'][0] and df['open'][0] == df['high'][0] and df['open'][0] == df['low'][0]:
                tmp.append(all_code[index])

    del_one_list = [x for x in all_code if x not in tmp]
    # find 停牌
    addsuffix_list = add_suffix(del_one_list)
    dicts = stop_dicts
    today_stop_list = dicts[str(today)]
    return [x[0:6] for x in addsuffix_list if x not in today_stop_list]


def money_regulate(history_buy_dicts, yestday):
    """
    求出一只股票可以分的钱
    :param history_buy_dicts:
    :param yestday:
    :return:
    """
    # ｛"2016-1-1":[50,98000],"2016-1-2":[60,8800],...｝
    lists = history_buy_dicts[yestday]
    # 1.先得到份数
    par_number = can_buy_number(lists[0])
    # 2.在得到昨天的可用资金
    # lists[1]
    # 一份的钱
    if par_number != 0:
        one_par_money = lists[1] / par_number
        # 一只股票的钱
        one_code_money = one_par_money / sets.firstday_code
    else:
        one_code_money = 0
    print("今天有多少只:{0},有多少份：{1},一只能分多少钱：{2}".format(lists[0], par_number, one_code_money))
    return one_code_money


def can_buy_number(x):
    """
    算法，根据昨天的购买支数，返回今天可以购买的份数
    :param x:
    :return:
    """
    # x = 199
    print("您输入的值为：{0}".format(x))
    CONSTANT = sets.how_many_part  # 份数
    # print("CONSTANT", CONSTANT)
    SUM = sets.firstday_code * CONSTANT  # 总支数
    # print("SUM", SUM)
    if x == 0:
        print("可以购买的份数{0}".format(sets.how_many_part))
        return sets.how_many_part
    elif x == SUM:
        print("可以购买的份数{0}".format(0))
        return 0
    else:
        x2 = SUM - x
        # 总量 % 还剩能购买的量
        gety = SUM % x2
        # print(gety)
        if gety != 0:
            s = x2 / sets.firstday_code
            print("!=0 可以购买的份数：", int(s))
            return int(s)
        else:
            if SUM - x < sets.firstday_code:
                print("< 可以 购买的份数：{0}".format(0))
                return 0
            else:
                sy = SUM / x
                print("/ 可以 购买的份数：", int(sy))
                return int(sy)


def if_newcode(newcode_lists, today, stop_dicts, create_stop_one_dict, w):
    """
    判断建仓日的code 是否是一字板、停牌，是就不加入list
    :param newcode_lists:
    :param today:
    :return: list
    """
    # 新code 如果是 一字板 和 停牌不加入 list
    # find 一字板
    df = rd.get_code4price(newcode_lists, today, w)
    new_list = []
    one_seven_list = []
    for onecode in newcode_lists:
        count = 0
        for i in range(len(df[onecode])):
            if df[onecode][0] == df[onecode][i]:
                count += 1
        if count != len(df[onecode]):
            new_list.append(onecode)
        else:
            one_seven_list.append("{0}=1".format(onecode))
            # print("在{0}建仓日发现一字板:{1}".format(today, onecode))
    # find 停牌
    addsuffix_list = add_suffix(new_list)
    dicts = stop_dicts
    today_stop_list = dicts[str(today)]

    for j in new_list:
        for k in today_stop_list:
            if str(k) == str(j):
                one_seven_list.append(str("{0}=7".format(j[0:6])))
    create_stop_one_dict[str(today)] = one_seven_list
    return [x[0:6] for x in addsuffix_list if x not in today_stop_list]


def only_code(lists):
    """
    返回每天唯一的code
    :param lists:
    :return: list
    """
    return list({}.fromkeys([x[0:6] for x in lists]).keys())


def get_addcode(code, everdaycode_list, today):
    """
    在建仓日这一天，生成
    获取每日需要交易的 code_list
    一个code如果建仓之后，在新的信号日再次出现，就把名字转换成 1@2016-02-02
    :return: ['839',"840",...]
    """
    code_str = code
    # 先判断和之前code 是否相同
    if len(everdaycode_list) != 0:  # 第一天的list为空
        for i in range(len(everdaycode_list)):
            if str(code) == str(everdaycode_list[i]):
                code_str = str(code_str) + "@" + str(today)
    return code_str


def add_suffix(lists):
    """
    "给code添加后缀"
    :param lists:
    :return: list
    """
    list1 = map(get_sixcode, lists)
    return list(list1)


def del_suffix(lists):
    """
    "给code添加后缀"
    :param lists:
    :return: list
    """
    list1 = map(get_sixcode, lists)
    return list(list1)


def get_sixcode(code):
    """
    返回一个标准6位的编码 带后缀
    :param code:
    :return:
    """
    code = str(code)
    # 补齐code 并且判断是.SZ  or .SH
    if len(code) == 1 or len(code) == 2 or len(code) == 3 or len(code) == 3 or len(code) == 4 or len(code) == 5:
        code = code.zfill(6)
    if int(code[0]) == 6:
        code = code + ".SH"
    else:
        code = code + ".SZ"
    return code


def mergenoeday(everdayinfor_dict, today):
    """
    获取一天内所有code ,list , 然后合并成一个矩阵
    :param everdayinfor_dict:
    :param today:
    :return: df
    """
    oneday_allcode = everdayinfor_dict[today]
    df = pd.DataFrame(oneday_allcode, index=range(0, len(oneday_allcode)),
                      columns=["code", "open", "现仓位", "特殊备注1or7", "开仓用的钱", "开仓剩余钱", "平仓得的钱", "卖出价", "持有or卖出备注:1or0",
                               "最高收盘价", "股票市值"])
    return df
