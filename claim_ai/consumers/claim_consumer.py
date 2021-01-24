import json
import logging
import zlib
import concurrent.futures
import traceback

from ..apps import ClaimAiConfig
from ..evaluation import ClaimBundleEvaluation
from channels.generic.websocket import AsyncConsumer

logger = logging.getLogger(__name__)


class ClaimConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        await self.send({"type": "websocket.accept"})
        await self._authenticate_connection()
        self.bundle_query = {}
        self.pool_executor = concurrent.futures.ProcessPoolExecutor(max_workers=10)

    async def websocket_receive(self, event):
        payload = self._get_content(event)
        if payload['type'] == 'claim.bundle.payload':
            index = self._assign_event_index(payload)
            await self._bundle_evaluation(payload['content'], index)
            print(F"Payload with id {index} evaluated")
        elif payload['type'] == 'claim.bundle.acceptance':
            # TODO: confirm evaluation receive and remove it from query
            print("Evaluated payload accepted")
            pass

    def _get_content(self, event):
        bytes_data = event.get('bytes', None)
        if bytes_data:
            try:
                bytes_data = zlib.decompress(bytes_data)
            except Exception as e:
                pass
            bundle = json.loads(bytes_data.decode("utf-8"))
            return bundle

    def _assign_event_index(self, payload):
        if payload.get('bundle_id', None):
            return payload['bundle_id']
        event_index = len(self.bundle_query.keys())
        return event_index

    async def _bundle_evaluation(self, content, event_index):
        await self._send_acceptance(event_index)
        await self._send_evaluation(content, event_index)

    async def _send_acceptance(self, event_index):
        accept_response = {'type': 'claim.bundle.acceptance', 'content': 'Accepted', 'index': event_index}
        await self.send({
            'text': json.dumps(accept_response),
            'type': 'websocket.send'
        })

    async def _send_evaluation(self, bundle, event_index):
        try:
            evaluation_result = ClaimBundleEvaluation.evaluate_bundle(bundle)
            evaluation_response = {'type': 'claim.bundle.payload', 'content': evaluation_result, 'index': event_index}
            await self.send({'type': 'websocket.send', 'text': json.dumps(evaluation_response) })
        except Exception as e:
            logger.error("Exception during claim evaluation: {}".format(traceback.print_exc()))
            evaluation_response = {'type': 'claim.bundle.evaluation_exception', 'content': str(e), 'index': event_index}
            await self.send({'type': 'websocket.send', 'text': json.dumps(evaluation_response) })

    async def _authenticate_connection(self):
        if not ClaimAiConfig.authentication:
            return True
        else:
            _, auth_token = next(
                ((header_name, value) for header_name, value in self.scope['headers']
                 if header_name == b'auth-token'), (None, None)
            )
            if auth_token.decode("utf-8") not in ClaimAiConfig.authentication:
                response_payload = {'type': 'claim.bundle.authentication_exception',
                                    'content': 'Invalid authentication token'}
                await self.send({"type": "websocket.send",
                                 "text": json.dumps(response_payload)
                                 })
                await self.send({"type": "websocket.close", "code": 1007})
                raise ConnectionError("Invalid authentication key")
