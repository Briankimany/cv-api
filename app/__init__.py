
import sys
import app.backend.db as _db
import app.backend.config as _config
import app.backend.exceptions as _exceptions
import app.backend.logger as _logger

sys.modules['app.db'] = _db
sys.modules['app.config'] = _config
sys.modules['app.exceptions'] = _exceptions
sys.modules['app.logger'] = _logger
