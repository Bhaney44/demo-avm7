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

    call_json_ref(app_client)
    # app_client.call(DemoAVM7.vrf_verify, ... )
    # app_client.call(DemoAVM7.replace, ...)
    # app_client.call(DemoAVM7.b64decode, ...)
    # app_client.call(DemoAVM7.json_ref, ...):
    # app_client.call(DemoAVM7.ed25519verify_bare, ...):
    # app_client.call(DemoAVM7.sha3_256, ...):
    # app_client.call(DemoAVM7.block, ...):

    print("deleting app")
    app_client.delete()


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
