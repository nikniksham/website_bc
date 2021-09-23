from data.admin import Admin
from data import db_session


def raise_error(error, session=None):
    if session:
        session.close()
    return {"message": error}


def check_admin_status(email, need_status=1):
    admin, session = check_admin(email)
    if admin.status < int(need_status):
        return raise_error("У вас недостаточно прав для этого", session), 1
    return admin, session


def check_admin(email):
    session = db_session.create_session()
    admin = session.query(Admin).filter(Admin.email == email).first()
    if not admin:
        return raise_error(f"Админ {email} не найден", session), 1
    return admin, session