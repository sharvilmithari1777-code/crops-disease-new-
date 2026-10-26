"""
Croplytics — Smart Agriculture Assistant
Main Flask Web Application
"""

import os
import json
import uuid
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, send_from_directory, abort, jsonify
)
from werkzeug.utils import secure_filename

# Import Domain Services
from services.database import (
    register_user, authenticate_user, get_user_by_id,
    log_activity, get_user_history, get_system_stats
)
from services.yield_prediction import predict_crop_yield, CROPS, REGIONS
from services.carbon_calculator import calculate_farm_carbon_footprint, EMISSION_FACTORS
from services.disease_detection import analyze_plant_leaf, is_allowed_file

# Flask App Initialization
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("CROPLYTICS_SECRET_KEY", "croplytics-development-secret-key-2026")
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 Megabytes limit

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Context processor for current_user
@app.context_processor
def inject_current_user():
    user_id = session.get("user_id")
    current_user = get_user_by_id(user_id) if user_id else None
    return dict(current_user=current_user)

# Helper to load product catalog
def get_products():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "products.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Error reading products.json]: {e}")
        return []

# -------------------------------------------------------------
# Routes
# -------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")
    stats = get_system_stats()
    recent_history = get_user_history(user_id=user_id, limit=6)
    return render_template("dashboard.html", stats=stats, recent_history=recent_history)

@app.route("/disease-detection", methods=["GET", "POST"])
def disease_detection():
    result = None
    analyzed_image_url = None
    selected_crop_hint = ""

    if request.method == "POST":
        selected_crop_hint = request.form.get("crop_hint", "").strip()
        sample_image_name = request.form.get("sample_image", "").strip()

        # Case A: Preset sample leaf requested
        if sample_image_name:
            safe_sample = os.path.basename(sample_image_name)
            sample_path = os.path.join(app.root_path, "static", "images", "samples", safe_sample)

            if os.path.exists(sample_path):
                result = analyze_plant_leaf(sample_path, crop_hint=selected_crop_hint)
                analyzed_image_url = url_for("static", filename=f"images/samples/{safe_sample}")

                # Log activity
                user_id = session.get("user_id")
                input_desc = f"Sample: {safe_sample} (Hint: {selected_crop_hint or 'Auto'})"
                res_desc = f"Diagnosed: {result.get('disease_name')} ({result.get('confidence_score')}%)"
                log_activity(user_id, "disease", input_desc, res_desc)
                flash(f"AI diagnosis completed: {result.get('disease_name')} ({result.get('confidence_score')}%)", "success")
            else:
                flash("Selected sample file was not found on server.", "error")

        # Case B: User uploaded a file
        elif "leaf_image" in request.files:
            file = request.files["leaf_image"]

            if file and file.filename != "":
                if is_allowed_file(file.filename):
                    original_name = secure_filename(file.filename)
                    ext = original_name.rsplit(".", 1)[1].lower() if "." in original_name else "jpg"
                    unique_name = f"leaf_{uuid.uuid4().hex[:10]}.{ext}"
                    save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)

                    try:
                        file.save(save_path)
                        result = analyze_plant_leaf(save_path, crop_hint=selected_crop_hint)
                        analyzed_image_url = url_for("serve_uploaded_file", filename=unique_name)

                        # Log activity
                        user_id = session.get("user_id")
                        input_desc = f"Uploaded Leaf: {original_name} (Hint: {selected_crop_hint or 'Auto'})"
                        res_desc = f"Diagnosed: {result.get('disease_name')} ({result.get('confidence_score')}%)"
                        log_activity(user_id, "disease", input_desc, res_desc)
                        flash(f"AI diagnosis completed: {result.get('disease_name')} ({result.get('confidence_score')}%)", "success")
                    except Exception as e:
                        print(f"[Upload Error]: {e}")
                        flash("Error processing uploaded image. Please ensure it is a valid photograph.", "error")
                else:
                    flash("Invalid file format. Allowed formats: .jpg, .jpeg, .png, .webp", "error")
            else:
                flash("Please choose an image file to upload or select a sample leaf below.", "error")

    return render_template(
        "disease_detection.html",
        result=result,
        analyzed_image_url=analyzed_image_url,
        selected_crop_hint=selected_crop_hint
    )

