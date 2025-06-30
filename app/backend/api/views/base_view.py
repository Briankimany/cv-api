
from flask import request ,jsonify
from flask.views import MethodView
from marshmallow import Schema ,ValidationError

from ...exceptions import InvalidTokenError ,InvalidDataError
from ...logger import CustomLogger
from ...config import CONFIG,AppConfig
from ...db.managers import init_db_access_layer ,TokenIssuer
from ..utils import api_logger

from ...config.api_schema import * 


class BaseView(MethodView):
    """
    Foundation for all route views with token-based authentication and standardized logging.

    Inherits:
        flask.views.MethodView

    Responsibilities:
        - Provides consistent structure for API views.
        - Initializes and attaches:
            - A shared database access layer (`db_access`)
            - A shared token issuer (`token_issuer`)
            - A structured logger used for all subclasses
        - Applies the `api_logger` decorator to log all incoming requests.
        - Optionally stores an expected Marshmallow schema for request validation.

    Args:
        config (AppConfig): Application configuration object. Defaults to global CONFIG.
        expected_data_format (Schema): Optional Marshmallow schema for validating request payloads.

    Attributes:
        expected_data_format (Schema): A Marshmallow schema instance for input validation (per-view).
        logger (CustomLogger): Class-level logger injected into all view methods via decorators.
        db_access (DbAccessLayer): Shared interface for reading/writing to the database.
        token_issuer (TokenIssuer): Token issuing and management service.
    """

    def __init__(self,config:AppConfig=CONFIG,expected_data_format:Schema=None):
        self.expected_data_format:Schema = expected_data_format

        logger = CustomLogger(config=config.loggers['api'])
        self.__class__.logger = logger
        self.__class__.decorators = [api_logger(logger ,self.return_response)]

        self.__class__.db_access = init_db_access_layer(config)
        self.__class__.token_issuer = TokenIssuer(config)
        self.token_issuer =  TokenIssuer(config)


    @classmethod
    def extract_token_from_header(cls):
        """
        Extracts token from Authorization header (Bearer scheme)
        Raises InvalidTokenError if missing/malformed
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise InvalidTokenError("Missing or invalid Authorization header")
        return auth_header[7:].strip()

    def parse_and_validate(self,expected_data_format:Schema=None):
        """
        Parses and validates the request data against the expected format.
        Args:
            expected_data_format: Optional dictionary with expected data format
        Returns:
            Parsed and validated data
        """
        try:
            if not expected_data_format:
                expected_data_format = self.expected_data_format

            data =expected_data_format().load(request.get_json())
            self.logger.debug(f"ROUTE: {request.path} METHOD :{request.method}: INCOMING REQUEST DATA: {data}")
            return data
        except ValidationError as e:
            msg = []
            for key ,msgs in e.messages.items():
                msg.extend([f"{key} : {msg}" for msg in msgs])
            msg = ':\t'.join(msg)
            error= InvalidDataError(msg ,msg)
            self.logger.warning(f"Validation Error: {error}")
            raise error 
        

    def get_request_remote_addr(self):
        """
        Returns the remote address of the request.
        """
        return request.remote_addr\
    
    def return_response(self, response_data:dict, code:int=200):
        """
        Returns a Flask JSON response with the given data and HTTP status code.

        Args:
            response_data (dict): The data to be returned as JSON.
            code (int, optional): HTTP status code for the response. Defaults to 200.

        Returns:
            A tuple of (JSON response, status code) suitable for Flask response.
        """

        self.logger.debug(f"[RESPONSE] :ROUTE {request.path} :data {response_data}")
        return jsonify(response_data), code