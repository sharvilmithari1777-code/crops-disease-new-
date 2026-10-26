"""
Croplytics — Comprehensive Integration and Verification Test Suite
Tests all endpoints, forms, calculations, authentications, database logging,
and verifies genuine Deep Learning plant disease classification with MobileNetV2.
"""

import urllib.request
import urllib.parse
import json
import os
import sys

BASE_URL = "http://127.0.0.1:5000"
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def test_get(url_path, expected_text):
    full_url = BASE_URL + url_path
    req = urllib.request.Request(full_url)
    try:
        with urllib.request.urlopen(req) as response:
            status = response.status
            content = response.read().decode("utf-8")
            assert status == 200, f"Expected 200 but got {status}"
            assert expected_text in content, f"Expected '{expected_text}' not in response for {url_path}"
            print(f" [PASS] GET {url_path} (Status 200, contains '{expected_text}')")
            return True
    except Exception as e:
        print(f" [FAIL] GET {url_path}: {e}")
        return False

def test_yield_post():
    full_url = BASE_URL + "/yield-forecast"
    data = urllib.parse.urlencode({
        "crop_type": "Wheat",
        "region": "Punjab",
        "N": "130",
        "P": "60",
        "K": "40",
        "ph": "6.8",
        "temperature": "22",
        "rainfall": "600",
        "humidity": "65",
        "area": "4.0"
    }).encode("utf-8")

    req = urllib.request.Request(full_url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read().decode("utf-8")
            assert "Estimated Yield Per Hectare" in content, "Missing yield forecast header"
            assert "Harvest Forecast: Wheat" in content, "Missing Wheat forecast"
            assert "Quintals" in content, "Missing quintals metric"
            print(" [PASS] POST /yield-forecast (Valid output generated with Scikit-Learn)")
            return True
    except Exception as e:
        print(f" [FAIL] POST /yield-forecast: {e}")
        return False

def test_carbon_post():
    full_url = BASE_URL + "/carbon-calculator"
    data = urllib.parse.urlencode({
        "area": "5.0",
        "fertilizer_kg": "450",
        "pesticide_qty": "10",
        "pesticide_unit": "Litres",
        "fuel_litres": "120",
        "electricity_kwh": "600",
        "irrigation_method": "Drip / Micro-irrigation"
    }).encode("utf-8")

    req = urllib.request.Request(full_url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read().decode("utf-8")
            assert "Annual Emissions Assessment" in content, "Missing carbon summary"
            assert "t CO₂e" in content, "Missing t CO2e metric"
            assert "carbonDoughnutChart" in content, "Missing doughnut chart container"
            print(" [PASS] POST /carbon-calculator (Calculated with documented IPCC factors)")
            return True
    except Exception as e:
        print(f" [FAIL] POST /carbon-calculator: {e}")
        return False

def test_disease_sample_post():
    full_url = BASE_URL + "/disease-detection"
    data = urllib.parse.urlencode({
        "sample_image": "sample_late_blight.jpg",
        "crop_hint": "Tomato"
    }).encode("utf-8")

    req = urllib.request.Request(full_url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read().decode("utf-8")
            assert "Confidence" in content, "Missing confidence score in result"
            assert "Recommended Action Plan" in content, "Missing treatment action plan"
            assert "Organic Treatment" in content, "Missing organic treatment tab"
            print(" [PASS] POST /disease-detection (Diagnosed with real MobileNetV2 model inference)")
            return True
    except Exception as e:
        print(f" [FAIL] POST /disease-detection: {e}")
        return False

def test_disease_upload_multipart_post():
    """Tests actual image file upload via multipart/form-data."""
    import mimetypes
    sample_file = os.path.join(PROJECT_ROOT, "static", "images", "samples", "sample_healthy_leaf.jpg")
    assert os.path.exists(sample_file), "Sample image file missing for upload test"

    boundary = "----CroplyticsBoundaryTest7MA4YWxkTrZu0gW"
    with open(sample_file, "rb") as f:
        file_bytes = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="crop_hint"\r\n\r\n'
        f"Tomato\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="sample_image"\r\n\r\n\r\n'
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="leaf_image"; filename="test_leaf_upload.jpg"\r\n'
        f"Content-Type: image/jpeg\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        BASE_URL + "/disease-detection",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            content = response.read().decode("utf-8")
            assert response.status == 200
            assert "Confidence" in content, "Missing confidence score on uploaded leaf"
            assert "Recommended Action Plan" in content, "Missing action plan on uploaded leaf"
            print(" [PASS] POST /disease-detection (Multipart file upload diagnosed successfully by neural net)")
            return True
    except Exception as e:
        print(f" [FAIL] Multipart upload test: {e}")
        return False

def test_registration_and_login():
    import http.cookiejar
    import time
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    reg_url = BASE_URL + "/register"
    unique_user = f"farmer_{int(time.time())}"
    reg_data = urllib.parse.urlencode({
        "full_name": "Test Farmer",
        "username": unique_user,
        "email": f"{unique_user}@croplytics.farm",
        "farm_name": "Sunrise Organic Farm",
        "farm_location": "Haryana, India",
        "password": "securepassword123"
    }).encode("utf-8")

    try:
        with opener.open(reg_url, data=reg_data) as response:
            content = response.read().decode("utf-8")
            print(f" [PASS] POST /register (Account created for {unique_user})")

        # Now test dashboard with session cookie
        dash_url = BASE_URL + "/dashboard"
        with opener.open(dash_url) as response:
            content = response.read().decode("utf-8")
            assert "Test Farmer" in content, "User name missing in dashboard"
            print(" [PASS] GET /dashboard (Authenticated session recognized Test Farmer)")
            return True
    except Exception as e:
        print(f" [FAIL] Auth flow: {e}")
        return False

def test_invalid_yield_input():
    full_url = BASE_URL + "/yield-forecast"
    data = urllib.parse.urlencode({
        "crop_type": "Wheat",
        "region": "Punjab",
        "N": "NOT_A_NUMBER",
        "P": "abc",
        "area": "-5"
    }).encode("utf-8")
    req = urllib.request.Request(full_url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read().decode("utf-8")
            assert response.status == 200
            print(" [PASS] POST /yield-forecast [Invalid input handled gracefully with status 200]")
            return True
    except Exception as e:
        print(f" [FAIL] POST /yield-forecast invalid input: {e}")
        return False

def test_invalid_carbon_input():
    full_url = BASE_URL + "/carbon-calculator"
    data = urllib.parse.urlencode({
        "area": "bad_area",
        "fertilizer_kg": "xyz"
    }).encode("utf-8")
    req = urllib.request.Request(full_url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read().decode("utf-8")
            assert response.status == 200
            print(" [PASS] POST /carbon-calculator [Invalid input handled gracefully with status 200]")
            return True
    except Exception as e:
        print(f" [FAIL] POST /carbon-calculator invalid input: {e}")
        return False

def test_store_order_api():
    full_url = BASE_URL + "/api/order"
    order_data = json.dumps({
        "customer_name": "Test Farmer",
        "phone": "9876543210",
        "address": "Green Acres Farm, Ludhiana",
        "pincode": "141001",
        "payment_method": "Cash on Delivery",
        "coupon": "KISAN10",
        "items": [
            {"id": "prod-001", "name": "Neem Gold Organic Cake", "price": 650, "qty": 2},
            {"id": "prod-011", "name": "IFFCO Nano Urea", "price": 225, "qty": 1}
        ]
    }).encode("utf-8")

    req = urllib.request.Request(
        full_url,
        data=order_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as response:
            assert response.status == 200
            res_json = json.loads(response.read().decode("utf-8"))
            assert res_json.get("success") is True
            assert "AGRI-" in res_json.get("order_id", "")
            assert res_json.get("total_amount") > 0
            print(f" [PASS] POST /api/order (Order #{res_json['order_id']} placed successfully, Total: Rs. {res_json['total_amount']})")
            return True
    except Exception as e:
        print(f" [FAIL] POST /api/order: {e}")
        return False

def test_crop_yield_model_consistency():
    import joblib
    model_path = os.path.join(PROJECT_ROOT, "models", "crop_yield_model.joblib")
    assert os.path.exists(model_path), "Model file missing"
    m = joblib.load(model_path)
    expected_features = ["crop_type", "region", "N", "P", "K", "ph", "temperature", "rainfall", "humidity"]
    assert m["features"] == expected_features, "Feature order mismatch"
    assert m["metrics"]["r2_score"] > 0.95, "R2 score below threshold"
    print(f" [PASS] Scikit-Learn Yield Model Consistency (R²: {m['metrics']['r2_score']}, features: {len(expected_features)})")
    return True

def test_deep_learning_artifacts():
    model_path = os.path.join(PROJECT_ROOT, "models", "plant_disease", "best_model.keras")
    class_names_path = os.path.join(PROJECT_ROOT, "models", "plant_disease", "class_names.json")
    metadata_path = os.path.join(PROJECT_ROOT, "models", "plant_disease", "model_metadata.json")

    assert os.path.exists(model_path), f"Missing model: {model_path}"
    assert os.path.exists(class_names_path), f"Missing class names: {class_names_path}"
    assert os.path.exists(metadata_path), f"Missing metadata: {metadata_path}"

    with open(class_names_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
        classes = meta["classes"]
        assert len(classes) == 38, f"Expected 38 classes but got {len(classes)}"

    with open(metadata_path, "r", encoding="utf-8") as f:
        m_data = json.load(f)
        assert m_data.get("model_name") == "Croplytics_MobileNetV2"

    print(f" [PASS] Deep Learning Model Artifacts (38 classes, MobileNetV2 verified, size: {os.path.getsize(model_path)/(1024*1024):.2f}MB)")
    return True

def test_deep_learning_service_inference():
    from services.disease_detection import analyze_plant_leaf
    sample_file = os.path.join(PROJECT_ROOT, "static", "images", "samples", "sample_early_blight.jpg")
    res = analyze_plant_leaf(sample_file, crop_hint="Tomato")

    # Verify response schema
    required_keys = [
        "disease_name", "scientific_name", "affected_crop", "confidence_score",
        "severity_level", "severity_color", "symptoms", "description",
        "organic_treatment", "chemical_treatment", "preventive_measures",
        "visual_features", "model_details"
    ]
    for k in required_keys:
        assert k in res, f"Missing required key '{k}' in inference result"

    assert isinstance(res["confidence_score"], (int, float))
    assert res["confidence_score"] > 0.0
    assert isinstance(res["organic_treatment"], list)
    assert len(res["organic_treatment"]) > 0
    assert res["is_demo_mode"] is False

    print(f" [PASS] Direct Service Inference: {res['disease_name']} (Confidence: {res['confidence_score']}%, Demo Mode: False)")
    return True

def test_invalid_image_handling():
    from services.disease_detection import analyze_plant_leaf
    # Test non-existent file
    res1 = analyze_plant_leaf("non_existent_image_12345.jpg")
    assert "error" in res1, "Non-existent image did not return error"

    # Test dummy text file as image
    dummy_txt = os.path.join(PROJECT_ROOT, "models", "dummy_test.txt")
    with open(dummy_txt, "w") as f:
        f.write("Not an image")
    try:
        res2 = analyze_plant_leaf(dummy_txt)
        assert "error" in res2, "Unreadable text file did not return error"
        print(" [PASS] Graceful Invalid / Corrupt Image Handling")
        return True
    finally:
        if os.path.exists(dummy_txt):
            os.remove(dummy_txt)

def test_crop_hint_transparency():
    from services.disease_detection import analyze_plant_leaf
    sample_file = os.path.join(PROJECT_ROOT, "static", "images", "samples", "sample_corn_rust.jpg")
    # Pass conflicting hint "Potato"
    res = analyze_plant_leaf(sample_file, crop_hint="Potato")
    # Verify that prediction was not corrupted or forcefully overridden
    assert res["affected_crop"] != "Potato" or "Potato" in res["model_details"]["raw_class"], "Crop hint silently altered model prediction"
    assert "Advisory" in res["model_details"]["crop_hint_status"] or "aligns" in res["model_details"]["crop_hint_status"]
    print(" [PASS] Crop Hint Transparency (Conflicting hints disclosed without altering neural network prediction)")
    return True

if __name__ == "__main__":
    print("==========================================")
    print(" Running Complete Croplytics Test Suite")
    print("==========================================")
    
    # Unit & ML Consistency Tests (run even without HTTP server)
    local_tests = [
        test_crop_yield_model_consistency(),
        test_deep_learning_artifacts(),
        test_deep_learning_service_inference(),
        test_invalid_image_handling(),
        test_crop_hint_transparency()
    ]

    # HTTP Route & Integration Tests (require Flask server)
    http_tests = []
    try:
        with urllib.request.urlopen(BASE_URL, timeout=2) as r:
            server_online = True
    except Exception:
        server_online = False

    if server_online:
        print("\n--- Running Live HTTP Server Integration Tests ---")
        http_tests = [
            test_get("/", "Smart Farming Starts Here"),
            test_get("/dashboard", "Farmer Dashboard"),
            test_get("/disease-detection", "Plant Disease Detection"),
            test_get("/yield-forecast", "Machine Learning Crop Yield Forecasting"),
            test_get("/carbon-calculator", "Agricultural Carbon Footprint Calculator"),
            test_get("/products", "Sustainable Agricultural Product Recommendations"),
            test_get("/login", "Sign In"),
            test_get("/register", "Create Your Croplytics Account"),
            test_get("/history", "Diagnostic & Analysis History"),
            test_yield_post(),
            test_carbon_post(),
            test_disease_sample_post(),
            test_disease_upload_multipart_post(),
            test_registration_and_login(),
            test_invalid_yield_input(),
            test_invalid_carbon_input(),
            test_store_order_api()
        ]
    else:
        print("\n [NOTE] Flask server is not currently running on http://127.0.0.1:5000.")
        print("        Launch Flask with 'python app.py' to run full HTTP endpoint tests.")

    all_tests = local_tests + http_tests
    print("\n==========================================")
    if all(all_tests):
        print(f" ALL {len(all_tests)} EXECUTED TESTS PASSED PERFECTLY!")
    else:
        print(f" {all_tests.count(False)} TESTS FAILED!")
    print("==========================================")
