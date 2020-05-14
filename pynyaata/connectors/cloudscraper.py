import re
from collections import OrderedDict
from urllib.parse import urlparse

from cloudscraper import CloudScraper, CloudflareIUAMError, JavaScriptInterpreter


class CloudScraperWrapper(CloudScraper):

    def IUAM_Challenge_Response(self, body, url, interpreter):
        try:
            formPayload = re.search(
                r'<form (?P<form>.*?="challenge-form" '
                r'action="(?P<challengeUUID>.*?'
                r'__cf_chl_jschl_tk__=\S+)"(.*?)</form>)',
                body,
                re.M | re.DOTALL
            ).groupdict()

            if not all(key in formPayload for key in ['form', 'challengeUUID']):
                self.simpleException(
                    CloudflareIUAMError,
                    "Cloudflare IUAM detected, unfortunately we can't extract the parameters correctly."
                )

            payload = OrderedDict()
            for challengeParam in re.findall(r'<input\s(.*?)>', formPayload['form']):
                inputPayload = dict(re.findall(r'(\S+)="(\S+)"', challengeParam))

                if inputPayload.get('name') in ['r', 'jschl_vc', 'pass']:
                    if inputPayload.get('name') != "jschl_vc":

                        payload.update({inputPayload['name']: inputPayload['value']})
                    elif inputPayload.get('name') == "jschl_vc" and "jschl_vc" not in payload:
                        payload.update({inputPayload['name']: inputPayload['value']})

        except AttributeError:
            self.simpleException(
                CloudflareIUAMError,
                "Cloudflare IUAM detected, unfortunately we can't extract the parameters correctly."
            )

        hostParsed = urlparse(url)

        try:
            payload['jschl_answer'] = JavaScriptInterpreter.dynamicImport(
                interpreter
            ).solveChallenge(body, hostParsed.netloc)
        except Exception as e:
            self.simpleException(
                CloudflareIUAMError,
                'Unable to parse Cloudflare anti-bots page: {}'.format(
                    getattr(e, 'message', e)
                )
            )

        return {
            'url': '{}://{}{}'.format(
                hostParsed.scheme,
                hostParsed.netloc,
                self.unescape(formPayload['challengeUUID'])
            ),
            'data': payload
        }
