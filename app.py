import os
from flask import Flask, render_template
from config import Config
from database.database import db, init_db
from database.models import User, Customer
from ontology.ontology_manager import OntologyManager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Database
    init_db(app)

    # Register Blueprints
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.transaction_routes import transaction_bp
    from routes.customer_routes import customer_bp
    from routes.alert_routes import alert_bp
    from routes.ontology_routes import ontology_bp
    from routes.report_routes import report_bp
    from routes.import_routes import import_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(alert_bp)
    app.register_blueprint(ontology_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(import_bp)

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    # Startup setup
    with app.app_context():
        # Check if database needs seeding
        if not User.query.filter_by(username='admin').first() or Customer.query.count() == 0:
            print("Database empty or missing admin user. Auto-seeding initial dataset...")
            from database.seed_data import seed_database
            seed_database(app)

        # Load ontology into memory
        print("Loading MoneyLaunderingDetectionOntology into RDF graph...")
        app.ontology_manager = OntologyManager()

    return app

if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*70)
    print(" MONEY LAUNDERING DETECTION SYSTEM USING ONTOLOGY ")
    print(" Web Application Running at: http://127.0.0.1:5000")
    print(" Demo Credentials: Admin (admin / admin123)")
    print("="*70 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
