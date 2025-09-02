# Wasted

*Track your fridge, reduce food waste, and cook smarter.*

****

## Overview

**Wasted** is a lightweight web app built with Streamlit and SQLite, designed to help users track food inventory, visualize expiry trends, and receive recipe suggestions before food goes bad.

Key features include:
- User registration and login with secure password hashing
- Add, view, and delete food items (category, dates, quantity, unit, price)
- Visual cues for expiring or expired items
- Waste statistics and estimated financial loss
- Recipe suggestions via the Spoonacular API

---

## Requirements

Before running the application, ensure the following are installed:

- Python 3.9+
- Pip (Python package manager)

---

## Quick Start

1. Clone the repository:
   
   ```bash
    git clone https://github.com/unibo-dtm-se-2425-Wasted/artifact.git
    cd artifact
    ```

2. Install dependencies:
    
    ```bash
    pip install -r requirements.txt
    ```

3.  Run the app:

    ```bash
    streamlit run app.py
    ```
    Then open your browser at http://localhost:8501.

---

## Usage

### Register an Account
Users can create an account with a unique username and password.  
Passwords are stored securely using hashing.  

### Login
Log in with your credentials to access your personal food inventory.  

### Manage Food Items
Add food items with details such as name, category, purchase and expiry dates, quantity, and price.  
You can view them in a dashboard, delete them when consumed, or track their status (OK, Expiring Soon, Expired).  

### View Waste Statistics
The app calculates the number of expired items, percentage of wasted food, and estimated financial loss.  

### Get Recipe Suggestions
When items are close to expiration, the app suggests recipes that help reuse those ingredients.  

---


## Technologies Used

- **Backend:** Python (Streamlit framework)  
- **Frontend:** Streamlit components (HTML/CSS generated)  
- **Database:** SQLite (via Python’s `sqlite3` library)  
- **External API:** Spoonacular (recipe suggestions)  

---

## Future Enhancements

- Add notifications (e.g., email or push) when items are close to expiration.  
- Implement multi-user support with roles (e.g., family/shared fridge).  
- Add integration with barcode scanning to simplify item insertion.  
- Enhance the dashboard with richer data visualizations.  
- Extend recipe recommendation with more advanced AI-based suggestions.  

---

## License 

This project is licensed under the terms of the **Apache License 2.0**.  
See the [LICENSE](LICENSE) file for the full text.

---
## Contact

For questions or feedback, reach out:

- [Sara Marrocolo](mailto:sara.marrocolo@studio.unibo.it)
- [Viola Morgia](mailto:viola.morgia@studio.unibo.it)
- [Vu Ngoc Mai Nguyen](mailto:vungocngocmai.nguyen@studio.unibo.it)


