import socket
import threading
import os
import platform
import ipaddress
import time
import smtplib
import sys
from email.mime.text import MIMEText

from config import *

list_clear = 0


def validate_ip(s):
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True


# Пытается установить соединение с определённым портом.
# Если установила, то при флаге 0 записывает в начальный список портов, иначе в конечный
def scan_port(ip, port, flag):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if client.connect_ex((ip, port)):
        pass
    else:
        print(f"Порт {port} открыт")
        print(port)
        ip_port = str(ip) + ':' + str(port)
        if flag != 0:
            f = open('port1.txt', 'a')
            f.write(ip_port + '\n')
        else:
            f = open('port.txt', 'r')
            ip_list = f.read().split('\n')
            f.close()
            f = open('port.txt', 'a')
            if ip_port not in ip_list:
                f.write(ip_port + '\n')
            f.close()


def clear_list():  # Очищает изначальные списки ip и портов
    ans = 'Yes'
    if ans == 'Yes':
        open('port.txt', 'w').close()
        open('ip.txt', 'w').close()
        open('ip_scan.txt', 'w').close()
        open('ip_scan_one.txt', 'w').close()
        list_clear = 0


def ping(ip, flag):  # Делает пинг к ip, если флаг 0 записывает в начальный, иначе в конечный для позжей проверки
    oc = platform.system()
    if (oc == "Windows"):
        ping_com = "ping -n 1 "
    else:
        ping_com = "ping -c 1 "

    response = os.popen(ping_com + ip)
    data = response.readlines()
    for line in data:
        if 'TTL' in line:
            print(ip, "--> Ping Ok")
            if flag == 0:
                f = open('ip.txt', 'r')
                ip_list = f.read().split('\n')
                f.close()
                f = open('ip.txt', 'a')
                if ip not in ip_list:
                    f.write(str(ip) + '\n')
                f.close()
                f = open('ip1.txt', 'a')
            else:
                f = open('ip2.txt', 'a')
            f.write(str(ip) + '\n')
            f.close()
            break


# Добавляет в список ip 1 адрес. Если порт 0 проверяет все открытые порты, иначе записыает определённый порт
def add_ip(ip, port):
    f = open('ip.txt', 'r')
    ip_list = f.read().split('\n')
    f.close()
    f = open('ip.txt', 'a')
    if ip not in ip_list:
        f.write(str(ip) + '\n')
        f.close()
    f = open('ip_scan_one.txt', 'r')
    ip_list = f.read().split('\n')
    f.close()
    f = open('ip_scan_one.txt', 'a')
    if ip not in ip_list:
        f.write(str(ip) + '\n')
        f.close()
    if port != 0:
        ip_port = str(ip) + ':' + str(port)
        f = open('port.txt', 'r')
        ip_list = f.read().split('\n')
        f.close()
        f = open('port.txt', 'a')
        if ip_port not in ip_list:
            f.write(ip_port + '\n')
        f.close()
    else:
        for i in range(65535):
            potoc = threading.Thread(target=scan_port, args=(ip, i, 0))
            potoc.start()
        potoc.join()


def scan_ip(ip_1, ip_2):  # Вызывает пинг на диапазон адресов, после записи проверяет ответившие ip на порты
    start_ip = ipaddress.IPv4Address(ip_1)
    end_ip = ipaddress.IPv4Address(ip_2)
    open('ip1.txt', 'w').close()
    for ip_int in range(int(start_ip), int(end_ip)):
        ip = str(ipaddress.IPv4Address(ip_int))
        potoc = threading.Thread(target=ping, args=(ip, 0))
        potoc.start()
    potoc.join()
    f = open('ip1.txt', 'r')
    ip_list = f.read().split('\n')
    f.close()
    for ip in ip_list:
        for i in range(65535):
            potoc = threading.Thread(target=scan_port, args=(ip, i, 0))
            potoc.start()
        potoc.join()
    f = open('ip_scan.txt', 'a')
    f.write(str(ipaddress.IPv4Address(start_ip)) + '\n')
    f.write(str(ipaddress.IPv4Address(end_ip)) + '\n')
    f.close()
    open('ip1.txt', 'w').close()


# Сканирует диапазон, если нет найденного ip в изначальном, то выводит новый ip/ После сканирует порты у найденных ip
def scan(ip_1, ip_2):
    start_ip = ipaddress.IPv4Address(ip_1)
    end_ip = ipaddress.IPv4Address(ip_2)

    for ip_int in range(int(start_ip), int(end_ip)):
        ip = str(ipaddress.IPv4Address(ip_int))
        potoc = threading.Thread(target=ping, args=(ip, 1))
        potoc.start()
    potoc.join()
    f = open('ip.txt', 'r')
    ip_start = f.read().split('\n')
    f.close()
    f = open('ip2.txt', 'r')
    ip_new = f.read().split('\n')
    f.close()
    open('ip2.txt', 'w').close()
    for i in ip_new:
        if i not in ip_start:
            print("Незагестрированный ip: " + str(i))
    print(ip_new)

    for ip in ip_new:
        for i in range(65535):
            potoc = threading.Thread(target=scan_port, args=(ip, i, 1))
            potoc.start()
        potoc.join()
        print(ip)
    f = open('port.txt', 'r')
    port = f.read().split('\n')
    f.close()
    f = open('port1.txt', 'r')
    port1 = f.read().split('\n')
    f.close()
    open('port1.txt', 'w').close()

    flag = 0
    a = []
    for i in port1:
        if i not in port:
            flag = 1
            print(i, 'Неизвестный порт')
            a.append(i)

    if flag == 0:
        print('Незарегистрированные порты не обнаружены')
        print(send_email(message=str('Незарегистрированные порты не обнаружены')))
    else:
        print(send_email(message=str("Неизвестный порт(ы):" + str(a))))

