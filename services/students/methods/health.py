from flask import Blueprint, jsonify, request


def health_blueprint():
    blueprint = Blueprint("health", __name__)

    @blueprint.route("/health", methods=["GET"])
    def health():
        ip_info = {
                    'direct_ip': request.remote_addr,
                    'forwarded_for': request.headers.get('X-Forwarded-For'),
                    'real_ip': request.headers.get('X-Real-IP'),
                    'client_ip': request.headers.get('CF-Connecting-IP')
                }

        client_ip = (
            request.headers.get('X-Forwarded-For', '').split(',')[0] or
            request.headers.get('X-Real-IP') or
            request.headers.get('CF-Connecting-IP') or
            request.remote_addr
        )

        ip_info['detected_client_ip'] = client_ip

        return jsonify({"status": "ok", "service": "Get-One Student Service", "IP": ip_info }), 200

    return blueprint
