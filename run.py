import os
import tempfile
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- HTML CONTENT (Same as before) ---
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TechStore Checkout</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .error-text { color: red; font-size: 0.9em; }
        .success-msg { color: green; font-weight: bold; }
        .container { max-width: 500px; margin: 0 auto; border: 1px solid #ccc; padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Secure Checkout</h1>
        <div id="cart-summary">
            <h3>Order Summary</h3>
            <div class="item">Gaming Laptop - $1000</div>
            <div class="item">Wireless Mouse - $50</div>
            <hr>
            <p>Total: $<span id="total-price">1050</span></p>
        </div>
        <div class="discount-section">
            <label for="promo_code">Discount Code:</label>
            <input type="text" id="promo_code" name="promo_code" placeholder="Try SAVE20">
            <button id="apply_btn" onclick="applyDiscount()">Apply Code</button>
            <div id="promo_message" class="msg"></div>
        </div>
        <br>
        <form id="checkout_form" onsubmit="event.preventDefault(); validateForm();">
            <label>Email:</label><br>
            <input type="email" id="email_addr" name="email" required>
            <div id="email_error" class="error-text"></div>
            <br>
            <label>Shipping Method:</label><br>
            <input type="radio" name="shipping" id="ship_standard" value="standard" checked onchange="updateShipping(0)">
            <label for="ship_standard">Standard (Free)</label><br>
            <input type="radio" name="shipping" id="ship_express" value="express" onchange="updateShipping(20)">
            <label for="ship_express">Express (+$20)</label>
            <br><br>
            <button type="submit" id="pay_now_btn" style="background-color: green; color: white; padding: 10px 20px; border: none; cursor: pointer;">Pay Now</button>
        </form>
        <div id="payment_status"></div>
    </div>
    <script>
        let baseTotal = 1050;
        let shippingCost = 0;
        let discountMultiplier = 1.0;
        function updateDisplay() {
            const finalTotal = (baseTotal * discountMultiplier) + shippingCost;
            document.getElementById('total-price').innerText = finalTotal.toFixed(0);
        }
        function updateShipping(cost) {
            shippingCost = cost;
            updateDisplay();
        }
        function applyDiscount() {
            const code = document.getElementById('promo_code').value.trim();
            const msg = document.getElementById('promo_message');
            if(code === 'SAVE20') {
                discountMultiplier = 0.8;
                msg.innerText = 'Success: 20% Discount Applied!';
                msg.className = 'success-msg';
                msg.style.color = 'green';
            } else {
                discountMultiplier = 1.0;
                msg.innerText = 'Error: Invalid Coupon Code';
                msg.className = 'error-text';
                msg.style.color = 'red';
            }
            updateDisplay();
        }
        function validateForm() {
            const email = document.getElementById('email_addr').value;
            const errorDiv = document.getElementById('email_error');
            if (!email.includes('@') || !email.includes('.')) {
                errorDiv.innerText = "Please enter a valid email address.";
            } else {
                errorDiv.innerText = "";
                document.getElementById('payment_status').innerText = "Payment Successful!";
                document.getElementById('checkout_form').style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""


def run_visual_test():
    driver = None
    html_file_path = None
    try:
        # 1. Setup
        print("🚀 Setting up test environment...")
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".html", encoding='utf-8') as f:
            f.write(html_content)
            html_file_path = f.name

        driver = webdriver.Chrome()
        driver.maximize_window()

        # 2. Load Page
        print(f"📂 Opening file: {html_file_path}")
        driver.get(f"file:///{html_file_path}")
        time.sleep(1)  # Wait so we can see the page load in the video

        print("\n--- 🎬 STARTING TEST: TC-DC-001 ---")

        # 3. Get Elements
        promo_input = driver.find_element(By.ID, "promo_code")
        apply_btn = driver.find_element(By.ID, "apply_btn")
        total_span = driver.find_element(By.ID, "total-price")
        msg_div = driver.find_element(By.ID, "promo_message")

        # 4. Pre-check
        initial_price = total_span.text
        print(f"ℹ️  Initial Price: ${initial_price}")
        assert initial_price == "1050"

        # 5. Perform Actions (with delays for video)
        print("⌨️  Typing 'SAVE20'...")
        promo_input.send_keys("SAVE20")
        time.sleep(1)  # DELAY FOR DEMO

        print("🖱️  Clicking Apply Button...")
        apply_btn.click()
        time.sleep(1)  # DELAY FOR DEMO

        # 6. Validations
        WebDriverWait(driver, 5).until(EC.text_to_be_present_in_element((By.ID, "total-price"), "840"))

        new_price = total_span.text
        success_msg = msg_div.text

        print(f"✅ Price updated to: ${new_price}")
        assert new_price == "840"

        print(f"✅ Success Message: '{success_msg}'")
        assert "Success" in success_msg

        # Check color
        color = msg_div.value_of_css_property("color")
        if color == "rgba(0, 128, 0, 1)":
            print("✅ Message Color is Green")

        print("\n🎉 --- TEST PASSED SUCCESSFULLY! ---")
        time.sleep(2)  # Pause at the end so the video captures the success state

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
    finally:
        if driver:
            driver.quit()
        if html_file_path and os.path.exists(html_file_path):
            os.remove(html_file_path)


if __name__ == "__main__":
    run_visual_test()