def send_email(
        message):  # Модуль отправки почтового сообщения с адресса segrkoh@gmail.com на адресса указанные в файле mail.txt
    recipients = ["Массив с списком адресов почт"]
    f = open('mail.txt', 'r')
    recipients = f.read().split('\n')
    f.close()
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    print(recipients)

    server.login(SENDER, PASSWORD)
    msg = MIMEText(message)
    msg["Subject"] = "ОТЧЁТ ПРОВЕРКИ БЕЗОПАСНОСТИ ПИРИМЕТРА"
    server.sendmail(SENDER, recipients, msg.as_string())

    return "Сообщение отправлено"


def idle():
    f = open('ip_scan.txt', 'r')
    ip_list = f.read().split('\n')
    f.close()
    print(ip_list)
    ip_count = len(ip_list) - 1
    for i in range(0, ip_count, 2):
        if ip_list[i] == '':
            break
        scan(ip_list[i], ip_list[i + 1])
    f = open('ip_scan_one.txt', 'r')
    ip_list = f.read().split('\n')
    f.close()
    print(ip_list)
    for i in ip_list:
        if i != '':
            ip_end = str(ipaddress.IPv4Address(int(ipaddress.IPv4Address(i)) + 1))
            scan(i, ip_end)


timer = threading.Timer(30, idle)
timer.start()
b = time.perf_counter()
print('При простое в течение 30 секунд будет запущено сканирование ранее добавленных ip и диапазонов.', end=" ")
print('До завершения сканирования не получится запустить другие команды')

while (1):
    print('Доступные команды:')
    print('1 - Создание начальных списков ip и портов по диапазону')
    print('2 - Сканирование диапазона на проверку незарегистрированных ip и портов')
    print('3 - Добавление одного ip в список')
    print('4 - Сканирование одиночного ip')
    print('5 - Очистить изначальные списки (полученные на 1 или 3 команде)')
    print('6 - Полное сканирование ранее добавленных ip и диапазонов')
    print('0 - Завершение программы')
    print('Введите число:')

    x = input()
    if time.perf_counter() - b > 30:
        timer.join()
    else:
        timer.cancel()
    if x == '1':
        while (1):
            print('Введите начальный ip диапазона:')
            ip_1 = input()
            if validate_ip(ip_1):
                break
            else:
                print('Неверно указан начальный ip')
        while (1):
            print('Введите конечный ip диапазона (проверяться не будет):')
            ip_2 = input()
            if validate_ip(ip_2):
                break
            else:
                print('Неверно указан конечный ip')
        scan_ip(ip_1, ip_2)
    elif x == '2':
        while (1):
            print('Введите начальный ip диапазона:')
            ip_1 = input()
            if validate_ip(ip_1):
                break
            else:
                print('Неверно указан начальный ip')
        while (1):
            print('Введите конечный ip диапазона (проверяться не будет):')
            ip_2 = input()
            if validate_ip(ip_2):
                break
            else:
                print('Неверно указан конечный ip')
        scan(ip_1, ip_2)
    elif x == '3':
        while (1):
            print('Введите ip:')
            ip = input()
            if validate_ip(ip):
                break
            else:
                print('Неверно указан ip')
        while (1):
            print('Введите порт (Порт = 0, запустит скан всех портов):')
            port = input()
            if port.isdigit() and (int(port) >= 0 and int(port) <= 65535):
                port = int(port)
                break
            else:
                print('Неверно указан порт')
        add_ip(ip, port)
    elif x == '4':
        while (1):
            print('Введите ip:')
            ip = input()
            if validate_ip(ip):
                break
            else:
                print('Неверно указан ip')
        ip_end = str(ipaddress.IPv4Address(int(ipaddress.IPv4Address(ip)) + 1))
        scan(ip, ip_end)
    elif x == '5':
        print('Вы уверены?')
        print('1 - Да')
        print('2 - Нет')
        x = input()
        if x == '1':
            clear_list()
            print('Списки очищены')
    elif x == '6':
        f = open('ip_scan.txt', 'r')
        ip_list = f.read().split('\n')
        f.close()
        print(ip_list)
        ip_count = len(ip_list) - 1
        for i in range(0, ip_count, 2):
            if ip_list[i] == '':
                break
            scan(ip_list[i], ip_list[i + 1])
        f = open('ip_scan_one.txt', 'r')
        ip_list = f.read().split('\n')
        f.close()
        print(ip_list)
        for i in ip_list:
            if i != '':
                ip_end = str(ipaddress.IPv4Address(int(ipaddress.IPv4Address(i)) + 1))
                scan(i, ip_end)
    elif x == '0':
        print('Программа завершенна')
        break
    else:
        print('Такой команды не существует')
