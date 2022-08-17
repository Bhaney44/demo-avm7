from algosdk.encoding import encode_address
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    TransactionWithSigner,
)
from application import DemoAVM7
from beaker import Application, client, sandbox


def demo():

    app_client = client.ApplicationClient(
        client=sandbox.get_algod_client(),
        app=DemoAVM7(),
        signer=sandbox.get_accounts().pop().signer,
    )

    app_id, app_addr, _ = app_client.create()
    print(f"Created app with id {app_id} and address {app_addr}")

    call_vrf(app_client)
    call_block_ops(app_client)
    call_json_ref(app_client)

    # app_client.call(DemoAVM7.vrf_verify, ... )
    # app_client.call(DemoAVM7.replace, ...)
    # app_client.call(DemoAVM7.b64decode, ...)
    # app_client.call(DemoAVM7.json_ref, ...):
    # app_client.call(DemoAVM7.ed25519verify_bare, ...):
    # app_client.call(DemoAVM7.sha3_256, ...):
    # app_client.call(DemoAVM7.block, ...):

    ## app_client.call(DemoAVM7.replace, ...)
    ## app_client.call(DemoAVM7.b64decode, ...)
    ## app_client.call(DemoAVM7.json_ref, ...):
    ## app_client.call(DemoAVM7.ed25519verify_bare, ...):
    ## app_client.call(DemoAVM7.sha3_256, ...):
    ## app_client.call(DemoAVM7.block, ...):

    # print("deleting app")
    # app_client.delete()


def call_vrf(app_client: client.ApplicationClient):
    """Calls the app method to verify the message/proof/pubkey

    In practice the values would not be hardcoded as they are here.
        msg should be something like sha512_256(round | round_seed)
        proof should be the result of calling Prove (or similar)
        pub_key should be the public key of the key pair used to generate the proof from the message

    """

    msg: bytes = bytes.fromhex(
        "528b9e23d93d0e020a119d7ba213f6beb1c1f3495a217166ecd20f5a70e7c2d7"
    )
    proof: bytes = bytes.fromhex(
        "372a3afb42f55449c94aaa5f274f26543e77e8d8af4babee1a6fbc1c0391aa9e6e0b8d8d7f4ed045d5b517fea8ad3566025ae90d2f29f632e38384b4c4f5b9eb741c6e446b0f540c1b3761d814438b04"
    )
    pub_key: bytes = bytes.fromhex(
        "3a2740da7a0788ebb12a52154acbcca1813c128ca0b249e93f8eb6563fee418d"
    )
    address = encode_address(pub_key)

    atc = AtomicTransactionComposer()
    app_client.add_method_call(
        atc, DemoAVM7.vrf_verify, msg=msg, proof=proof, pub_key=address
    )
    for x in range(8):
        # Add dummy transactions to increase op budget, a logic sig could also be used
        # to decrease the cost since it has a budget of 20k (apps have 700)
        app_client.add_method_call(atc, DemoAVM7.noop, note=x.to_bytes(8, "big"))
    result = atc.execute(app_client.client, 4)

    actual_result = bytes(result.abi_results[0].return_value).hex()

    expected_result = "ed04a66ab306b3b39fe06da21af0d7bee5020d62cd18c39dbdb5c4f222336c2ada42ac1c110be3254872318240f55547da145859786b7d17be1002d4dde209b7"
    print(f"VRF Result: {actual_result}")

    assert actual_result == expected_result


def call_block_ops(app_client: client.ApplicationClient):
    """Calls the new block header accessors for getting timestamp and
    seed from a historical block
    """
    # Lower the range of last-first so we get access to more blocks
    sp = app_client.client.suggested_params()
    sp.last = sp.first + 5

    result = app_client.call(DemoAVM7.block, suggested_params=sp)
    ts, hash = result.return_value
    print(f"Block Timestamp: {ts}")
    print(f"Block Hash: {bytes(hash).hex()}")


def call_json_ref(app_client: client.ApplicationClient):
    import json

    obj = {
        "string_key": "In Xanadu did Kubla Khan",
        "uint_key": 42,
        "obj_key": {"lol": "lmao"},
    }

    json_str = json.dumps(obj)
    result = app_client.call(DemoAVM7.json_ref, json_str=json_str)
    print(f"result {result.return_value}")

    string_key_value, uint_key_value, obj_key_value = result.return_value
    assert obj["string_key"] == string_key_value
    assert obj["uint_key"] == uint_key_value
    assert json.dumps(obj["obj_key"]) == obj_key_value


if __name__ == "__main__":
    demo()
