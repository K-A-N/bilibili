# -*- codeing = utf-8 -*-
# @Time: 2020/4/28上午9:53
# @Author: KAN
# @File: bili.py
# @Software: PyCharm

from bs4 import BeautifulSoup
import selenium.webdriver
from selenium.webdriver import ActionChains
import ssl
import re
import urllib.request
import time
import os

ssl._create_default_https_context = ssl._create_unverified_context

# 图片个数
imgNumber = 0
# 专栏个数
columnNumber = 0
# 总页数
end = 0
end_1 = 0
# 当前页数
nowPager = 1


def getURL(url):
    global end
    global end_1
    # 使用webdriver模拟浏览器加载js
    d = selenium.webdriver.Chrome()
    # 打开网页
    d.get(url)
    # 获取当前打开页面的源码
    html = [d.page_source]
    try:
        # 获取页数
        end = int("".join(re.compile('title="最后一页:\d*').findall(str(html[0])))[12:])
    except ValueError:
        end = 1;
        end_1 = 1;
    try:
        # 获取下一页按钮元素
        nextPager = d.find_element_by_class_name("be-pager-next")
    except (selenium.common.exceptions.NoSuchElementException):
        d.close()
        print("输入的ID可能有误")
        return -1
    for i in range(end - 1):
        # 模拟点击下一页
        ActionChains(d).move_to_element(nextPager).click(nextPager).perform()
        # 延迟是为了js加载完毕
        time.sleep(0.5)
        # 获取下一页的源码
        html.append(d.page_source)
    d.close()
    return html


def getData(html):
    global imgNumber, columnNumber, nowPager, end_1, end
    imgList = []
    # 处理每一页的源码
    for htmlPager in html:
        bs = BeautifulSoup(htmlPager, "html.parser")
        # if else 判断是不是最后一页，最后一页与其他页面结构不同
        if nowPager == end & end_1 == 0:
            li = bs.select(".main-content")
        else:
            li = bs.select(".content")
        # 获取文章超链接
        findLink = re.compile(r'<a href="(.*?)"', re.S)
        link = findLink.findall(str(li))
        linkCopy = []
        img = []
        # 去重
        for i in range(len(link)):
            if i % 2 != 0:
                linkCopy.append(link[i])
        for i in range(len(linkCopy)):
            s = "https:" + linkCopy[i]
            # 打开文章超链接
            res = urllib.request.urlopen(s)
            div = res.read().decode("utf-8")
            # 查找图片所在区域
            bs2 = BeautifulSoup(div, "html.parser").find_all(class_="article-holder")
            # 获取图片超链接
            img.append(re.compile(r'data-src="(.*?)"', re.S).findall(str(bs2)))
            # 专栏计数器加一
            columnNumber += 1
        # 获取过来的图片超链接没有"https:"，需要拼接
        for i in range(len(img)):
            for j in range(len(img[i])):
                img[i][j] = "https:" + img[i][j]
                imgNumber += 1
        # 此列表添加的是每页的图片
        imgList.append(img)
        # 当前页数
        nowPager += 1
    return imgList


# 下载文件
def downloadDatalist(datalist):
    counter = 1;
    for i in datalist:
        for j in i:
            for a in j:
                # 文件后缀
                fileType = a[len(a) - 4:]
                # 打开图片
                try:
                    res = urllib.request.urlopen(a)
                except urllib.error.URLError:
                    continue;
                try:
                    os.mkdir("bb")
                except FileExistsError:
                    pass
                # 文件路径
                path = "./bb/" + str(counter) + fileType
                # 新建文件
                f = open(path, "wb")
                # 写入文件
                f.write(res.read())
                f.close()
                print("第%d张完成" % counter)
                counter += 1


def main():
    # https://space.bilibili.com/228149311
    # https://space.bilibili.com/30924338
    # https://space.bilibili.com/7892952
    global imgNumber, columnNumber
    # 爬取地址
    baseurl = "https://space.bilibili.com/" + input("输入账号ID：") + "/article"
    # getURL获取需要爬取的源码
    html = getURL(baseurl)
    if html == -1:
        print("end")
        return
    # getData处理爬取后的数据
    datalist = getData(html)
    for i in datalist:
        print(i)
    print("一共获取了%d页，%d个专栏，%d张图片" % (end, columnNumber, imgNumber))
    inp = input("是否下载？Y/N  ")
    if inp in "Y" or inp in "y":
        # 下载
        downloadDatalist(datalist)
    elif inp in "N" or inp in "n":
        print("end")
        return
    print("end")


if __name__ == '__main__':
    main()
