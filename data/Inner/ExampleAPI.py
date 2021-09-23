import datetime
from data import db_session
from data.Inner.AuditlogAPI import add_auditlog
from data.example import Example
from data.Inner.main_file import raise_error, check_admin_status


def find_by_id(id, session):
    example = session.query(Example).get(id)
    if not example:
        return raise_error(f"Пример работы не найден", session), 1
    return example, session


def get_example_list():
    session = db_session.create_session()
    examples = session.query(Example).all()
    session.close()
    return [item.to_dict(only=('id', 'name', 'description', 'image', 'link')) for item in examples]


def edit_example(example_id, args):
    if not all(args[key] is not None for key in ['admin_email', 'action']):
        return raise_error('Пропущены некоторые важные аргументы')
    admin, session = check_admin_status(args['admin_email'])
    example, session = find_by_id(example_id, session)
    if type(example) == dict:
        session.close()
        return example
    if args['action'] == "get":
        session.close()
        return example.to_dict(only=('id', 'name', 'description', 'image', 'link'))
    elif args['action'] == 'delete':
        session.delete(example)
        session.commit()
        add_auditlog("Удаление", f"Админ {admin.name} {admin.surname} удаляет пример работы {example.number}", admin,
                     datetime.datetime.now())
        session.close()
        return {"success": f"Пример работы {example.number} успешно удалён"}
    elif args['action'] == 'put':
        count = 0
        example_dict = example.to_dict(only=('name', 'description', 'image', 'link'))
        keys = list(filter(lambda key: args[key] is not None and key in example_dict and args[key] != example_dict[key], args.keys()))
        for key in keys:
            count += 1
            if key == 'name':
                if session.query(Example).filter(Example.name == args['name']).first():
                    raise_error("Этот пример работы уже существует", session)
                example.name = args["name"]
            if key == 'description':
                example.description = args["description"]
            if key == 'image':
                example.image = args["image"]
            if key == 'link':
                example.link = args["link"]
        if count == 0:
            return raise_error("Пустой запрос", session)
        example_dict_2 = example.to_dict(only=('name', 'description', 'image', 'link'))
        list_chang = [f'изменяет {key} с {example_dict[key]} на {example_dict_2[key]}' for key in keys]
        session.commit()
        add_auditlog("Изменение", f"Админ {admin.name} {admin.surname} изменяет пример работы {example.number}:"
                                  f" {', '.join(list_chang)}", admin, datetime.datetime.now())
        session.close()
        return {"success": f"Пример работы {example.number} успешно изменён"}
    return raise_error("Неизвестный метод", session)


def create_example(args):
    if not all(args[key] is not None for key in ['name', 'description', 'image', 'link', 'admin_email']):
        return raise_error('Пропущены некоторые аргументы, необходимые для добавления нового примера работы')
    admin, session = check_admin_status(args['admin_email'])
    if session.query(Example).filter(Example.link == args['link']).first():
        return raise_error("Этот пример работы уже существует", session)
    new_example = Example()
    new_example.name = args["name"]
    new_example.description = args["description"]
    new_example.image = args["image"]
    new_example.link = args["link"]
    session.add(new_example)
    session.commit()
    add_auditlog("Создание", f"Админ {admin.name} {admin.surname} добавляет пример работы {new_example.number}: {new_example.to_dict(only=('id', 'name', 'description', 'image', 'link'))}",
                 admin, datetime.datetime.now())
    session.close()
    return {'success': f'Пример работы {new_example.number} создан'}