@app.route("/yield-forecast", methods=["GET", "POST"])
def yield_forecast():
    result = None
    inputs = None

    if request.method == "POST":
        try:
            inputs = {
                "crop_type": request.form.get("crop_type", "Wheat").strip(),
                "region": request.form.get("region", "Punjab").strip(),
                "N": float(request.form.get("N", 120)),
                "P": float(request.form.get("P", 60)),
                "K": float(request.form.get("K", 40)),
                "ph": float(request.form.get("ph", 6.8)),
                "temperature": float(request.form.get("temperature", 24.0)),
                "rainfall": float(request.form.get("rainfall", 750.0)),
                "humidity": float(request.form.get("humidity", 65.0)),
                "area": float(request.form.get("area", 2.0))
            }
            result = predict_crop_yield(inputs)

            # Log to history
            user_id = session.get("user_id")
            input_desc = f"{inputs['crop_type']} in {inputs['region']} ({inputs['area']} ha, NPK {inputs['N']}-{inputs['P']}-{inputs['K']})"
            res_desc = f"Forecast: {result['yield_per_ha']} t/ha | Total: {result['total_production_tonnes']} tonnes"
            log_activity(user_id, "yield", input_desc, res_desc)
            flash("Crop yield forecast generated successfully!", "success")
        except (ValueError, TypeError) as e:
            flash("Invalid input numbers. Please check your form values and try again.", "error")

    return render_template(
        "yield_forecast.html",
        result=result,
        inputs=inputs,
        crops=CROPS,
        regions=REGIONS
    )

@app.route("/carbon-calculator", methods=["GET", "POST"])
def carbon_calculator():
    result = None
    inputs = None

    if request.method == "POST":
        try:
            inputs = {
                "area": float(request.form.get("area", 1.0)),
                "fertilizer_kg": float(request.form.get("fertilizer_kg", 0.0)),
                "pesticide_qty": float(request.form.get("pesticide_qty", 0.0)),
                "pesticide_unit": request.form.get("pesticide_unit", "Litres").strip(),
                "fuel_litres": float(request.form.get("fuel_litres", 0.0)),
                "electricity_kwh": float(request.form.get("electricity_kwh", 0.0)),
                "irrigation_method": request.form.get("irrigation_method", "Flood / Furrow").strip()
            }
            result = calculate_farm_carbon_footprint(inputs)

            # Log to history
            user_id = session.get("user_id")
            input_desc = f"{inputs['area']} ha farm ({inputs['irrigation_method']}) | Fert: {inputs['fertilizer_kg']}kg, Fuel: {inputs['fuel_litres']}L"
            res_desc = f"Total: {result['total_tonnes_co2e']} t CO₂e ({result['emissions_per_ha_tonnes']} t/ha, {result['rating']})"
            log_activity(user_id, "carbon", input_desc, res_desc)
            flash("Carbon footprint calculations computed with documented IPCC emission factors.", "success")
        except (ValueError, TypeError) as e:
            flash("Invalid numerical values in carbon calculator. Please verify inputs.", "error")

    methods = list(EMISSION_FACTORS["irrigation_methods"].keys())
    return render_template(
        "carbon_calculator.html",
        result=result,
        inputs=inputs,
        irrigation_methods=methods
    )

@app.route("/products")
def products():
    catalog = get_products()
    return render_template("products.html", products=catalog)

