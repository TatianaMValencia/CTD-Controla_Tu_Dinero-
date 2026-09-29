"""Cambio de contraseña con código de 10 dígitos por correo.

Mismo patrón que 2FA: Redis primario (claves pw:*), Postgres fallback.
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.password import PasswordCode
from app.services.email import send_password_code
from app.services.twofa import CooldownError, _r


def _hash(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def _keys(user_id: str) -> tuple[str, str, str]:
    return f"pw:code:{user_id}", f"pw:att:{user_id}", f"pw:cd:{user_id}"


def emitir(db: Session | None, user_id: str, correo: str) -> None:
    code = f"{secrets.randbelow(10_000_000_000):010d}"
    r = _r()
    if r is not None:
        ck, _, cd = _keys(user_id)
        ttl = r.ttl(cd)
        if ttl and ttl > 0:
            raise CooldownError(int(ttl))
        ttl_s = settings.twofa_ttl_min * 60
        r.setex(ck, ttl_s, _hash(code))
        r.setex(cd, settings.twofa_cooldown_s, "1")
        try:
            send_password_code(correo, code)
        except Exception:
            r.delete(ck, cd)
            raise
        return
    assert db is not None
    db.query(PasswordCode).filter_by(user_id=user_id, used=False).update({"used": True})
    db.add(PasswordCode(user_id=user_id, code_hash=_hash(code),
                        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=settings.twofa_ttl_min)))
    db.commit()
    send_password_code(correo, code)


def verificar(db: Session | None, user_id: str, code: str) -> bool:
    r = _r()
    if r is not None:
        ck, ak, _ = _keys(user_id)
        h = r.get(ck)
        if not h:
            return False
        n = r.incr(ak)
        if n == 1:
            r.expire(ak, settings.twofa_ttl_min * 60)
        if n > settings.twofa_max_attempts:
            r.delete(ck, ak)
            return False
        if h == _hash(code.strip()):
            r.delete(ck, ak)
            return True
        return False
    assert db is not None
    row = db.query(PasswordCode).filter_by(user_id=user_id, used=False).order_by(PasswordCode.expires_at.desc()).first()
    if not row:
        return False
    if datetime.utcnow() > row.expires_at or row.attempts >= settings.twofa_max_attempts:
        row.used = True
        db.commit()
        return False
    row.attempts += 1
    if row.code_hash == _hash(code.strip()):
        row.used = True
        db.commit()
        return True
    db.commit()
    return False
