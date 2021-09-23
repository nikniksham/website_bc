import datetime
from data import db_session
from data.Inner.AuditlogAPI import add_auditlog
from data.text import Text
from data.Inner.main_file import raise_error, check_admin_status


def find_by_id(id, session):
    text = session.query(Text).get(id)
    if not text:
        return raise_error(f"Текст не найден", session), 1
    return text, session


def get_text_list():
    session = db_session.create_session()
    texts = session.query(Text).all()
    session.close()
    return [item.to_dict(only=('id', 'position', 'name', 'body')) for item in texts]


def edit_text(text_id, args):
    if not all(args[key] is not None for key in ['admin_email', 'action']):
        return raise_error('Пропущены некоторые важные аргументы')
    admin, session = check_admin_status(args['admin_email'])
    text, session = find_by_id(text_id, session)
    if type(text) == dict:
        session.close()
        return text
    if args['action'] == "get":
        session.close()
        return text.to_dict(only=('id', 'position', 'name', 'body'))
    elif args['action'] == 'delete':
        session.delete(text)
        session.commit()
        add_auditlog("Удаление", f"Админ {admin.name} {admin.surname} удаляет текст {text.number}", admin,
                     datetime.datetime.now())
        session.close()
        return {"success": f"Текст {text.number} успешно удалён"}
    elif args['action'] == 'put':
        count = 0
        text_dict = text.to_dict(only=('position', 'name', 'body'))
        keys = list(filter(lambda key: args[key] is not None and key in text_dict and args[key] != text_dict[key], args.keys()))
        for key in keys:
            count += 1
            if key == 'position':
                text.position = args["position"]
            if key == 'name':
                text.name = args["name"]
            if key == 'body':
                text.body = args["body"]
        if count == 0:
            return raise_error("Пустой запрос", session)
        text_dict_2 = text.to_dict(only=('position', 'name', 'body'))
        list_chang = [f'изменяет {key} с {text_dict[key]} на {text_dict_2[key]}' for key in keys]
        session.commit()
        add_auditlog("Изменение", f"Админ {admin.name} {admin.surname} изменяет текст {text.number}:"
                                  f" {', '.join(list_chang)}", admin, datetime.datetime.now())
        session.close()
        return {"success": f"Текст {text.number} успешно изменён"}
    return raise_error("Неизвестный метод", session)


def create_text(args):
    if not all(args[key] is not None for key in ['position', 'name', 'body', 'admin_email']):
        return raise_error('Пропущены некоторые аргументы, необходимые для добавления нового текста')
    admin, session = check_admin_status(args['admin_email'])
    new_text = Text()
    new_text.position = args["position"]
    new_text.name = args["name"]
    new_text.body = args["body"]
    session.add(new_text)
    session.commit()
    add_auditlog("Создание", f"Админ {admin.name} {admin.surname} добавляет текст {new_text.number}: {new_text.to_dict(only=('id', 'position', 'name', 'body'))}",
                 admin, datetime.datetime.now())
    session.close()
    return {'success': f'Текст {new_text.number} создан'}
