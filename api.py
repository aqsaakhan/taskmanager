from flask import jsonify, request
from flask_login import current_user, login_required

def init_api(api, app, db, Todo):
    @api.route('/api/tasks', methods=['GET'])
    @login_required
    def get_tasks():
        tasks = Todo.query.filter_by(user_id=current_user.id).all()
        return jsonify([{
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'completed': task.completed
        } for task in tasks])

    @api.route('/api/tasks', methods=['POST'])
    @login_required
    def create_task():
        data = request.json
        new_task = Todo(title=data['title'], description=data.get('description', ''), user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        return jsonify({
            'id': new_task.id,
            'title': new_task.title,
            'description': new_task.description,
            'completed': new_task.completed
        }), 201

    @api.route('/api/tasks/<int:id>', methods=['PUT'])
    @login_required
    def update_task(id):
        task = Todo.query.get_or_404(id)
        if task.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        data = request.json
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.completed = data.get('completed', task.completed)
        db.session.commit()
        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'completed': task.completed
        })

    @api.route('/api/tasks/<int:id>', methods=['DELETE'])
    @login_required
    def delete_task(id):
        task = Todo.query.get_or_404(id)
        if task.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        db.session.delete(task)
        db.session.commit()
        return '', 204