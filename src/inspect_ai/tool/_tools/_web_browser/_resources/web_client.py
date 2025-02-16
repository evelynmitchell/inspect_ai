"""A client to interract with the web server."""

import sys

import grpc
from dm_env_rpc.v1 import connection as dm_env_connection
from dm_env_rpc.v1 import dm_env_adaptor, dm_env_rpc_pb2

_DM_ENV_BASE_PORT = 9443
_WORLD_NAME = "WebBrowser"
_SESSION_FLAG = "--session_name="


def parse_args(cli_args: list[str]) -> tuple[str, str]:
    if not cli_args:
        return _WORLD_NAME, ""

    if cli_args[0].startswith(_SESSION_FLAG):
        world_name = cli_args[0][len(_SESSION_FLAG) :]

        if len(cli_args) == 1:
            return world_name, ""
        else:
            return world_name, " ".join(cli_args[1:])

    else:
        return _WORLD_NAME, " ".join(cli_args)


def main() -> None:
    world_name, command = parse_args(sys.argv[1:])

    # Keep connection open even when empty data pings are received. This is
    # required to avoid a "too many pings" error.
    options = [
        ("grpc.keepalive_permit_without_calls", 0),
        ("grpc.keepalive_timeout_ms", 20000),
        ("grpc.http2.max_pings_without_data", 0),
        ("grpc.http2.max_pings_without_data", 0),
        ("grpc.http2.max_ping_strikes", 0),
        ("grpc.http2.min_recv_ping_interval_without_data_ms", 0),
    ]
    channel = grpc.secure_channel(
        f"localhost:{_DM_ENV_BASE_PORT}",
        grpc.local_channel_credentials(),
        options=options,
    )
    connection = dm_env_connection.Connection(channel)

    specs = connection.send(
        dm_env_rpc_pb2.JoinWorldRequest(world_name=world_name)
    ).specs

    with dm_env_adaptor.DmEnvAdaptor(
        connection=connection, specs=specs, nested_tensors=False
    ) as env:
        time_step = env.step({"command": command})
        for key, value in time_step.observation.items():
            print(key, ": ", value)
        env.close()


if __name__ == "__main__":
    main()
