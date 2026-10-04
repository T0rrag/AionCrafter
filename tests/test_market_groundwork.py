"""SYNTHETIC contract integration only; not real-market reconciliation."""
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
import tempfile
import unittest

from aioncrafter.acquisition import ListingOffer, depth_cost, indicative_cost
from aioncrafter.models import PriceType
from aioncrafter.price_cache import PriceCache
from aioncrafter.price_service import PriceService, ProviderFailure, RequestPolicy
from aioncrafter.references import reference_label
from aioncrafter.storage import Store
from .helpers import catalog
from .synthetic_prices import Clock, SyntheticProvider, sample


class MarketGroundworkTests(unittest.TestCase):
    def test_snapshot_retry_manual_fallback_and_persistence_keep_provenance(self):
        clock = Clock()
        obs = sample(price_type=PriceType.LISTING, available_quantity=3, unit_price='1.00')
        provider = SyntheticProvider((obs,))
        cache = PriceCache(provider, clock=clock, ttl=timedelta(seconds=10), max_source_age=timedelta(minutes=30))
        policy = RequestPolicy(5, 10, timedelta(minutes=1), 2, timedelta(seconds=1),
                               timedelta(seconds=3), timedelta(seconds=20))
        service = PriceService(cache, policy, batched=True)
        first = service.resolve((obs.identity,))[0]
        result = depth_cost(obs.identity, 2, (ListingOffer(first.observations[0], '3.00', False),),
                            provider.capabilities, max_states=100)
        self.assertEqual((first.state, result.total, result.leftovers), ('stale', 300, 1))
        clock.advance(10)
        provider.failures = [ProviderFailure('unavailable', retryable=True)]
        failure = service.resolve((obs.identity,))[0]
        self.assertEqual((failure.state, failure.observations), ('stale_error', (obs,)))
        manual = replace(obs, observation_id='SYNTHETIC-manual-fallback', price_type=PriceType.MANUAL,
                         unit_price='2.00', supersedes_id=obs.observation_id,
                         fetched_at=clock().isoformat(), observed_at=clock().isoformat())
        fallback = service.resolve((obs.identity,), manual={obs.identity: manual})[0]
        estimate = indicative_cost(obs.identity, 2, fallback.observations[0])
        self.assertEqual((fallback.origin, estimate.total, estimate.stock), ('manual', 400, 'unverified'))
        self.assertIn('Manual', reference_label(manual, now=clock()))
        with tempfile.TemporaryDirectory() as directory:
            with Store(str(Path(directory) / 'synthetic.sqlite')) as store:
                c = catalog()
                store.publish(c, expected_active=None)
                for record in (obs, manual):
                    store.save_observation(record, release_id=c.release_id)
                self.assertEqual(store.observation(obs.observation_id), obs)
                self.assertEqual(store.observation(manual.observation_id), manual)
        self.assertEqual(cache.peek(obs.identity).entry.observations, (obs,))
        clock.advance(1)
        recovered = service.resolve((obs.identity,))[0]
        self.assertEqual((recovered.origin, recovered.state), ('provider', 'stale'))
        self.assertEqual(recovered.observations[0].fetched_at, obs.fetched_at)
