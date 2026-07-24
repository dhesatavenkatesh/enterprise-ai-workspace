import hashlib
import hmac


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_token_hash(
    token: str,
    stored_hash: str,
) -> bool:
    calculated_hash = hash_token(token)

    return hmac.compare_digest(
        calculated_hash,
        stored_hash,
    )
