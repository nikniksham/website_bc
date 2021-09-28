import datetime
from data import db_session
from data.Inner.AuditlogAPI import add_auditlog
from data.email import Email
from data.Inner.main_file import raise_error, check_admin_status


def find_by_id(id, session):
    email = session.query(Email).get(id)
    if not email:
        return raise_error(f"Электронная почта не найдена", session), 1
    return email, session


def get_email_list():
    session = db_session.create_session()
    emails = session.query(Email).all()
    session.close()
    return [item.to_dict(only=('id', 'email')) for item in emails]


def edit_email(email_id, args):
    count = 0
    if not all(args[key] is not None for key in ['admin_email', 'action']):
        return raise_error('Пропущены некоторые важные аргументы')
    admin, session = check_admin_status(args['admin_email'])
    email, session = find_by_id(email_id, session)
    if type(email) == dict:
        session.close()
        return email
    if args['action'] == "get":
        session.close()
        return email.to_dict(only=('id', 'email'))
    elif args['action'] == 'delete':
        session.delete(email)
        session.commit()
        add_auditlog("Удаление", f"Админ {admin.name} {admin.surname} удаляет электронную почту {email.email}",
                     admin, datetime.datetime.now())
        session.close()
        return {"success": f"Электроная почта {email.email} успешно удалена"}
    elif args['action'] == 'put':
        email, session = find_by_id(email_id, session)
        if type(email) == dict:
            session.close()
            return email
        email_dict = email.to_dict(only=('email',))
        keys = list(filter(lambda key: args[key] is not None and key in email_dict and args[key] != email_dict[key], args.keys()))
        for key in keys:
            count += 1
            if key == 'email':
                if session.query(Email).filter(Email.email == args['email']).first():
                    raise_error("Этот адрес электронной почты уже существует", session)
                email.email = args["email"]
        if count == 0:
            return raise_error("Пустой запрос")
        email_dict_2 = email.to_dict(only=('email',))
        list_chang = [f'изменяет {key} с {email_dict[key]} на {email_dict_2[key]}' for key in keys]
        session.commit()
        add_auditlog("Изменение", f"Админ {admin.name} {admin.surname} изменяет электронную почту {email.email}:"
                                  f" {', '.join(list_chang)}", admin, datetime.datetime.now())
        session.close()
        return {"success": f"Электронная почта {email.email} успешно изменена"}
    return raise_error("Неизвестный метод", session)


def create_email(args):
    if not all(args[key] is not None for key in ['email', 'admin_email']):
        return raise_error('Пропущены некоторые аргументы, необходимые для создания нового адреса электронной почты')
    admin, session = check_admin_status(args['admin_email'])
    if session.query(Email).filter(Email.email == args['email']).first():
        return raise_error("Этот адрес электронной почты уже существует", session)
    new_email = Email()
    new_email.email = args["email"]
    session.add(new_email)
    session.commit()
    add_auditlog("Создание", f"Админ {admin.name} {admin.surname} добавляет почтовый адрес {new_email.email}: {new_email.to_dict(only=('id', 'email'))}",
                 admin, datetime.datetime.now())
    session.close()
    return {'success': f'Почтовый адрес {new_email.email} создан'}
