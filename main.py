"""
Main entry point for XAU Quant Platform
"""

import sys
import logging
from config import get_config
from master_controller import MasterController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Main entry point
    """
    try:
        logger.info("Initializing XAU Quant Platform...")
        
        # Load configuration
        config = get_config()
        logger.info(f"Configuration loaded: {config['symbol']}")
        
        # Initialize master controller
        controller = MasterController(config)
        logger.info("Master controller initialized")
        
        # Run backtest
        logger.info("Starting backtest execution...")
        report = controller.run_backtest()
        
        logger.info("Platform execution completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Platform error: {str(e)}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
