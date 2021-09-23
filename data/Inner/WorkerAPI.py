import datetime
from data import db_session
from data.Inner.AuditlogAPI import add_auditlog
from data.worker import Worker
from data.Inner.main_file import raise_error, check_admin_status


def find_by_id(id, session):
    worker = session.query(Worker).get(id)
    if not worker:
        return raise_error(f"Сотрудник не найден", session), 1
    return worker, session


def get_worker_list():
    session = db_session.create_session()
    workers = session.query(Worker).all()
    session.close()
    return [item.to_dict(only=('id', 'name', 'image', 'profession', 'description', 'phone', 'email')) for item in workers]


def edit_worker(worker_id, args):
    if not all(args[key] is not None for key in ['admin_email', 'action']):
        return raise_error('Пропущены некоторые важные аргументы')
    admin, session = check_admin_status(args['admin_email'])
    worker, session = find_by_id(worker_id, session)
    if type(worker) == dict:
        session.close()
        return worker
    if args['action'] == "get":
        session.close()
        return worker.to_dict(only=('id', 'name', 'image', 'profession', 'description', 'phone', 'email'))
    elif args['action'] == 'delete':
        session.delete(worker)
        session.commit()
        add_auditlog("Удаление", f"Админ {admin.name} {admin.surname} удаляет сотрудник {worker.number}", admin,
                     datetime.datetime.now())
        session.close()
        return {"success": f"Сотрудник {worker.number} успешно удалён"}
    elif args['action'] == 'put':
        count = 0
        worker_dict = worker.to_dict(only=('name', 'image', 'profession', 'description', 'phone', 'email'))
        keys = list(filter(lambda key: args[key] is not None and key in worker_dict and args[key] != worker_dict[key], args.keys()))
        for key in keys:
            count += 1
            if key == 'name':
                if session.query(Worker).filter(Worker.name == args['name']).first():
                    raise_error("Этот сотрудник уже существует", session)
                worker.name = args["name"]
            if key == 'image':
                worker.image = args["image"]
            if key == 'profession':
                worker.profession = args["profession"]
            if key == 'description':
                worker.description = args["description"]
            if key == 'phone':
                worker.phone = args["phone"]
            if key == 'email':
                worker.email = args["email"]
        if count == 0:
            return raise_error("Пустой запрос", session)
        worker_dict_2 = worker.to_dict(only=('name', 'image', 'profession', 'description', 'phone', 'email'))
        list_chang = [f'изменяет {key} с {worker_dict[key]} на {worker_dict_2[key]}' for key in keys]
        session.commit()
        add_auditlog("Изменение", f"Админ {admin.name} {admin.surname} изменяет сотрудника {worker.number}:"
                                  f" {', '.join(list_chang)}", admin, datetime.datetime.now())
        session.close()
        return {"success": f"Сотрудник {worker.number} успешно изменён"}
    return raise_error("Неизвестный метод", session)


def create_worker(args):
    if not all(args[key] is not None for key in ['name', 'image', 'profession', 'description', 'phone', 'email', 'admin_email']):
        return raise_error('Пропущены некоторые аргументы, необходимые для добавления нового примера работы')
    admin, session = check_admin_status(args['admin_email'])
    if session.query(Worker).filter(Worker.link == args['link']).first():
        return raise_error("Этот сотрудник уже существует", session)
    new_worker = Worker()
    new_worker.name = args["name"]
    new_worker.image = args["image"]
    new_worker.profession = args["profession"]
    new_worker.description = args["description"]
    new_worker.phone = args["phone"]
    new_worker.email = args["email"]
    session.add(new_worker)
    session.commit()
    add_auditlog("Создание", f"Админ {admin.name} {admin.surname} добавляет сотрудника {new_worker.number}: {new_worker.to_dict(only=('id', 'name', 'image', 'profession', 'description', 'phone', 'email'))}",
                 admin, datetime.datetime.now())
    session.close()
    return {'success': f'Сотрудник {new_worker.number} создан'}
