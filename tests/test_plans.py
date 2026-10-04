from dataclasses import replace
from datetime import datetime, timezone
from http.server import HTTPServer
from pathlib import Path
from threading import Thread
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json
import re
import sqlite3
import tempfile
import unittest

from aioncrafter.codec import ValidationError, dumps
from aioncrafter.plans import PlanStore, SavedPlan, catalog_digest, decode_plan, encode_plan
from aioncrafter.web import form_observations, handler
from tests.helpers import catalog


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.c = catalog()
        self.form = dict(workflow='materials',market='test-server',market_kind='server',
                         faction_mode='not_applicable',faction='',currency='TEST',precision='2',
                         observed='2026-10-01T10:00:00Z',q0='3',p0='12.30',owned0='2')
        self.plan = SavedPlan(1, 'SYNTHETIC plan', True, self.c.release_id, catalog_digest(self.c),
                              tuple(sorted(self.form.items())), form_observations(self.c,self.form),
                              datetime.now(timezone.utc).isoformat())
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = str(Path(self.temp.name)/'plans.sqlite3')

    def test_json_csv_roundtrip_preserves_observation_and_inventory(self):
        for format in ('json','csv'):
            self.assertEqual(decode_plan(encode_plan(self.plan,format),self.c,format),self.plan)
        dangerous = replace(self.plan, name='=HYPERLINK("example")')
        payload = encode_plan(dangerous,'csv')
        self.assertEqual(decode_plan(payload,self.c,'csv'),dangerous)
        import csv,io
        self.assertTrue(all(row[2].startswith("'") for row in list(csv.reader(io.StringIO(payload.decode())))[1:]))

    def test_invalid_import_cannot_rewrite_saved_plan(self):
        with PlanStore(self.path) as store:
            store.save(self.plan,self.c)
            bad = json.loads(dumps(self.plan));bad['fields'].append(['unknown','value'])
            for payload in (b'{}', b'[]', json.dumps(bad).encode(), b'x'*262145):
                with self.assertRaises(ValidationError):
                    decode_plan(payload,self.c)
            self.assertEqual(store.load(self.plan.name,self.c),(1,self.plan))
        with self.assertRaisesRegex(ValidationError,'PLAN_CATALOG'):
            decode_plan(encode_plan(self.plan),replace(self.c,release_id='other'))

    def test_reopen_revisions_conflicts_and_explicit_deletion(self):
        with PlanStore(self.path) as store:
            self.assertEqual(store.save(self.plan,self.c),1)
        with PlanStore(self.path) as store:
            self.assertEqual(store.load(self.plan.name,self.c),(1,self.plan))
            newer = replace(self.plan,favorite=False)
            self.assertEqual(store.save(newer,self.c,1),2)
            with self.assertRaisesRegex(ValidationError,'CONCURRENT_CHANGE'):
                store.save(self.plan,self.c,1)
            self.assertEqual(store.load(self.plan.name,self.c),(2,newer))
            with self.assertRaises(ValidationError):
                store.delete(self.plan.name,1)
            store.delete(self.plan.name,2)
            self.assertEqual(store.list(),())

    def test_original_ingestion_time_retained_and_edits_link_previous(self):
        original = self.plan.observations
        self.assertEqual(form_observations(self.c,self.form,original),original)
        changed = form_observations(self.c,dict(self.form,p0='15'),original)
        self.assertEqual(changed[0].supersedes_id,original[0].observation_id)
        self.assertEqual(changed[1:],original[1:])
        different_market = form_observations(self.c,dict(self.form,market='other'),original)
        self.assertIsNone(different_market[0].supersedes_id)

    def test_forged_observation_and_empty_or_unknown_fields_rejected(self):
        bad = replace(self.plan,observations=(replace(self.plan.observations[0],unit_price='99'),*self.plan.observations[1:]))
        for plan in (bad,replace(self.plan,fields=()),replace(self.plan,fields=(*self.plan.fields,('action','delete')))):
            with self.assertRaises(ValidationError):
                decode_plan(encode_plan(plan),self.c)

    def test_unrelated_and_newer_databases_refused(self):
        con = sqlite3.connect(self.path)
        con.execute('CREATE TABLE unrelated (id INTEGER)');con.close()
        with self.assertRaisesRegex(ValidationError,'PLAN_DATABASE'):
            PlanStore(self.path)
        future = str(Path(self.temp.name)/'future.sqlite3')
        with PlanStore(future) as store:
            store.connection.execute('PRAGMA user_version=999')
        with self.assertRaisesRegex(ValidationError,'PLAN_VERSION'):
            PlanStore(future)

    def test_http_save_load_export_import_reset_and_csrf(self):
        server=HTTPServer(('127.0.0.1',0),handler(self.c,self.path))
        thread=Thread(target=server.serve_forever,daemon=True);thread.start()
        url=f'http://127.0.0.1:{server.server_port}'
        def post(form):
            with urlopen(Request(url,data=urlencode(form).encode())) as response:
                return response.read().decode()
        try:
            with urlopen(url) as response:
                token=re.search('name="csrf" value="([^"]+)"',response.read().decode()).group(1)
            fields=dict(self.form,action='save',plan_name='web plan',revision='0')
            self.assertIn('CSRF',post(fields))
            fields['csrf']=token
            self.assertIn('Saved locally at revision 1',post(fields))
            action=lambda a: dict(action=a,csrf=token,plan_name='web plan')
            loaded=post(action('load'))
            self.assertIn('Total: 36.90',loaded)
            exported=post(action('export_json'))
            plan=decode_plan(exported.encode(),self.c)
            self.assertEqual(plan.name,'web plan')
            preview=post(dict(action='import',csrf=token,import_data=exported,import_format='json'))
            self.assertIn('Import validated',preview)
            self.assertIn('import_payload',preview)
            imported_fields = dict(self.form,action='save',csrf=token,plan_name='imported copy',revision='0',import_payload=exported)
            self.assertIn('Saved locally at revision 1',post(imported_fields))
            with PlanStore(self.path) as store:
                self.assertEqual(store.load('imported copy',self.c)[1].observations,plan.observations)
            self.assertIn('Unsaved form reset',post(action('reset')))
            with PlanStore(self.path) as store:
                self.assertEqual(len(store.list()),2)
            self.assertIn('CONFIRM_DELETE',post(dict(action('delete'),revision='1')))
            self.assertIn('revisions deleted',post(dict(action('delete'),revision='1',confirm_delete='yes')))
        finally:
            server.shutdown();server.server_close();thread.join()
