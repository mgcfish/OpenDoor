# -*- coding: utf-8 -*-

"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Development Team: Stanislav WEB
"""

import importlib
import random

from urllib3 import ProxyManager
from urllib3.exceptions import DependencyWarning, MaxRetryError

from .providers import RequestProvider
from .exceptions import ProxyRequestError


class Proxy(RequestProvider):
    """Proxy class"""

    __debug = False
    __cfg = False
    __list = None
    __pm = None

    def __init__(self, config, debug=0, **kwargs):
        """
        Proxy instance
        :param src.lib.browser.config.Config config:
        :param int debug: debug flag
        :raise ProxyRequestError
        """

        try:
            self.__tpl = kwargs.get('tpl')
            self.__list = kwargs.get('proxy_list')

            if type(self.__list) is not list or 0 == len(self.__list):
                raise TypeError('Proxy list empty or has invalid format')

        except (TypeError, ValueError) as e:
            raise ProxyRequestError(e.message)

        self.__list = kwargs.get('proxy_list')

        self.__cfg = config
        self.__debug = False if debug < 2 else True

        if True is self.__debug:
            self.__tpl.debug(key='proxy_pool_start')

    def __proxy_pool(self):
        """
        Create Proxy connection pool
        :raise ProxyRequestError
        :return: urllib3.HTTPConnectionPool
        """

        try:

            proxy_server = self.__get_random_proxyserver()

            if self.__get_proxy_type(proxy_server) == 'socks':

                if not self.__pm:

                    module = importlib.import_module('urllib3.contrib.socks')
                    self.__pm = getattr(module, 'SOCKSProxyManager')

                pool = self.__pm(proxy_server, num_pools=self.__cfg.threads, timeout=self.__cfg.timeout, block=True)
            else:
                pool = ProxyManager(proxy_server, num_pools=self.__cfg.threads, timeout=self.__cfg.timeout, block=True)
            return pool
        except (DependencyWarning, ImportError) as e:
            raise ProxyRequestError(e)

    def request(self, url):

        try:
            pool = self.__proxy_pool()
        except MaxRetryError as e:
            print e
            exit()
        except ProxyRequestError as e:
            raise ProxyRequestError(e)

        response = pool.request(self.__cfg.method, url, headers=None, retries=self.__cfg.retries)
        return response

    def __get_random_proxyserver(self):
        """
        Get random server from proxy list
        :return: str
        """

        index = random.randrange(0, len(self.__list))
        server = self.__list[index].strip()

        return server

    def __get_proxy_type(self, server):
        """
        Set proxy type
        :param str server:
        :return: str
        """

        if 'socks' in server:
            return 'socks'
        elif 'https' in server:
            return 'https'
        else:
            return 'http'