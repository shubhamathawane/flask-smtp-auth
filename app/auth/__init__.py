from flask import Blueprint, request, jsonify, url_for, render_template
from app.models.user import User
from app import db
from app.utils.email import generate_confirmation_token, confirm_token, send_email
from config import Config
auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # Generate verification token
    token = generate_confirmation_token(user.email)
    print(f"data : {Config.MAIL_DEFAULT_SENDER}")
    confirm_url = url_for("auth.confirm_email", token=token, _external=True)
    html = render_template("email/confirm.html", confirm_url=confirm_url)

    # Send verification email
    send_email(user.email, "Please Confirm Your Email", html)

    return jsonify({"message": "A confirmation email has been sent."})


@auth.route("/confirm/<token>", methods=["GET"])
def confirm_email(token):
    try:
        email = confirm_token(token)
    except Exception as e:
        return jsonify({"message": "Invalid or expired token"}), 400

    user = User.query.filter_by(email=email).first_or_404()

    if user.is_verified:
        return jsonify({"message": "Account already verified"}), 200

    user.is_verified = True
    db.session.commit()

    return jsonify({"message": "You have confirmed your account!"}), 200


@auth.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    email = data.get("email")

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    # Generate reset token
    token = generate_confirmation_token(user.email)
    reset_url = url_for("auth.reset_with_token", token=token, _external=True)
    html = render_template("email/reset_password.html", reset_url=reset_url)

    # Send password reset email
    send_email(user.email, "Password Reset Request", html)

    return jsonify({"message": "A password reset email has been sent."})


@auth.route("/reset/<token>", methods=["GET", "POST"])
def reset_with_token(token):
    try:
        email = confirm_token(token)
    except Exception as e:
        return jsonify({"message": "Invalid or expired token"}), 400

    user = User.query.filter_by(email=email).first_or_404()

    if request.method == "POST":
        data = request.get_json()
        new_password = data.get("password")

        user.set_password(new_password)
        db.session.commit()

        return jsonify({"message": "Password reset successful"}), 200

    return jsonify({"message": "Provide a new password"}), 200
