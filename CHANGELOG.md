# Changelog

All notable changes to this project are documented in this file.  
Development milestones are listed prior to the first official release.

## Development Milestones

### 0.1.0 
- Initial code base with core functionality:
  - Add food items
  - Fetch recipes from Spoonacular
  - Basic waste statistics
- No user interface yet; commands run in backend scripts.

### 0.2.0 
- Improved table visualization for food items.
- Added ability to delete food items from inventory.

### 0.3.0 
- User interface enhancements in Streamlit.
- Added filtering options for food items based on status.

### 0.4.0 
- Added user registration and login.
- Full integration of user-specific food inventories.

## First release [1.0.0] 
- First official release of Wasted.
- Combines all previous milestones into a deployable Streamlit app.
- Features:
  - User registration and login with secure password hashing
  - Add, view, and delete food items (category, purchase & expiry dates, quantity, unit, price)
  - Visual cues for expiring or expired items
  - Waste statistics and estimated financial loss
  - Recipe suggestions via Spoonacular API
