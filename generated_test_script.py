import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# --- Strict Requirement 1 & 2: Use Chrome, normal mode, maximize window ---
# Setup Chrome options
chrome_options = Options()
# chrome_options.add_argument("--headless") # Commented out to ensure NOT headless
chrome_options.add_argument("--start-maximized") # Maximize window

# Create a temporary HTML file for the target HTML content
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
            <h3>User Details</h3>

            <label>Full Name:</label><br>
            <input type="text" id="full_name" name="name" placeholder="John Doe" required><br><br>

            <label>Email:</label><br>
            <input type="email" id="email_addr" name="email" required>
            <div id="email_error" class="error-text"></div>
            <br>

            <label>Address:</label><br>
            <textarea id="address" name="address" placeholder="123 Main St" rows="2" required></textarea><br><br>

            <h3>Shipping Method</h3>
            <input type="radio" name="shipping" id="ship_standard" value="standard" checked onchange="updateShipping(0)">
            <label for="ship_standard">Standard (Free)</label><br>

            <input type="radio" name="shipping" id="ship_express" value="express" onchange="updateShipping(20)">
            <label for="ship_express">Express (+$20)</label>
            <br><br>

            <h3>Payment Method</h3>
            <input type="radio" name="payment" id="pay_cc" value="cc" checked>
            <label for="pay_cc">Credit Card</label><br>
            <input type="radio" name="payment" id="pay_paypal" value="paypal">
            <label for="pay_paypal">PayPal</label>
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
                discountMultiplier = 0.8; // 20% off
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

temp_html_file = "temp_checkout_page.html"
with open(temp_html_file, "w") as f:
    f.write(html_content)

# Initialize the Chrome driver
driver = webdriver.Chrome(options=chrome_options)

try:
    # Navigate to the local HTML file
    driver.get(f"file:///{os.path.abspath(temp_html_file)}")
    # Strict Requirement 4: Add time.sleep(2) after driver.get()
    time.sleep(2)

    print(f"Test Case: TC-005 - Apply 'SAVE20' with leading/trailing spaces (' SAVE20 ')")

    # Step 1: Locate the discount code input field (id="promo_code").
    promo_code_input = driver.find_element(By.ID, "promo_code")

    # Step 2: Enter ' SAVE20 ' (with spaces) into the input field.
    # Strict Requirement 5: Add time.sleep(1) BEFORE every .send_keys()
    time.sleep(1)
    promo_code_input.send_keys(" SAVE20 ")
    print("Entered ' SAVE20 ' into the discount code field.")

    # Step 3: Click the 'Apply Code' button (id="apply_btn").
    apply_btn = driver.find_element(By.ID, "apply_btn")
    # Strict Requirement 5: Add time.sleep(1) BEFORE every .click()
    time.sleep(1)
    apply_btn.click()
    print("Clicked the 'Apply Code' button.")

    # --- Verify Expected Result ---
    # Expected Result 1: The total price (id="total-price") should remain $1050.
    total_price_element = driver.find_element(By.ID, "total-price")
    actual_total_price = total_price_element.text
    expected_total_price = "1050"

    assert actual_total_price == expected_total_price, \
        f"Assertion Failed: Expected total price to be '{expected_total_price}', but got '{actual_total_price}'."
    print(f"Total price verification passed. Actual: ${actual_total_price}, Expected: ${expected_total_price}.")

    # Expected Result 2: The message div (id="promo_message") should display 'Error: Invalid Coupon Code'.
    promo_message_element = driver.find_element(By.ID, "promo_message")
    actual_promo_message = promo_message_element.text
    expected_promo_message = "Error: Invalid Coupon Code"

    assert actual_promo_message == expected_promo_message, \
        f"Assertion Failed: Expected promo message to be '{expected_promo_message}', but got '{actual_promo_message}'."
    print(f"Promo message text verification passed. Actual: '{actual_promo_message}', Expected: '{expected_promo_message}'.")

    # Expected Result 3: The message div (id="promo_message") should have red text (class 'error-text').
    actual_promo_message_class = promo_message_element.get_attribute("class")
    expected_class_part = "error-text"

    assert expected_class_part in actual_promo_message_class, \
        f"Assertion Failed: Expected promo message class to contain '{expected_class_part}', but got '{actual_promo_message_class}'."
    print(f"Promo message class verification passed. Class: '{actual_promo_message_class}'.")

    print("\nTC-005: All assertions passed!")

except Exception as e:
    print(f"\nTC-005: Test Failed! {e}")

finally:
    # Add a final sleep to observe the result
    time.sleep(3)
    driver.quit()
    # Clean up the temporary HTML file
    if os.path.exists(temp_html_file):
        os.remove(temp_html_file)