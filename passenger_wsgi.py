import os
import sys

# Add current directory to python path
sys.path.insert(0, os.path.dirname(__file__))

# Try to import and run the application, logging any startup errors
try:
    from app import app as application
except Exception as e:
    import traceback
    error_file = os.path.join(os.path.dirname(__file__), "passenger_error.log")
    with open(error_file, "w", encoding="utf-8") as f:
        f.write("Passenger WSGI Startup Error:\n")
        traceback.print_exc(file=f)
    raise e