import inspect
import json
import zlib
import time
import asyncio
import threading
import concurrent.futures
import functools

from channels.exceptions import StopConsumer

from ..evaluation import ClaimBundleEvaluation
from channels.generic.websocket import WebsocketConsumer, AsyncConsumer


import traceback


class ClaimConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        self.bundle_query = {}
        self.pool_executor = concurrent.futures.ProcessPoolExecutor(max_workers=10)
        await self.send({
            "type": "websocket.accept",
        })

    async def websocket_receive(self, event):
        index = self._assign_event_index(event)
        await self._bundle_evaluation(event, index)

    def _get_content(self, event):
        bytes_data = event.get('bytes', None)
        if bytes_data:
            bytes_data = zlib.decompress(bytes_data)
            bundle = json.loads(bytes_data.decode("utf-8"))
            return bundle

    def _assign_event_index(self, event):
        event_index = len(self.bundle_query.keys())
        self.bundle_query[event_index] = event
        return event_index

    async def _bundle_evaluation(self, event, event_index):
        content = self._get_content(event)
        await self._send_acceptance(event_index)
        await self._send_evaluation(content, event_index)


    async def _send_acceptance(self, event_index):
        accept_response = { 'type': 'claim.bundle.acceptance', 'content': 'Accepted', 'index': event_index}
        await self.send({
            'text': json.dumps(accept_response),
            'type': 'websocket.send'
        })

    async def _send_evaluation(self, bundle, event_index):
        evaluation_result = ClaimBundleEvaluation.evaluate_bundle(bundle)
        evaluation_response = {'type': 'claim.bundle.payload', 'content': evaluation_result, 'index': event_index}
        await self.send({
            'type': 'websocket.send',
            'text': json.dumps(evaluation_response)
        })
