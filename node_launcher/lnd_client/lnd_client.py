import codecs
import os
from sys import platform
from typing import List

import grpc
from google.protobuf.json_format import MessageToDict
from grpc._plugin_wrapping import (
    _AuthMetadataPluginCallback,
    _AuthMetadataContext
)

import node_launcher.lnd_client.rpc_pb2 as ln
import node_launcher.lnd_client.rpc_pb2_grpc as lnrpc
from node_launcher.configuration import Configuration

os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'


class LndClient(object):
    def __init__(self, configuration: Configuration):

        lnd_tls_cert_path = os.path.join(self.main_lnd_path, 'tls.cert')
        self.lnd_tls_cert = open(lnd_tls_cert_path, 'rb').read()

        cert_credentials = grpc.ssl_channel_credentials(self.lnd_tls_cert)

        admin_macaroon_path = os.path.join(self.main_lnd_path, 'admin.macaroon')
        with open(admin_macaroon_path, 'rb') as f:
            macaroon_bytes = f.read()
            self.macaroon = codecs.encode(macaroon_bytes, 'hex')

        def metadata_callback(context: _AuthMetadataPluginCallback,
                              callback: _AuthMetadataContext):
            callback([('macaroon', self.macaroon)], None)

        auth_credentials = grpc.metadata_call_credentials(metadata_callback)

        self.credentials = grpc.composite_channel_credentials(cert_credentials,
                                                              auth_credentials)

        self.grpc_channel = grpc.secure_channel(rpc_uri,
                                                self.credentials

                                                )
        self.lnd_client = lnrpc.LightningStub(self.grpc_channel)