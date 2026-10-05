"""Local HTTP/input and storage-failure regressions; no browser or live game QA."""
from http.server import HTTPServer
from pathlib import Path
import socket
import sqlite3
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from aioncrafter.web import handler
from tests.helpers import catalog
from tests.http_form import FormControls


class SecurityRecoveryTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / 'plans.sqlite3'
        Handler = handler(catalog(), str(self.path))
        Handler.log_message = lambda *_: None
        Handler.request_timeout = 0.2
        self.server = HTTPServer(('127.0.0.1', 0), Handler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)
        self.url = f'http://127.0.0.1:{self.server.server_port}'
        with urlopen(self.url) as response:
            self.form = FormControls(response.read().decode()).fields
        self.form.update(market='test-server', currency='TEST', observed='2026-10-01T10:00:00Z', q0='3', p0='12.30')

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def post(self, fields, route=''):
        with urlopen(Request(self.url + route, data=urlencode(fields).encode()), timeout=3) as response:
            return response.read().decode()

    def test_corrupt_plan_store_preserves_calculation_and_inputs_without_false_success(self):
        self.path.write_bytes(b'broken SQLite')
        with urlopen(self.url) as response:
            self.assertIn('STORAGE_UNAVAILABLE', response.read().decode())
        html = self.post(self.form)
        self.assertIn('Total: 36.90', html)
        self.assertIn('STORAGE_UNAVAILABLE', html)
        self.assertEqual(FormControls(html).fields['p0'], '12.30')
        html = self.post(dict(self.form, action='save', plan_name='SYNTHETIC fail'))
        self.assertNotIn('Saved locally at revision', html)
        self.assertIn('STORAGE_UNAVAILABLE', html)
        self.assertEqual(self.path.read_bytes(), b'broken SQLite')

    def test_write_failure_retains_unsaved_plan_and_avoids_leaking_storage_details(self):
        with patch('aioncrafter.plans.PlanStore.save', side_effect=sqlite3.OperationalError('private/path/disk full')):
            html = self.post(dict(self.form, action='save', plan_name='SYNTHETIC disk full'))
        self.assertIn('STORAGE_UNAVAILABLE', html)
        self.assertIn('Total: 36.90', html)
        self.assertNotIn('private/path', html)
        self.assertNotIn('Saved locally at revision', html)

    def test_corrupt_ledger_and_save_failure_preserve_valid_preview(self):
        with urlopen(self.url + '/ledger') as response:
            form = FormControls(response.read().decode()).fields
        form.update(action='preview_record', journal_name='SYNTHETIC outage', market='test-server',
                    currency='TEST', occurred='2026-10-05T10:00:00Z', record_ref='SYNTHETIC receipt',
                    record_item='0', record_quantity='3', paid_total='12.30')
        preview = self.post(form, '/ledger')
        fields = FormControls(preview).fields
        original = fields['journal_payload']
        self.assertTrue(original)
        Path(str(self.path) + '.ledger.sqlite3').write_bytes(b'broken ledger')
        html = self.post(dict(fields, action='save'), '/ledger')
        self.assertIn('STORAGE_UNAVAILABLE', html)
        self.assertNotIn('Journal saved locally', html)
        self.assertEqual(FormControls(html).fields['journal_payload'], original)

    def test_non_ascii_csrf_is_rejected_for_both_stores_without_disconnect(self):
        for route, fields in (('', dict(self.form, action='save', plan_name='SYNTHETIC invalid token')),
                              ('/ledger', dict(action='load', journal_name='SYNTHETIC invalid token'))):
            html = self.post(dict(fields, csrf='é'), route)
            self.assertIn('CSRF', html)
            self.assertNotIn('Saved locally at revision', html)

    def test_malformed_utf8_and_duplicate_fields_are_rejected(self):
        for payload in (b'action=calculate&market=%FF', b'action=save&action=delete'):
            with urlopen(Request(self.url, data=payload)) as response:
                html = response.read().decode()
            self.assertNotIn('Saved locally at revision', html)
            self.assertTrue('DUPLICATE_FIELD' in html or 'invalid start byte' in html)

    def test_body_timeout_frees_server_for_the_next_request(self):
        with socket.create_connection(self.server.server_address, timeout=3) as connection:
            request = f'POST / HTTP/1.0\r\nHost: 127.0.0.1:{self.server.server_port}\r\nContent-Length: 20\r\n\r\nx'
            connection.sendall(request.encode())
            self.assertIn(b'408', connection.recv(4096))
        with urlopen(self.url, timeout=3) as response:
            self.assertEqual(response.status, 200)

    def test_malformed_request_path_returns_bad_request(self):
        with socket.create_connection(self.server.server_address, timeout=3) as connection:
            connection.sendall(f'GET http://[ HTTP/1.0\r\nHost: 127.0.0.1:{self.server.server_port}\r\n\r\n'.encode())
            self.assertIn(b'400', connection.recv(4096))

    def test_host_origin_guards_and_response_privacy_headers(self):
        for headers, payload in (({'Host': 'foreign.example'}, None),
                                 ({'Origin': 'https://foreign.example'}, urlencode(self.form).encode())):
            with self.assertRaises(HTTPError) as error:
                urlopen(Request(self.url, data=payload, headers=headers))
            self.assertEqual(error.exception.code, 403)
            error.exception.close()
        with urlopen(self.url) as response:
            self.assertEqual(response.headers['Cache-Control'], 'no-store')
            self.assertEqual(response.headers['X-Content-Type-Options'], 'nosniff')
            self.assertEqual(response.headers['Referrer-Policy'], 'no-referrer')
            self.assertIn("frame-ancestors 'none'", response.headers['Content-Security-Policy'])
