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
python -m venv venv<br>
source venv/bin/activate  # On Windows: venv\Scripts\activate

* Install Dependencies:
pip install -r requirements.txt

* Initialize the Database:
Create the SQLite database (app.db) by running the initialization script (if provided) or manually creating the users and predictions tables:
<br>
CREATE TABLE users (<br>
    id INTEGER PRIMARY KEY AUTOINCREMENT,<br>
    username TEXT UNIQUE NOT NULL,<br>
    password_hash TEXT NOT NULL<br>
);<br>
CREATE TABLE predictions (<br>
    id INTEGER PRIMARY KEY AUTOINCREMENT,<br>
    user_id INTEGER,<br>
    credit_score REAL,<br>
    geography TEXT,<br>
    gender TEXT,<br>
    age REAL,<br>
    tenure REAL,<br>
    balance REAL,<br>
    num_products INTEGER,<br>
    has_cr_card TEXT,<br>
    is_active TEXT,<br>
    estimated_salary REAL,<br>
    prediction INTEGER,<br>
    probability REAL,<br>
    FOREIGN KEY (user_id) REFERENCES users (id)<br>
);<br>

* Model Files:
The repository may exclude model.pkl, scaler.pkl, and geography_encoder.pkl due to file size limits.<br>
To generate these,use the training script (e.g., train_model.py) with your dataset.<br>
  
Example steps:
python utils/preprocess.py<br>
Ensure scikit-learn is used to train a model and save StandardScaler and LabelEncoder objects.<br>

* Run the Application:
python app.py<br>
Open http://localhost:5000 in your browser.<br>

Usage:
* Register: Create an account at http://localhost:5000/register.
* Login: Sign in at http://localhost:5000/login.
* Dashboard: View statistics and a churn vs. stay chart at http://localhost:5000/home.
* Predict: Enter customer details at http://localhost:5000/predict to get churn predictions.
