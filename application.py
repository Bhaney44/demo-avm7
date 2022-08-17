from typing import Literal

from pyteal import *
from beaker import *

class DemoAVM7(Application):

    VrfProof = abi.StaticArray[abi.Byte, Literal[80]]
    VrfHash = abi.StaticArray[abi.Byte, Literal[64]]
    @external
    def vrf_verify(self, msg: abi.DynamicArray[abi.Byte], proof: VrfProof, pub_key: abi.Address, *, output: VrfHash):
        return Seq(
            # Use the Algorand VRF 
            vrf_result := VrfVerify.algorand(
                # Note: in practice the message is likely to be something like:
                #    sha512_256(concat(itob(round), block.seed(round)))
                # Get the bytes from the message (chop off 2 as they're the uint16 encoded length)
                Suffix(msg.encode(), Int(2)),
                # Get the bytes from the proof
                proof.encode(),
                # Note: in practice this is likely to be some hardcoded public key or one of
                #   a set of "pre-approved" public keys
                # Get the pubkey bytes
                pub_key.encode(),
            ),
            # Check Successful
            Assert(vrf_result.output_slots[1].load() == Int(1)),
            # Write the result to the output
            output.decode(vrf_result.output_slots[0].load())
        ) 

    @external
    def replace(self):
        #replace2            
        #replace3            
        return Approve()

    @external
    def b64decode(self):
        #base64_decode       
        return Approve()

    @external
    def json_ref(self):
        #json_ref            
        return Approve()

    @external
    def ed25519verify_bare(self):
        #ed25519verify_bare  
        return Approve()

    @external
    def sha3_256(self):
        #sha3_256            
        return Approve()

    @external
    def block(self):
        # seed
        #block  (Seed and timestamp)
        return Approve()


    @external
    def noop(self):
        return Approve()

    @delete(authorize=Authorize.only(Global.creator_address()))
    def delete(self):
        return Approve()
