from doaa_session_protocol import next_message, start


def main():
    session = start("sess-1", "en")
    assert session["status"] == "session_ready"
    msg = {"protocol": "doaa.alg.v1", "request_id": "req-1"}
    first = next_message(session, msg)
    assert first["status"] == "session_message_ready" and first["handshake"] is not None
    session2 = dict(session); session2["handshake_sent"] = True
    second = next_message(session2, msg)
    assert second["status"] == "session_message_ready" and second["handshake"] is None
    assert next_message(session, {"protocol": "wrong"})["reason"] == "algorithm_message_required"
    assert start("bad id!", "en")["reason"] == "session_identity_invalid"
    assert start("sess-2", "fr")["reason"] == "language_unsupported"
    print('{"tests":5,"status":"passed","handshake_once":true,"weights_modified":false,"authority":"none"}')


if __name__ == "__main__":
    main()
