from doaa_handshake import build


def main():
    for language in ("ar", "en", "zh"):
        result = build(language)
        assert result["status"] == "handshake_ready"
        assert result["message"]["protocol"] == "doaa.handshake.v1"
        assert set(result["message"]["references"]) == {"R1", "R2", "R3"}
        assert result["message"]["automatic_execution"] is False
        assert result["execution_authority"] == "none"
        assert result["model_weights_modified"] is False
        assert len(result["serialized"].encode("utf-8")) <= 8192
    assert build("fr")["reason"] == "language_unsupported"
    print('{"tests":4,"status":"passed","weights_modified":false,"authority":"none"}')


if __name__ == "__main__":
    main()
