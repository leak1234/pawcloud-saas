from app import create_app

app = create_app()

if __name__ == '__main__':
    # El host '0.0.0.0' es vital para que Docker exponga el puerto
    app.run(host='0.0.0.0', port=5000, debug=True)