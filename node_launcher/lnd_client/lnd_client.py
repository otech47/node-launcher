import codecs
import os
from typing import List

# noinspection PyPackageRequirements
import grpc
# noinspection PyProtectedMember,PyPackageRequirements
from grpc._plugin_wrapping import (_AuthMetadataContext,
                                   _AuthMetadataPluginCallback)

import node_launcher.lnd_client.rpc_pb2 as ln
import node_launcher.lnd_client.rpc_pb2_grpc as lnrpc
from node_launcher.configuration import Configuration

os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'


class LndClient(object):
    def __init__(self, configuration: Configuration):
        self.c = configuration
        lnd_tls_cert_path = os.path.join(self.c.lnd.lnddir, 'tls.cert')
        self.lnd_tls_cert = open(lnd_tls_cert_path, 'rb').read()

        cert_credentials = grpc.ssl_channel_credentials(self.lnd_tls_cert)

        admin_macaroon_path = os.path.join(self.c.lnd.lnddir, 'admin.macaroon')
        with open(admin_macaroon_path, 'rb') as f:
            macaroon_bytes = f.read()
            self.macaroon = codecs.encode(macaroon_bytes, 'hex')

        # noinspection PyUnusedLocal
        def metadata_callback(context: _AuthMetadataPluginCallback,
                              callback: _AuthMetadataContext):
            # noinspection PyCallingNonCallable
            callback([('macaroon', self.macaroon)], None)

        auth_credentials = grpc.metadata_call_credentials(metadata_callback)

        self.credentials = grpc.composite_channel_credentials(cert_credentials,
                                                              auth_credentials)

        self.grpc_channel = grpc.secure_channel(f'localhost:{self.c.lnd.grpc_port}',
                                                self.credentials)
        self.lnd_client = lnrpc.LightningStub(self.grpc_channel)
        self.wallet_unlocker = lnrpc.WalletUnlockerStub(self.grpc_channel)

    def generate_seed(self) -> ln.GenSeedResponse:
        request = ln.GenSeedRequest()
        response = self.wallet_unlocker.GenSeed(request)
        return response

    def initialize_wallet(self, password: str,
                          seed: List[str]) -> ln.InitWalletResponse:
        request = ln.InitWalletRequest()
        request.wallet_password = password.encode('latin1')
        request.cipher_seed_mnemonic.extend(seed)
        response = self.wallet_unlocker.InitWallet(request)
        return response

    def unlock(self, password: str) -> ln.UnlockWalletResponse:
        request = ln.UnlockWalletRequest()
        request.wallet_password = password.encode('latin1')
        response = self.wallet_unlocker.UnlockWallet(request)
        return response
