"""
Web routes for KOL Sentiment MCP
"""
from flask import Blueprint, jsonify, current_app, render_template

web_bp = Blueprint("web", __name__)

@web_bp.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html", 
        version=current_app.config.get("VERSION", "1.0.0")
    )

@web_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    # Check if Masa API client is initialized
    from app.services.masa_client import is_initialized
    
    health_data = {
        "status": "healthy",
        "version": current_app.config.get("VERSION", "1.0.0"),
        "masa_api_client": is_initialized(),
        "environment": current_app.config.get("ENV", "production")
    }
    
    return jsonify(health_data) 