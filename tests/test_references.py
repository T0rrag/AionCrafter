from dataclasses import replace
from datetime import datetime, timezone
from html import unescape
from http.server import HTTPServer
from threading import Thread
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import re
import tempfile
import unittest
from aioncrafter.codec import ValidationError, dumps
from aioncrafter.models import PriceType
from aioncrafter.references import import_references, reference_label
from aioncrafter.plans import SavedPlan, PlanStore, catalog_digest, encode_plan, decode_plan
from aioncrafter.web import form_observations, handler, render
from tests.helpers import catalog, market, observation


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.c = catalog()
        self.form = dict(workflow='materials',market='test-server',market_kind='server',
                         faction_mode='not_applicable',currency='TEST',precision='2',
                         observed='2026-10-01T10:00:00Z',q0='3',p0='12.30')
        self.obs = replace(observation(),price_type=PriceType.SNAPSHOT,
                           observed_at='2026-10-01T10:00:00Z')

    def test_types_scope_duplicates_and_unknown_rights(self):
        for kind in (PriceType.MANUAL,PriceType.VENDOR_PURCHASE,PriceType.SNAPSHOT):
            obs = replace(self.obs,price_type=kind)
            self.assertEqual(import_references(dumps((obs,)),self.c,market()),(obs,))
        for payload in (dumps((self.obs,self.obs)),dumps((replace(self.obs,price_type=PriceType.VENDOR_SELL_BACK),)),
                        dumps((replace(self.obs,identity=replace(self.obs.identity,market=replace(market(),market_id='other'))),)),
                        '[]','{}','x'*262145):
            with self.assertRaises(ValidationError):
                import_references(payload,self.c,market())
        from aioncrafter.identity import DatasetKind
        from aioncrafter.models import RightsStatus
        # Real rights cannot be smuggled into the synthetic catalog.
        with self.assertRaises(ValidationError):
            import_references(dumps((replace(self.obs,provenance=replace(self.obs.provenance,
                dataset_kind=DatasetKind.GAME,rights_status=RightsStatus.UNVERIFIED)),)),self.c,market())

    def test_age_uses_observation_never_ingestion_and_unknown_stays_unknown(self):
        now=datetime(2026,10,4,10,tzinfo=timezone.utc)
        self.assertIn('age 72h 0m',reference_label(self.obs,now=now))
        self.assertIn('age 72h 0m',reference_label(replace(self.obs,fetched_at='2026-10-04T11:00:00Z'),now=now))
        self.assertIn('age unknown',reference_label(replace(self.obs,observed_at=None),now=now))
        self.assertIn('unavailable',reference_label(replace(self.obs,unit_price=None),now=now))

    def test_future_age_including_subsecond_is_not_reported_as_fresh(self):
        now = datetime(2026, 10, 1, 10, tzinfo=timezone.utc)
        for time in ('2026-10-01T10:00:00.500Z', '2026-10-01T12:00:00Z'):
            obs = replace(self.obs, observed_at=time, fetched_at='2026-10-02T10:00:00Z')
            self.assertIn('future observation — check clock', reference_label(obs, now=now))
        offset = replace(self.obs, observed_at='2026-10-01T12:00:00+02:00')
        self.assertIn('age 0h 0m', reference_label(offset, now=now))

    def test_reference_roundtrip_unknown_time_and_linked_manual_override(self):
        old=form_observations(self.c,self.form)
        for kind in (PriceType.VENDOR_PURCHASE,PriceType.SNAPSHOT):
            obs=replace(self.obs,price_type=kind,observed_at=None)
            observations=(obs,*old[1:])
            form=dict(self.form,t0='')
            plan=SavedPlan(1,'reference',False,self.c.release_id,catalog_digest(self.c),
                           tuple(sorted(form.items())),observations,'2026-10-04T12:00:00Z')
            for format in ('json','csv'):
                self.assertEqual(decode_plan(encode_plan(plan,format),self.c,format),plan)
            self.assertEqual(form_observations(self.c,form,observations),observations)
            # A manual edit with unknown observation time is refused.
            with self.assertRaises(ValidationError):
                form_observations(self.c,dict(form,p0='15'),observations)
            changed=form_observations(self.c,dict(form,p0='15',t0=self.form['observed']),observations)
            self.assertEqual(changed[0].price_type,PriceType.MANUAL)
            self.assertEqual(changed[0].supersedes_id,obs.observation_id)
            self.assertIn('age unknown',render(self.c,form,supplied_observations=observations))

    def test_http_import_calculate_save_reload_retains_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=tmp+'/plans.sqlite3'
            server=HTTPServer(('127.0.0.1',0),handler(self.c,path))
            thread=Thread(target=server.serve_forever,daemon=True);thread.start()
            def post(form):
                with urlopen(Request(f'http://127.0.0.1:{server.server_port}',data=urlencode(form).encode())) as response:
                    return response.read().decode()
            try:
                with urlopen(f'http://127.0.0.1:{server.server_port}') as response:
                    token=re.search('name="csrf" value="([^"]+)"',response.read().decode()).group(1)
                preview=post(dict(self.form,action='references',reference_data=dumps((self.obs,))))
                self.assertIn('Reference import validated',preview)
                payload=unescape(re.search('name="reference_payload" value="([^"]+)"',preview).group(1))
                form=dict(self.form,reference_payload=payload)
                calculated=post(form)
                self.assertIn('Snapshot · age',calculated)
                self.assertIn('Total: 36.90',calculated)
                self.assertIn('Saved locally at revision 1',post(dict(form,action='save',csrf=token,plan_name='reference')))
                loaded=post(dict(action='load',csrf=token,plan_name='reference'))
                self.assertIn('Snapshot · age',loaded)
                with PlanStore(path) as store:
                    self.assertEqual(store.load('reference',self.c)[1].observations[0],self.obs)
            finally:
                server.shutdown();server.server_close();thread.join()

    def test_browser_blank_item_times_use_explicit_default(self):
        form=dict(self.form,**{f't{i}':'' for i in range(len(self.c.items))})
        self.assertNotIn('role="alert"',render(self.c,form))
        self.assertEqual(form_observations(self.c,form)[0].observed_at,self.form['observed'])

    def test_game_references_require_recorded_permission(self):
        from types import SimpleNamespace
        from aioncrafter.identity import DatasetKind
        from aioncrafter.models import RightsStatus
        scope=replace(self.c.scope,dataset_kind=DatasetKind.GAME)
        item=replace(self.c.items[0],identity=replace(self.c.items[0].identity,scope=scope))
        game_market=replace(market(),dataset_kind=DatasetKind.GAME)
        provenance=replace(self.obs.provenance,dataset_kind=DatasetKind.GAME,rights_status=RightsStatus.PERMITTED,
                           rights_ref='test-only permission receipt')
        obs=replace(self.obs,identity=replace(self.obs.identity,item=item.identity,market=game_market),provenance=provenance)
        test_catalog=SimpleNamespace(items=(item,))
        self.assertEqual(import_references(dumps((obs,)),test_catalog,game_market),(obs,))
        with self.assertRaisesRegex(ValidationError,'REFERENCE_RIGHTS'):
            import_references(dumps((replace(obs,provenance=replace(provenance,rights_status=RightsStatus.UNVERIFIED)),)),test_catalog,game_market)
