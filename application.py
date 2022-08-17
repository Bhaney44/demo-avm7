from typing import Literal

from pyteal import *
from beaker import *


class DemoAVM7(Application):
    @external
    def vrf_verify(
        self,
        msg: abi.DynamicArray[abi.Byte],
        proof: abi.StaticArray[abi.Byte, Literal[80]],
    ):
        return Approve()

    @external
    def replace(self):
        # replace2
        # replace3
        return Approve()

    @external
    def b64decode(self):
        # base64_decode
        return Approve()

    JsonExampleResult = abi.Tuple3[abi.String, abi.Uint64, abi.String]

    @external
    def json_ref(self, json_str: abi.String, *, output: JsonExampleResult):
        return Seq(
            (s := abi.String()).set(
                JsonRef.as_string(json_str.get(), Bytes("string_key"))
            ),
            (i := abi.Uint64()).set(
                JsonRef.as_uint64(json_str.get(), Bytes("uint_key"))
            ),
            (o := abi.String()).set(
                JsonRef.as_object(json_str.get(), Bytes("obj_key"))
            ),
            output.set(s, i, o),
        )

    @external
    def ed25519verify_bare(self):
        # ed25519verify_bare
        return Approve()

    @external
    def sha3_256(self):
        # sha3_256
        return Approve()

    @external
    def block(self):
        # seed
        # block  (Seed and timestamp)
        return Approve()

    @delete(authorize=Authorize.only(Global.creator_address()))
    def delete(self):
        return Approve()
