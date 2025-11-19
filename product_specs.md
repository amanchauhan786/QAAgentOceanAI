# Product Specifications and Business Rules

## 1. Discount Codes
The system supports the following promotional logic:
- **Code "SAVE20"**: Applies a **20% discount** to the base cart total.
- **Invalid Codes**: Any code other than "SAVE20" must display an error message: "Error: Invalid Coupon Code".
- **Success Message**: Valid codes must display "Success: 20% Discount Applied!".

## 2. Shipping Logic
- **Standard Shipping**: Costs **$0** (Free).
- **Express Shipping**: Adds a flat fee of **$20** to the total order value.
- The Total Price must update immediately when a shipping option is selected.

## 3. Payment Flow
- The "Pay Now" button must be **Green**.
- Upon successful form submission, the form should disappear and display "Payment Successful!".