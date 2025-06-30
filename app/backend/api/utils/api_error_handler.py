
from ...logger import CustomLogger
from flask import jsonify 
from ...exceptions import BaseAPIError ,InternalServerError
from functools import wraps
from decimal import Decimal 
from marshmallow import Schema


def api_logger(logger:CustomLogger ,response_maker=None):
    def catch_exceptions(f):
        """
        Decorator for uniform error handling across all endpoints
        """
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except BaseAPIError as e:
                logger.logger.debug(f"Error in {f.__name__}: {e}")

                if response_maker:
                    return response_maker(e.to_response(),e.status_code)
                
                return jsonify(e.to_response()), e.status_code
            
            except Exception as e:
                logger.logger.error(
                    f"Unexpected error in {f.__name__}: {type(e).__name__} - {str(e)}",
                    stack_info=True,
                    stacklevel=1
                )
                unexpected_error = InternalServerError(str(e))
                if response_maker:
                    return response_maker(unexpected_error.to_response() ,unexpected_error.status_code)
                return jsonify(unexpected_error.to_response()), 500
            
        return wrapper
    return catch_exceptions

