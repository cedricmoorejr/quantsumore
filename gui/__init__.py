from .cpi.calculateGUI import InflationCalculatorApp
from quantsumore.api.cpi.ConsumerPriceIndexAPI import engine as gui
inflation_calculator = gui.CPI_U.InflationAdjustment

# Create the app object
GUI = InflationCalculatorApp(inflation_calculator)

__all__ = ['GUI']