@app.route("/api/order", methods=["POST"])
def place_order():
    """
    Processes real-world e-commerce fertilizer orders.
    Calculates subtotals, applies discounts/subsidies, generates order reference ID,
    and logs order activity in SQLite history.
    """
    try:
        data = request.get_json(silent=True) or request.form.to_dict()
        items = data.get("items", [])
        if isinstance(items, str):
            try:
                items = json.loads(items)
            except Exception:
                items = []

        if not items:
            return jsonify({
                "success": False,
                "message": "Your cart is empty. Please add items to your cart before proceeding."
            }), 400

        customer_name = data.get("customer_name", "Valued Farmer").strip() or "Valued Farmer"
        phone = data.get("phone", "").strip() or "Not Provided"
        address = data.get("address", "").strip() or "Farm Gate Delivery"
        pincode = data.get("pincode", "").strip() or "N/A"
        payment_method = data.get("payment_method", "Cash on Delivery").strip()
        coupon_applied = data.get("coupon", "").strip().upper()

        subtotal = 0.0
        for item in items:
            p = float(item.get("price_inr", item.get("price", 0)))
            q = int(item.get("qty", 1))
            subtotal += p * q

        discount = 0.0
        if coupon_applied in ["KISAN10", "FARMER10", "AGRI10"]:
            discount = round(subtotal * 0.10, 2)

        delivery_fee = 0.0 if (subtotal - discount) >= 999 or subtotal >= 999 else 50.0
        total_amount = round(subtotal - discount + delivery_fee, 2)

        import time
        order_id = f"AGRI-{int(time.time()) % 1000000:06d}"

        user_id = session.get("user_id")
        items_summary = ", ".join([f"{it.get('name', 'Product')} x{it.get('qty', 1)}" for it in items[:3]])
        if len(items) > 3:
            items_summary += f" + {len(items)-3} more"

        input_desc = f"Order #{order_id}: {items_summary} | Delivery to: {address}, PIN: {pincode}"
        result_desc = f"Total: ₹{total_amount:.2f} ({payment_method}) | Status: Confirmed for Priority Farm Dispatch"
        log_activity(user_id, "store", input_desc, result_desc)

        return jsonify({
            "success": True,
            "order_id": order_id,
            "customer_name": customer_name,
            "phone": phone,
            "address": address,
            "pincode": pincode,
            "items": items,
            "subtotal": subtotal,
            "discount": discount,
            "delivery_fee": delivery_fee,
            "total_amount": total_amount,
            "payment_method": payment_method,
            "estimated_delivery": "2-3 Business Days (Dispatched via Certified Regional Agri-Logistics)",
            "message": f"Order #{order_id} placed successfully! Your priority farm delivery has been confirmed."
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Error processing order: {str(e)}"}), 500

# -------------------------------------------------------------
# User Authentication Routes
# -------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username_or_email = request.form.get("username_or_email", "").strip()
        password = request.form.get("password", "")

        user, msg = authenticate_user(username_or_email, password)
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash(f"Welcome back, {user['full_name']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash(msg, "error")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        farm_name = request.form.get("farm_name", "").strip()
        farm_location = request.form.get("farm_location", "").strip()
        password = request.form.get("password", "")

        success, msg, user_id = register_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            farm_name=farm_name,
            farm_location=farm_location
        )

        if success:
            session["user_id"] = user_id
            session["username"] = username
            flash(msg, "success")
            return redirect(url_for("dashboard"))
        else:
            flash(msg, "error")

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("index"))

@app.route("/history")
def history_view():
    user_id = session.get("user_id")
    history_records = get_user_history(user_id=user_id, limit=50)
    return render_template("history.html", history=history_records)

@app.route("/uploads/<filename>")
def serve_uploaded_file(filename):
    safe_name = secure_filename(filename)
    return send_from_directory(app.config["UPLOAD_FOLDER"], safe_name)

# -------------------------------------------------------------
# Error Handlers
# -------------------------------------------------------------

@app.errorhandler(404)
def not_found_error(error):
    flash("The requested page does not exist.", "warning")
    return redirect(url_for("index"))

@app.errorhandler(413)
def file_too_large(error):
    flash("Uploaded file exceeds 5MB limit. Please upload a smaller image file.", "error")
    return redirect(url_for("disease_detection"))

@app.errorhandler(500)
def internal_error(error):
    flash("An unexpected server error occurred. Please try again.", "error")
    return redirect(url_for("index"))

# -------------------------------------------------------------
# Main Application Entrypoint
# -------------------------------------------------------------

if __name__ == "__main__":
    print("==================================================")
    print("  Croplytics — Smart Agriculture Assistant Server")
    print("  Running locally on: http://127.0.0.1:5000")
    print("==================================================")
    app.run(host="127.0.0.1", port=5000, debug=True)
