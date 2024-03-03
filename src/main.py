from website import create_app, ensure_config_presence


if __name__ == '__main__':
    ensure_config_presence()
    
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)