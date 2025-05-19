"""
MCP API routes for KOL Sentiment MCP
"""
from flask import Blueprint, jsonify, request, current_app
from model_context_protocol import MCPRequest, MCPResponse, MCPError
from app.utils.logger import get_component_logger
from app.handlers.kol_actions import handle_kol_action

logger = get_component_logger("mcp_api")
mcp_bp = Blueprint("mcp", __name__, url_prefix="/api/mcp")

@mcp_bp.route("/ping", methods=["GET"])
def ping():
    """Health check for MCP API"""
    return jsonify({
        "status": "ok",
        "message": "KOL Sentiment MCP API is running",
        "version": current_app.config.get("VERSION", "1.0.0")
    })

@mcp_bp.route("/query", methods=["POST"])
def query():
    """Main MCP query endpoint"""
    logger.info("Received MCP query")
    
    if not request.is_json:
        logger.error("Request body is not JSON")
        return jsonify({"error": "Request body must be JSON"}), 400
    
    try:
        # Parse request as MCP request
        req_data = request.get_json()
        mcp_request = MCPRequest.parse_obj(req_data)
        
        logger.info(f"Processing action: {mcp_request.action}")
        
        # Handle KOL actions
        if mcp_request.action.startswith("kol."):
            result = handle_kol_action(mcp_request)
            response = MCPResponse(id=mcp_request.id, result=result)
            return jsonify(response.dict())
        else:
            error_msg = f"Unsupported action: {mcp_request.action}"
            logger.error(error_msg)
            error = MCPError(code="UNSUPPORTED_ACTION", message=error_msg)
            response = MCPResponse(id=mcp_request.id, error=error)
            return jsonify(response.dict()), 400
    
    except Exception as e:
        logger.exception(f"Error processing MCP request: {str(e)}")
        error = MCPError(code="INTERNAL_ERROR", message=str(e))
        response = MCPResponse(id=request.get_json().get("id", "unknown"), error=error)
        return jsonify(response.dict()), 500 