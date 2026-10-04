"""SYNTHETIC ONLY: deterministic provider and clock; no network or game data."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone

from aioncrafter.providers import PriceCapabilities
from .helpers import observation, market


class Clock:
    def __init__(self):
        self.now = datetime(2026, 10, 4, 11, tzinfo=timezone.utc)

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += timedelta(seconds=seconds)


def sample(**changes):
    return replace(observation(), observed_at='2026-10-04T10:00:00Z', **changes)


class SyntheticProvider:
    capabilities = PriceCapabilities('SYNTHETIC-provider', (market(),), True, False, True,
                                     'SYNTHETIC scripted responses only', 'tests/synthetic_prices.py')

    def __init__(self, observations=()):
        self.responses = {o.identity: (o,) for o in observations}
        self.calls = []
        self.failures = []

    def observations_for(self, identity):
        return self.observations_for_batch((identity,))[identity]

    def observations_for_batch(self, identities):
        self.calls.append(identities)
        if self.failures:
            failure = self.failures.pop(0)
            if failure is not None:
                raise failure
        return {i: self.responses.get(i, ()) for i in identities}
