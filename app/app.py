"""
KOL Sentiment MCP - Flask Application
A Model Context Protocol (MCP) implementation for social media KOL Sentiment using Masa AI API
"""
import os
import json
from flask import Flask
from flask_cors import CORS
from loguru import logger
import dotenv
from app.utils.logger import setup_logging

def create_app(test_config=None):
    """Create and configure the Flask application"""
    # Load environment variables
    dotenv.load_dotenv()
    
    # Configure logging
    setup_logging()
    logger.info("Starting KOL Sentiment MCP")
    
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Set default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        PORT=int(os.environ.get("PORT", 5000)),
        MASA_API_KEY=os.environ.get("MASA_API_KEY"),
        MASA_API_URL=os.environ.get("MASA_API_URL", "https://data.dev.masalabs.ai/api"),
        LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"),
        RATE_LIMIT_PER_MINUTE=int(os.environ.get("RATE_LIMIT_PER_MINUTE", 100)),
        DEFAULT_MAX_RESULTS=int(os.environ.get("DEFAULT_MAX_RESULTS", 10)),
        DEFAULT_SENTIMENT_THRESHOLD=float(os.environ.get("DEFAULT_SENTIMENT_THRESHOLD", 0.5)),
        ENABLE_SENTIMENT_ANALYSIS=os.environ.get("ENABLE_SENTIMENT_ANALYSIS", "true").lower() == "true",
        ENABLE_TOPIC_EXTRACTION=os.environ.get("ENABLE_TOPIC_EXTRACTION", "true").lower() == "true",
        CACHE_TTL_SECONDS=int(os.environ.get("CACHE_TTL_SECONDS", 3600)),
        VERSION="1.0.0"
    )
    
    # Load development configuration if available
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "dev_config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                if "version" in config_data:
                    app.config["VERSION"] = config_data["version"]
                logger.info(f"Loaded dev config from {config_path}")
    except Exception as e:
        logger.warning(f"Could not load dev config: {str(e)}")
    
    # Load test config if provided
    if test_config is not None:
        app.config.from_mapping(test_config)
        logger.info("Test configuration loaded")
    
    # Enable CORS
    CORS(app)
    
    # Create instance directory if needed
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Register blueprints
    from app.routes.web import web_bp
    from app.routes.mcp import mcp_bp
    
    app.register_blueprint(web_bp)
    app.register_blueprint(mcp_bp)
    
    # Initialize Masa API client
    if app.config.get("MASA_API_KEY"):
        try:
            from app.services.masa_client import initialize_masa_client
            initialize_masa_client(app.config["MASA_API_KEY"], app.config["MASA_API_URL"])
            logger.info(f"Masa API client initialized with URL: {app.config['MASA_API_URL']}")
        except Exception as e:
            logger.error(f"Failed to initialize Masa API client: {str(e)}")
    else:
        logger.warning("No Masa API key provided. API client not initialized.")
    
    # Initialize NLP services if enabled
    if app.config.get("ENABLE_SENTIMENT_ANALYSIS") or app.config.get("ENABLE_TOPIC_EXTRACTION"):
        try:
            from app.services.nlp_service import initialize_nlp
            initialize_nlp()
            logger.info("NLP services initialized")
        except Exception as e:
            logger.error(f"Failed to initialize NLP services: {str(e)}")
    
    logger.info(f"Flask app initialized on port {app.config.get('PORT', 5000)}")
    return app 