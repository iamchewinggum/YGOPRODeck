from flask import Flask, request, jsonify
from routes.users import users_bp


app = Flask(__name__)

app.register_blueprint(users_bp, url_prefix='/api/users')



@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}),200




if __name__ == "__main__":
    app.run(debug=True) 

