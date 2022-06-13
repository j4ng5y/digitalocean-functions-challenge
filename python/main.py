#!/usr/bin/env python3
import logging
import sys

import requests
import structlog
import click


class Request:
    """
    The Request class will contain all of our methods to handle a request to the DigitalOcean Function Challenge api.

    Attributes
    ----------
    API_URL : str
        The API_URL attribute is a static string to hold the URL of the API to access.

    name: str
        The name attribute is the name of the Sammy that we wish to create.

    t : str
        The "t" attribute is the type of the Sammy that we wish to create. This attribute is named "t" to avoid
        conflicting with the "type" keywork.

    log : structlog.BoundLogger
        The log attribute is not an attribute to be dealt with directly, rather the _get_log(self) method will retrieve
        the bound logger for us.

    Methods
    -------
    _set_name(name: str)
        This method sets the value of the name attribute.

    _set_type(t: str)
        This method sets the value of the t attribute.

    _set_log()
        This method gets the application logger and sets it to the log attribute.

    _get_url() -> str
        This method returns the value of the API_URL attribute.

    _get_name() -> str
        This method returns the value of the name attribute.

    _get_type() -> str
        This method returns the value of the t attribute.

    _build_headers() -> dict
        This static method returns a dictionary to be used as a request header.

    _build_request_body() -> dict
        This method returns a dictionary to be used as the request body.

    do() -> requests.Response
        This method is the primary class method and is used to perform the HTTP POST request.
    """
    def __init__(self, name: str, t: str):
        """
        Parameters
        ----------
        :param name: str
            The name to give to your new Sammy.
        :param t: str
            The type to give to your new Sammy.
        """
        self.API_URL = "https://functionschallenge.digitalocean.com/api/sammy"
        self.name = None
        self.t = None
        self.log: structlog.BoundLogger = None
        self._set_name(name)
        self._set_type(t)
        self._set_log()

    def _set_name(self, name: str):
        """This method sets the value of the name attribute.

        Parameters
        ----------
        :param name: str
            The name of the new sammy to create.
        """
        self.name = name

    def _set_type(self, t: str):
        """This method sets the value of the t attribute.

        Input validation is handled at the CLI layer. We will need to do further input validation if we don't do the
        validation at the CLI layer.

        Parameters
        ----------
        :param t: str
            The type of the new sammy to create.
        """
        self.t = t

    def _set_log(self):
        """This method gets the application logger and sets it to the log attribute."""
        self.log = structlog.stdlib.get_logger()

    def _get_url(self) -> str:
        """This method returns the value of the API_URL attribute."""
        return self.API_URL

    def _get_name(self) -> str:
        """This method returns the value of the name attribute."""
        return self.name

    def _get_type(self) -> str:
        """This method returns the value of the t attribute."""
        return self.t

    def _build_request_body(self) -> dict:
        """This method returns a dictionary to be used as the request body."""
        return {
            "name": self.name,
            "type": self.t,
        }

    @staticmethod
    def _build_headers() -> dict:
        """This static method returns a dictionary to be used as a request header."""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def do(self) -> requests.Response:
        """This method is the primary class method and is used to perform the HTTP POST request."""
        return requests.post(url=self._get_url(), json=self._build_request_body(), headers=self._build_headers())


class Response:
    """
    The Response class will contain all of our methods to handle a response from the DigitalOcean Functions Challenge
    api.

    Attributes
    ----------
    resp : requests:Response
        The actual response that is retrieved from performing the do() function from our Request class.
    log: : structlog.BoundLogger
        The log attribute is not an attribute to be dealt with directly, rather the _get_log(self) method will retrieve
        the bound logger for us.

    Methods
    -------
    _set_log() -> None
        Gets the application logger.

    _get_status_code() -> int
        Gets the HTTP status code from the requests.Response object the class was initialized with.

    _has_errors() -> bool
        A helper to let us know if errors exist in the requests.Response object the class was initialized with.

    do() -> None
        The primary method of this class. Do is used to print the information from the response to the terminal.
    """
    def __init__(self, resp: requests.Response):
        """
        Parameters
        ----------
        :param resp: requests.Response
            A response object from our Request class do() method.
        """
        self.resp = resp
        self.log: structlog.BoundLogger = None

        self._set_log()

    def _set_log(self):
        """Gets the application logger."""
        self.log = structlog.stdlib.get_logger()

    def _get_status_code(self) -> int:
        """Gets the HTTP status code from the requests.Response object the class was initialized with."""
        return self.resp.status_code

    def _has_errors(self) -> bool:
        """A helper to let us know if errors exist in the requests.Response object the class was initialized with."""
        respj: dict = self.resp.json()
        if "errors" in respj:
            return True
        else:
            return False

    def do(self) -> None:
        """The primary method of this class. Do is used to print the information from the response to the terminal."""
        if self._has_errors():
            for e in self.resp.json()["errors"]:
                for ee in self.resp.json()["errors"][e]:
                    self.log.error(ee)
                return
        else:
            self.log.info(self.resp.json()["message"])


def configure_logger():
    """Basic application level logging configuration"""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )


@click.command()
@click.option('-n', '--name', "name", help='The name to give to your new Sammy.')
@click.option('-t', '--type', "t", type=click.Choice([
    "sammy",
    "punk",
    "dinosaur",
    "retro",
    "pizza",
    "robot",
    "pony",
    "bootcamp",
    "xray"
], case_sensitive=False), help='The type to give to your new Sammy.')
def main(name, t):
    configure_logger()
    req = Request(name, t)
    response = req.do()
    resp = Response(response)
    resp.do()


if __name__ == "__main__":
    main()
