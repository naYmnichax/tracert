import os
import re
import argparse
from json import loads
from urllib.error import URLError
from urllib.request import urlopen


reIP = re.compile('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) \n')
GRAY_IP_ADDRESS = ('192.168.', '172.', '10.')


def tracert(domain_name_or_ip: str) -> None:
    """
    Запускает сиситемную утилиту 'tracert'.
    :param domain_name_or_ip: str, IP-адрес или доменное имя.
    :return: None
    """
    os.system(f'tracert -d {domain_name_or_ip} > tracert.txt')


def get_ip_address() -> list:
    """
    Для получения списка IP-адресов из файла,
    в котором записана работа утилиты 'tracert'.
    :return: list, Возвращает список IP-адресов.
    """
    with open('tracert.txt', 'r') as f:
        data = f.read()
        list_with_ip_address = reIP.findall(data)

    return list_with_ip_address


def is_gray_ip(ip: str) -> bool:
    """
    Проверят является ли данный IP-адрес серым.
    :param ip: str, IP-адрес, который хотим проверить.
    :return: bool
    """
    return ip.startswith(GRAY_IP_ADDRESS)


def get_information(ip: str) -> list:
    """
    Получение информации о заданном IP-адресе.
    Получаем следующею информацию об IP-адресе:
    - Автономная система
    - Страна
    - Провайдер
    :param ip: str, IP-адрес, о котором хотим узнать дополнительную информацию.
    :return: list, список содержащий информацию об автономной системе,
    стране и провайдере
    """
    information_sheet = [ip, '***', '***', '***']
    if is_gray_ip(ip):
        return information_sheet
    try:
        with urlopen(f'https://ipinfo.io/{ip}/json') as site:
            data = loads(site.read())

            AS, Provider = data['org'].split(' ', 1)
            information_sheet[1] = AS
            information_sheet[2] = data['country']
            information_sheet[3] = Provider

    except URLError:
        print(f'[!] не удалось получить дополнительную информацию для ip-адреса: {ip}')

    return information_sheet


def get_route(ip_address: list) -> None:
    """
    Выводит в консоль таблицу пути до заданного домена.
    :param ip_address: list, Список IP-адресов, полученных, благодаря утилите 'tracert'
    :return: None
    """
    print(f'|   №   |{" " * 9}IP{" " * 9}|{" " * 5}AS{" " * 6}|{" " * 3}Country{" " * 4}|   Provider')
    count = 0
    for ip in ip_address:
        count += 1
        ip_with_mask, autonomous_system, country, provider = get_information(ip)
        print(f'|   {count}   |{" " * 3}{ip_with_mask}{" " * (17 - len(ip_with_mask))}|'
              f'{" " * 3}{autonomous_system}{" " * (10 - len(autonomous_system))}|'
              f'{" " * 6}{country}{" " * (8 - len(country))}|   {provider}')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('domain_name', type=str, help='enter the domain name or ip-address')

    args = parser.parse_args()

    tracert(args.domain_name)
    get_route(get_ip_address())


if __name__ == '__main__':
    main()
