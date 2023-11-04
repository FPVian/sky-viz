from config.logger import Logger


def test_logger_levels(caplog):
    '''
    Test that the logger creates logs with level in all caps.
    Azure Log Analytics queries will count the logs based on status.
    '''
    log = Logger.create(__name__)
    log.warning('')
    assert 'WARNING' in caplog.text
    caplog.clear()
    log.error('')
    assert 'ERROR' in caplog.text
    caplog.clear()
    log.critical('')
    assert 'CRITICAL' in caplog.text
