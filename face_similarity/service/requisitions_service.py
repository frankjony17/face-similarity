import asyncio
import json
import logging
import os
import time
import urllib.request

from aiohttp import ClientSession

from face_similarity.utils.response_error import raise_error


class RequisitionsService:
    """
    Class that guarantees the methods to make simultaneous requisitions using
    event loop in the current OS thread. Coroutines will be wrapped in a
    future and scheduled in the event loop. I create the list of requisitions
    linked to a session that will be executed at the same time.
    """
    response_api = list()
    __header = {'content-type': 'application/json'}

    def start_loop(self, loop, endpoints_list):
        """
        Start task execution. Run until finished. Make multiple requests
        simultaneously.
        Args:
            loop: (event_loop) Event loop in the current OS thread.
            endpoints_list: (list) Endpoint list with those to be required.
        Returns:
            (list) Requisition response list.
        """
        self.response_api = list()
        loop.create_task(self.__fetch(loop, endpoints_list))
        loop.run_forever()
        return self.get_response_values(endpoints_list[0])

    async def __make_requests(self, session, ep):
        """
        Create a new session and perform asynchronous request using a loop
        event.
        Args:
            session: (ClientSession) Interface for making HTTP requests.
            ep: (list) Endpoint and payload to request.
            loop: (event_loop) Event loop in the current OS thread.
        """
        start_time = time.time()
        data = json.dumps(ep[1])
        proxy = self.__get_proxy(ep[0])
        try:
            async with session.post(url=ep[0], data=data, proxy=proxy) as resp:
                if resp.status == 200:
                    self.set_logger(start_time, ep[0], resp.status)
                    response = await resp.json()
                    self.response_api.append([resp.status, response, ep[2]])
                else:
                    self.set_logger(start_time, ep[0], resp.status)
                    self.response_api.append([resp.status, resp])
        except Exception as exception:
            logging.getLogger('face_similarity.api').info(str(exception))
            raise_error(405)

    async def __fetch(self, loop, endpoints):
        """
        Coroutines will be wrapped in a future and scheduled in the event
        loop. I create the list of requisitions linked to a session that will
         be executed at the same time.
        Args:
            loop: (event_loop) Event loop in the current OS thread.
            endpoints: (list) List the endpoint and payload to request.
        """
        async with ClientSession(headers=self.__header, loop=loop) as session:
            tasks = (self.__make_requests(session, ep) for ep in endpoints)
            await asyncio.gather(*tasks, return_exceptions=True)
            loop.stop()

    @staticmethod
    def set_logger(start_time, url, code) -> None:
        """
        Log a message with severity 'INFO'. Print logs of the operation
        performed.
        Args:
            start_time: (time) Initial time of operation.
            url: (str) Endpoint with which the request was made.
            code: Requirement response status code.
        """
        logging.getLogger('face_similarity.requests').info({
            "url": url,
            "time": "%s seconds" % (time.time() - start_time),
            "code": code
        })

    @staticmethod
    def __get_proxy(url):
        """
        Obtain a proxy from the operational system if necessary.
        (in case of using VPN with the bank it is necessary to use the proxy)
        Args:
            url: (str) Endpoint with which the request was made.
        Returns:
            (str) Proxy url.
        """
        http_proxy = None
        try:
            schemes = os.environ['SCHEMES']
            if "127.0.0.1" in url or "0.0.0.0" in url or "localhost" in url:
                http_proxy = None
            else:
                http_proxy = urllib.request.getproxies().get(schemes)
        except KeyError:
            logging.getLogger('face_similarity.api').info(
                'SCHEMES > not found')
            raise_error(428)
        return http_proxy

    def get_response_values(self, endpoints) -> list:
        """
        Verify the response code of the requisition,
        case 200 returns the answer otherwise it aborts.
        Args:
            endpoints: (str) Endpoint with which the request was made.
        Returns:
            (list) List of responses obtained from simultaneous requisitions.
        """
        for response in self.response_api:
            if response[0] == 500:
                raise_error(424)
            elif response[0] > 200:
                raise_error(417, str(response[1].text), endpoints[0])
        return self.response_api

    def __del__(self):
        """"
        Class destroyer.
        """
        del self.response_api
