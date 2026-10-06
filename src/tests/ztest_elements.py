# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

from app.global_consts import GlobalConsts


class Sand:

    @staticmethod
    def send_get(tco, url):
        response = tco.test_client.get(url)
        # Assert that the response status code is 200 (OK)
        tco.assertEqual(response.status_code, 200)
        # Decode the response data
        data = response.get_json()
        return data

    @staticmethod
    def send_post(tco, url, body_dictio):
        response = tco.test_client.post(url, json=body_dictio)
        # Assert that the response status code is 200 (OK)
        tco.assertEqual(response.status_code, 200)
        # Decode the response data
        msg_return = response.get_json()
        return msg_return


class Pebble:
    @staticmethod
    def sample_procedure(tco, sample_arg):
        pass

class Rock:

    @staticmethod
    def get_version(capp, tco):
        my_url = 'api/Version'
        data = Sand.send_get(tco, my_url)
        tco.assertDictEqual(data, {'version': GlobalConsts.get('const_my_version')})
        return data

