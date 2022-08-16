from application import DemoAVM7
from beaker import client, sandbox

def demo():

    app_client = client.ApplicationClient(
        client=sandbox.get_algod_client(),
        app=DemoAVM7(),
        signer=sandbox.get_accounts().pop().signer
    )

    app_id, app_addr, _ = app_client.create()
    print(f"Created app with id {app_id} and address {app_addr}")

    call_block_ops(app_client)

    # app_client.call(DemoAVM7.vrf_verify, ... )
    # app_client.call(DemoAVM7.replace, ...)
    # app_client.call(DemoAVM7.b64decode, ...)
    # app_client.call(DemoAVM7.json_ref, ...):
    # app_client.call(DemoAVM7.ed25519verify_bare, ...):
    # app_client.call(DemoAVM7.sha3_256, ...):
    # app_client.call(DemoAVM7.block, ...):

    print("deleting app")
    app_client.delete()

def call_block_ops(app_client: client.ApplicationClient):
    """ Calls the new block header accessors for getting timestamp and 
        seed from a historical block
    """
    # Lower the range of last-first so we get access to more blocks
    sp = app_client.client.suggested_params()
    sp.last = sp.first+5

    result = app_client.call(DemoAVM7.block, suggested_params=sp)
    ts, hash = result.return_value
    print(f"Block Timestamp: {ts}")
    print(f"Block Hash: {bytes(hash).hex()}")

if __name__ == "__main__":
    demo()