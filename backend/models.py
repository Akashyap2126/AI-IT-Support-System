from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(
        db.Enum("user", "agent", "admin"),
        nullable=False,
        default="user"
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )


class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    category = db.Column(
        db.String(100),
        nullable=True
    )

    priority = db.Column(
        db.Enum("low", "medium", "high", "critical"),
        nullable=False,
        default="medium"
    )

    status = db.Column(
        db.Enum("open", "in_progress", "resolved", "closed"),
        nullable=False,
        default="open"
    )

    assigned_to = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    ai_category = db.Column(
        db.String(100),
        nullable=True
    )

    ai_priority = db.Column(
        db.String(50),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )


class TicketHistory(db.Model):
    __tablename__ = "ticket_history"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("tickets.id"),
        nullable=False
    )

    changed_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    old_status = db.Column(
        db.String(50),
        nullable=True
    )

    new_status = db.Column(
        db.String(50),
        nullable=True
    )

    action = db.Column(
        db.String(100),
        nullable=False
    )

    details = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )    

class TicketComment(db.Model):
    __tablename__ = "ticket_comments"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("tickets.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    comment = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )    

class RefreshToken(db.Model):
    __tablename__ = "refresh_tokens"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    token_hash = db.Column(
        db.String(255),
        nullable=False
    )

    expires_at = db.Column(
        db.DateTime,
        nullable=False
    )

    revoked = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )    

class AIPrediction(db.Model):
    __tablename__ = "ai_predictions"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("tickets.id"),
        nullable=False
    )

    predicted_category = db.Column(
        db.String(100),
        nullable=True
    )

    predicted_priority = db.Column(
        db.String(50),
        nullable=True
    )

    sentiment = db.Column(
        db.String(50),
        nullable=True
    )

    confidence = db.Column(
        db.Numeric(5, 4),
        nullable=True
    )

    model_version = db.Column(
        db.String(50),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )    

class SecurityEvent(db.Model):
    __tablename__ = "security_events"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    event_type = db.Column(
        db.String(100),
        nullable=False
    )

    ip_address = db.Column(
        db.String(45),
        nullable=True
    )

    user_agent = db.Column(
        db.String(255),
        nullable=True
    )

    details = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )    