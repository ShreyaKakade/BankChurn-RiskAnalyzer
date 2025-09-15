**ChurnPredict** : 
A Flask-based web application for predicting customer churn using machine learning. The app provides user authentication, a dashboard with prediction statistics and visualizations, and a form to predict churn based on customer data.

Features:
* User Authentication: Secure registration and login system.
* Dashboard: Displays total users, predictions, user-specific predictions, average credit score, average balance, and a bar chart of churn vs. stay outcomes.
* Churn Prediction: Input customer details (e.g., Credit Score, Geography, Age) to predict churn probability.
* Responsive UI: Built with Bootstrap 5.3, Font Awesome, and a custom color palette for a professional, modern look.
* Data Persistence: Stores user data and predictions in a SQLite database (app.db).

Setup Instructions:
* Clone the Repository:
git clone https://github.com/your-username/ChurnPredict.git<br>
cd ChurnPredict

* Create a Virtual Environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

* Install Dependencies:
pip install -r requirements.txt

* Initialize the Database:
Create the SQLite database (app.db) by running the initialization script (if provided) or manually creating the users and predictions tables:

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    credit_score REAL,
    geography TEXT,
    gender TEXT,
    age REAL,
    tenure REAL,
    balance REAL,
    num_products INTEGER,
    has_cr_card TEXT,
    is_active TEXT,
    estimated_salary REAL,
    prediction INTEGER,
    probability REAL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

* Model Files:
The repository may exclude model.pkl, scaler.pkl, and geography_encoder.pkl due to file size limits. To generate these:
   Use the training script (e.g., train_model.py) with your dataset.
  
Example steps:
python utils/preprocess.py
Ensure scikit-learn is used to train a model and save StandardScaler and LabelEncoder objects.

* Run the Application:
python app.py
Open http://localhost:5000 in your browser.

Usage
* Register: Create an account at http://localhost:5000/register.
* Login: Sign in at http://localhost:5000/login.
* Dashboard: View statistics and a churn vs. stay chart at http://localhost:5000/home.
* Predict: Enter customer details at http://localhost:5000/predict to get churn predictions.
