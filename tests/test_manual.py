from dataclasses import replace
from datetime import datetime, timezone
from http.server import HTTPServer
from threading import Thread
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import unittest
from aioncrafter.codec import ValidationError
from aioncrafter.manual import manual_observation, resolve_list
from aioncrafter.web import render, handler
from tests.helpers import catalog, market


class ManualTests(unittest.TestCase):
    def setUp(self):
        self.c = catalog()
        self.form = dict(workflow='materials', market='test-server', market_kind='server',
                         faction_mode='not_applicable', faction='', currency='TEST', precision='2',
                         observed='2026-10-01T10:00:00Z', q0='3', p0='12.30')

    def test_manual_observation_requires_time_preserves_missing_and_source(self):
        obs = manual_observation(self.c.items[0].identity, market(), '', self.form['observed'], self.c.provenance)
        self.assertIsNone(obs.unit_price)
        self.assertEqual(obs.observed_at, self.form['observed'])
        self.assertEqual(obs.provenance, self.c.provenance)
        for time in ('', '2026-10-01', '9999-01-01T00:00:00Z'):
            with self.assertRaises(ValidationError):
                manual_observation(self.c.items[0].identity, market(), '1', time, self.c.provenance)

    def test_pasted_ambiguous_alias_returns_candidates(self):
        rows = resolve_list(self.c, '2\tSynthetic potion')
        self.assertGreater(len(rows[0][1]), 1)
        for text in ('-1\tSynthetic ore', '2 Synthetic ore', '1\tunknown', ''):
            with self.assertRaises(ValidationError):
                resolve_list(self.c, text)

    def test_materials_form_needs_no_sale_fields(self):
        html = render(self.c, self.form)
        self.assertIn('Total: 36.90', html)
        self.assertIn('Manual references', html)
        self.assertNotIn('role="alert"', html)
        self.assertIn('Total: Incomplete', render(self.c, dict(self.form, p0='')))

    def test_item_form_batch_and_margin_and_unknown_probability(self):
        form = dict(self.form, workflow='item', recipe='synthetic-bar', product='2', target='3',
                    p0='10', p1='2', selling='30', tax='0.1', sale_fee='0', rounding='floor',
                    fee_source='SYNTHETIC assumption', craft_fee='1', craft_basis='per_batch')
        html = render(self.c, form)
        self.assertIn('2 crafts · 4 produced · 3 planned sales · 1 unsold leftovers', html)
        self.assertIn('Estimated profit/loss:', html)
        self.assertNotIn('role="alert"', html)
        self.assertIn('NONDETERMINISTIC', render(self.c, dict(form, recipe='synthetic-potion', product='4')))

    def test_ambiguity_picker_and_html_escaping(self):
        form = dict(self.form, paste='2\tSynthetic potion', market='<script>', p3='12.30')
        html = render(self.c, form)
        self.assertIn('Choose variant', html)
        self.assertNotIn('<script>', html)
        self.assertIn('Total: 24.60', render(self.c, dict(form, pick0='3')))

    def test_http_get_post_and_size_origin_limits(self):
        server = HTTPServer(('127.0.0.1', 0), handler(self.c))
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f'http://127.0.0.1:{server.server_port}'
            with urlopen(url) as response:
                self.assertIn(b'SYNTHETIC', response.read())
                self.assertIn("frame-ancestors 'none'", response.headers['Content-Security-Policy'])
            with urlopen(Request(url, data=urlencode(self.form).encode())) as response:
                self.assertIn(b'Total: 36.90', response.read())
            from urllib.error import HTTPError
            with self.assertRaises(HTTPError) as error:
                urlopen(Request(url, data=b'x', headers={'Origin':'http://other'}))
            self.assertEqual(error.exception.code, 403)
            error.exception.close()
            with self.assertRaises(HTTPError) as error:
                urlopen(Request(url, data=b'x'*65537))
            self.assertEqual(error.exception.code, 413)
            error.exception.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
