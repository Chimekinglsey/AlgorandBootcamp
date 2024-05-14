import algokit_utils
import pytest
from algokit_utils import get_localnet_default_account
from algokit_utils.config import config
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

from smart_contracts.artifacts.smart_con.client import SmartConClient


@pytest.fixture(scope="session")
def smart_con_client(
    algod_client: AlgodClient, indexer_client: IndexerClient
) -> SmartConClient:
    config.configure(
        debug=True,
        # trace_all=True,
    )

    client = SmartConClient(
        algod_client,
        creator=get_localnet_default_account(algod_client),
        indexer_client=indexer_client,
    )

    client.deploy(
        on_schema_break=algokit_utils.OnSchemaBreak.AppendApp,
        on_update=algokit_utils.OnUpdate.AppendApp,
    )
    return client


def test_says_hello(smart_con_client: SmartConClient) -> None:
    result = smart_con_client.hello(name="World")

    assert result.return_value == "Hello, World"


def test_simulate_says_hello_with_correct_budget_consumed(
    smart_con_client: SmartConClient, algod_client: AlgodClient
) -> None:
    result = (
        smart_con_client.compose().hello(name="World").hello(name="Jane").simulate()
    )

    assert result.abi_results[0].return_value == "Hello, World"
    assert result.abi_results[1].return_value == "Hello, Jane"
    assert result.simulate_response["txn-groups"][0]["app-budget-consumed"] < 100