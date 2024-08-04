from website.setup_app import AppSetup

if __name__ == '__main__':
    app_setup = AppSetup()
    app = app_setup.create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)