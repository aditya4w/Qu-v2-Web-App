from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000))
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(5), nullable=False, default="₹") 
    date = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"Expense('{self.category}', '{self.amount}')"

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/app', methods=['GET', 'POST'])
def tracker():
    if request.method == 'POST':
        category = request.form['category'] 
        description = request.form['description']
        amount = request.form['amount']
        currency = request.form['currency']
        date_string = request.form['date']

        if not category or not amount:
            return "Category and Amount are required!"

        if date_string:
            date_object = datetime.strptime(date_string, '%Y-%m-%d')
        else:
            date_object = datetime.now()

        new_expense = Expense(
            category=category, 
            description=description, 
            amount=amount, 
            currency=currency,
            date=date_object
        )

        try:
            db.session.add(new_expense)
            db.session.commit()
            return redirect('/app')
        except:
            return "There was an error adding your expense"

    view_mode = request.args.get('view', 'default') 
    expenses = []
    total = 0
    daily_breakdown = {} 

    if view_mode == 'summary':
        expenses = Expense.query.order_by(Expense.date.desc()).all()

    elif view_mode == 'analytics':
        all_data = Expense.query.order_by(Expense.date.desc()).all()
        for e in all_data:
            total += e.amount

            day_str = e.date.strftime('%d-%m-%Y')
            
            if day_str not in daily_breakdown:
                daily_breakdown[day_str] = 0
            
            daily_breakdown[day_str] += e.amount

    return render_template('tracker.html', view=view_mode, expenses=expenses, total=total, daily_breakdown=daily_breakdown)


if __name__ == '__main__':
    with app.app_context():
      db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
