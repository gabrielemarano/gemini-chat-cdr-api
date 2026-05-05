"""
Package per i client di database e servizi esterni.
"""
from .oracle_client import OracleClient
from .mock_client import MockClient

__all__ = ['OracleClient', 'MockClient']
