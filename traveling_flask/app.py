from flask import Flask, jsonify, redirect,render_template, request,url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookdatabase.db'
db = SQLAlchemy(app)



# 定義數據庫模型
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    rooms = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)

# 其他應用程序配置和路由等...
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book_room', methods=['POST'])
def book_room():
    if request.method == 'POST':
        date = request.form['date']
        print(f"Received date string: {date}")
        rooms = request.form['rooms']
        name = request.form['name']
        email = request.form['email']
        # date_obj = datetime.strptime(date, '%m/%d/%Y')
        date_obj = datetime.strptime(date, '%Y-%m-%d')  #.date()
        # current_date = datetime.now()
        #print(date_obj.type())
        date_str=str(date_obj)
        # if date_obj < current_date:
        #     return "不能选择过去的日期！"
        print(f"Parsed date object: {date_obj}")
        # 找到日期等于date_obj的行
        booked_rooms = Booking.query.filter_by(date=date)
        a=str(Booking.query.filter_by(date=date_obj).count())
        print("筆數"+a)
        if booked_rooms is None:
            total_rooms_sum = 0
        # 使用SUM函数来计算rooms值的总和
        else:
            total_rooms_sum = booked_rooms.with_entities(func.sum(Booking.rooms)).scalar()
        # if total_rooms_sum is None:
        #     total_rooms_sum = 0
        if total_rooms_sum is None:
            total_rooms_sum = 0
        remaining_rooms = 3 - total_rooms_sum  #假設3間
        if remaining_rooms<int(rooms):
            return render_template('index.html', mes=f"房間數不足，剩下 {remaining_rooms} 間")
        else:
            booking = Booking(date=date_obj, rooms=rooms, name=name, email=email)
            # booking = Booking(date=date, rooms=rooms, name=name, email=email)
            db.session.add(booking)
            db.session.commit()

            return redirect(url_for('success',email=email))

# 新的路由处理函数，用于获取特定日期的已订房间数量
# @app.route('/get_booked_rooms', methods=['POST'])
# def get_booked_rooms():
#     if request.method == 'POST':
#         selected_date = request.form.get('selected_date')
#         if selected_date:
#             # 将选定日期的字符串解析为日期对象
#             date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
#             # 查询特定日期的已订房间数量
#             booked_rooms = Booking.query.filter_by(date=date_obj).count()
#             # 计算剩余房间数量
#             remaining_rooms = 3 - booked_rooms
#             return jsonify(str(remaining_rooms))
# @app.route('/get_booked_rooms', methods=['POST'])
# def get_booked_rooms():
#     if request.method == 'POST':
#         selected_date = request.form.get('selected_date')
#         if selected_date:
#             # 将选定日期的字符串解析为日期对象
#             date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
#             # 查询特定日期的已订房间数量
#             booked_rooms = Booking.query.filter_by(date=date_obj).count()
#             # 计算剩余房间数量
#             remaining_rooms = 3 - booked_rooms
#             print(str(remaining_rooms))
#             return jsonify({'remaining_rooms': remaining_rooms})

@app.route('/success/<email>')
def success(email):
    bookings = Booking.query.filter_by(email=email).all()
    return render_template('my_bookings.html', bookings=bookings, email=email, mes="訂房成功！")  #"訂房成功！"

# @app.route('/my_bookings/<email>')
# def my_bookings(email):
#     # 查询特定用户的所有预订信息
#     bookings = Booking.query.filter_by(email=email).all()
#     return render_template('my_bookings.html', bookings=bookings)

@app.route('/edit_booking/<int:id>', methods=['GET', 'POST'])
def edit_booking(id):
    booking = Booking.query.get(id)
    
    if request.method == 'POST':
        # 更新现有预订信息
        date_str = request.form['date']
        # date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        
        rooms = request.form['rooms']
        name = request.form['name']
        email = request.form['email']
        
        booking.date = date_obj
        
        booking.rooms = rooms
        booking.name = name
        booking.email = email
        
        db.session.commit()
        #return redirect(url_for('my_bookings', email=email))  #會到輸入頁面
        # 直接渲染my_bookings页面，并传递用户的电子邮件参数
        # print(email+"edit")
        bookings = Booking.query.filter_by(email=email).all()
        
        return render_template('my_bookings.html', bookings=bookings, email=email)
    
    return render_template('edit_booking.html', booking=booking)

@app.route('/cancel_booking/<int:id>')
def cancel_booking(id):
    booking = Booking.query.get(id)
    #email=booking.email
    if booking:
        # 删除订单
        db.session.delete(booking)
        db.session.commit()
    return redirect(url_for('my_bookings', email=booking.email))   #email=email

@app.route('/my_bookings', methods=['GET', 'POST'])
def my_bookings():
    if request.method == 'POST':
        # email = request.form['email']    
        print("post")
        # print(email)

        email = request.form.get('email')
        if email:
            bookings = Booking.query.filter_by(email=email).all()
            print("1")
            # print(email)
            print(bookings)
            return render_template('my_bookings.html', bookings=bookings, email=email)
        email = request.args.get('email')
        if email:
            bookings = Booking.query.filter_by(email=email).all()
            print(bookings)
            print("2")
            return render_template('my_bookings.html', bookings=bookings, email=email)
    elif request.method == 'GET':
        # 如果是GET请求，检查是否存在电子邮件参数
        print("post")
        email = request.args.get('email')
        if email:
            # 查询特定用户的所有预订信息
            bookings = Booking.query.filter_by(email=email).all()
            print(bookings)
            print("3")
            return render_template('my_bookings.html', bookings=bookings, email=email)
    # return render_template('my_bookings.html', bookings=[], email=None)
    # else:
    return render_template('my_bookings_search.html')   #另一種方法

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

