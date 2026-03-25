import os
import sys
import io
import base64
import matplotlib
matplotlib.use('Agg') # Non-interactive backend for server use
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import traceback

def execute_python_plot(code: str) -> dict:
    """
    Executes Python code and captures the matplotlib plot as a base64 string.
    """
    # Create a clean namespace
    globals_dict = {
        'plt': plt,
        'pd': pd,
        'np': np,
        '__name__': '__main__'
    }
    
    # Redirect stdout
    stdout = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = stdout

    try:
        # Clear any existing plots
        plt.clf()
        plt.close('all')
        
        # Execute the code
        exec(code, globals_dict)
        
        # Capture the plot
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        
        output = stdout.getvalue()
        return {
            "success": True,
            "plot": f"data:image/png;base64,{img_str}",
            "stdout": output
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "stdout": stdout.getvalue()
        }
    finally:
        sys.stdout = old_stdout
