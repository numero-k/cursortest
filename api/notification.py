from flask import render_template, session, redirect, url_for, flash
from models.database import get_db
from . import notification_bp
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요합니다.')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@notification_bp.route('/list')
@login_required
def list_notifications():
    db = get_db()
    notifications = db.execute('''
        SELECT n.*, u.name as sender_name
        FROM notifications n
        JOIN users u ON n.sender_id = u.id
        WHERE n.receiver_id = ?
        ORDER BY n.created DESC
    ''', (session['user_id'],)).fetchall()
    
    return render_template('notification/list.html', notifications=notifications)

@notification_bp.route('/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_as_read(notification_id):
    db = get_db()
    notification = db.execute('''
        SELECT * FROM notifications 
        WHERE id = ? AND receiver_id = ?
    ''', (notification_id, session['user_id'])).fetchone()
    
    if not notification:
        flash('알림이 존재하지 않습니다.')
        return redirect(url_for('notification.list_notifications'))
    
    db.execute('''
        UPDATE notifications 
        SET is_read = 1 
        WHERE id = ?
    ''', (notification_id,))
    db.commit()
    
    return redirect(url_for('notification.list_notifications'))

@notification_bp.route('/all/read', methods=['POST'])
@login_required
def mark_all_as_read():
    db = get_db()
    db.execute('''
        UPDATE notifications 
        SET is_read = 1 
        WHERE receiver_id = ? AND is_read = 0
    ''', (session['user_id'],))
    db.commit()
    
    return redirect(url_for('notification.list_notifications')) 