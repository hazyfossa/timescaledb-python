def test_timescale_container_basic(timescale_container):
    """Test that the TimescaleDB container starts up and is accessible."""
    # Get connection details
    host = timescale_container.get_container_host_ip()
    exposed_port = timescale_container.get_exposed_port(timescale_container.port)
    assert host is not None
    assert exposed_port is not None
    assert exposed_port != timescale_container.port
