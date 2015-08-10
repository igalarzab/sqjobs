import pytest

from ..connectors.base import Connector
from ..connectors.dummy import Dummy
from .fixtures import Adder


class TestConnectorInterface(object):

    def test_default_connector_interface(self):
        dummy = Dummy()

        with pytest.raises(NotImplementedError):
            Connector.get_queue(dummy, 'demo')

        with pytest.raises(NotImplementedError):
            Connector.enqueue(dummy, 'demo', {})

        with pytest.raises(NotImplementedError):
            Connector.dequeue(dummy, 'demo', wait_time=20)

        with pytest.raises(NotImplementedError):
            Connector.delete(dummy, 'demo', 'id')

        with pytest.raises(NotImplementedError):
            Connector.retry(dummy, 'demo', 'id', 10)

        with pytest.raises(NotImplementedError):
            Connector.get_queues(dummy)

        with pytest.raises(NotImplementedError):
            Connector.get_dead_letter_queues(dummy)
