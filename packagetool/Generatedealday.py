import tushare as ts
import datetime
import xlsxwriter

path = '../outdata/'
lists = []
deal_list = []


def main():
    """
    生成交易日输出 excel
    """
    # 需要手工修改的 开始时间、结束时间
    begin = datetime.date(2015, 1, 6)
    end = datetime.date(2015, 1, 31)

    # get all date
    for i in range((end - begin).days + 1):
        day = begin + datetime.timedelta(days=i)
        lists.append(day)

    # get deal date
    for j in lists:
        a = ts.is_holiday(str(j))
        if a == False:
            deal_list.append(j)

    # out excel date
    workbook = xlsxwriter.Workbook(path + "交易日s.xlsx")
    worksheet = workbook.add_worksheet("Sheet1")
    for k in range(len(deal_list)):
        worksheet.write(0, k, deal_list[k])
    workbook.close()


if __name__ == '__main__':
    main()
