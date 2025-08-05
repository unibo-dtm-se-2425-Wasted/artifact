import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('my_project')

class MyClass:
    def my_method(self):
        return "Hello World"

logger.info("my_project loaded")

