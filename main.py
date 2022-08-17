import base64
import json
from hashlib import sha3_256
from typing import cast
from nacl.signing import SigningKey

from algosdk.encoding import encode_address
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    AccountTransactionSigner,
)
from application import DemoAVM7
from beaker import client, sandbox


def demo():

    app_client = client.ApplicationClient(
        client=sandbox.get_algod_client(),
        app=DemoAVM7(),
        signer=sandbox.get_accounts().pop().signer,
    )

    app_id, app_addr, _ = app_client.create()
    print(f"Created app with id {app_id} and address {app_addr}")

    # call_vrf(app_client)
    # call_block_ops(app_client)
    # call_json_ref(app_client)
    # call_b64_decode(app_client)
    # call_sha3_256(app_client)
    # call_replace(app_client)
    call_ed25519_bare(app_client)

    print("deleting app")
    app_client.delete()


def call_ed25519_bare(app_client: client.ApplicationClient):
    # Take the signer from the app client, we already know its
    # of type AccountTransactionSigner so we cheat a bit here
    b64_pk = cast(AccountTransactionSigner, app_client.get_signer()).private_key
    pk = list(base64.b64decode(b64_pk))
    signing_key = SigningKey(bytes(pk[:32]))

    msg = "Sign me please"
    sig = signing_key.sign(msg.encode()).signature

    atc = AtomicTransactionComposer()
    app_client.add_method_call(atc, DemoAVM7.ed25519verify_bare, msg=msg, sig=sig)
    # Increase our opcode budget, costs 1900
    # subtract actual app call ops 1900 - 700 = 1200
    # ceil(1200/700) = 2
    for x in range(2):
        app_client.add_method_call(atc, DemoAVM7.noop, note=x.to_bytes(8, "big"))

    group_result = atc.execute(app_client.client, 4)
    result = group_result.abi_results[0]
    print(f"got: {result.return_value}")

    assert result.return_value


def call_replace(app_client: client.ApplicationClient):
    msg = "replace these bytes"
    start = msg.find("these")
    replace_with = "those"

    result = app_client.call(
        DemoAVM7.replace, orig=msg, start=start, replace_with=replace_with
    )
    print(f"got: {result.return_value}")

    assert result.return_value == "replace those bytes"


def call_sha3_256(app_client: client.ApplicationClient):
    msg = "hash me plz"
    result = app_client.call(DemoAVM7.sha3_256, to_hash=msg)
    hex_result = bytes(result.return_value).hex()
    print(f"got: {hex_result}")

    expected = sha3_256(msg.encode()).hexdigest()
    assert hex_result == expected


def call_b64_decode(app_client: client.ApplicationClient):
    msg = b"I was a terror since the public school era"
    result = app_client.call(
        DemoAVM7.b64decode, b64encoded=base64.b64encode(msg).decode("utf8")
    )
    print(f"got: {result.return_value}")

    assert msg.decode("utf8") == result.return_value


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
    group_result = atc.execute(app_client.client, 4)
    result = group_result.abi_results[0]
    print(f"got: {result.return_value}")

    actual_result = bytes(result.return_value).hex()
    expected_result = "ed04a66ab306b3b39fe06da21af0d7bee5020d62cd18c39dbdb5c4f222336c2ada42ac1c110be3254872318240f55547da145859786b7d17be1002d4dde209b7"
    assert actual_result == expected_result


def call_block_ops(app_client: client.ApplicationClient):
    """Calls the new block header accessors for getting timestamp and
    seed from a historical block
    """

    # Lower the range of last-first so we get access to more blocks
    sp = app_client.client.suggested_params()
    sp.last = sp.first + 5

    round = sp.first - 10

    result = app_client.call(DemoAVM7.block, round=round, suggested_params=sp)
    print(f"got: {result.return_value}")
    ts, seed = result.return_value

    block_info = app_client.client.block_info(round)["block"]
    actual_ts = block_info["ts"]
    actual_seed = (
        list(base64.b64decode(block_info["seed"]))
        if "seed" in block_info
        else list(bytes(32))
    )

    assert ts == actual_ts
    assert seed == actual_seed


def call_json_ref(app_client: client.ApplicationClient):
    obj = {
        "string_key": "In Xanadu did Kubla Khan",
        "uint_key": 42,
        "obj_key": {"lol": "lmao"},
    }

    json_str = json.dumps(obj)
    result = app_client.call(DemoAVM7.json_ref, json_str=json_str)
    print(f"got: {result.return_value}")

    string_key_value, uint_key_value, obj_key_value = result.return_value
    assert obj["string_key"] == string_key_value
    assert obj["uint_key"] == uint_key_value
    assert json.dumps(obj["obj_key"]) == obj_key_value


if __name__ == "__main__":
    demo()
