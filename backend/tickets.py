from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import (
    db,
    Ticket,
    TicketHistory,
    TicketComment,
    User,
    AIPrediction
)

from decorators import role_required
from ai_service import (
    predict_ticket,
    generate_response_suggestion
)

tickets_bp = Blueprint("tickets", __name__)


@tickets_bp.route("", methods=["POST"])
@jwt_required()
def create_ticket():
    data = request.get_json()

    if not data:
        return {"message": "Request body is required"}, 400

    title = data.get("title")
    description = data.get("description")
    category = data.get("category")

    if not title or not description:
        return {"message": "Title and description are required"}, 400

    user_id = int(get_jwt_identity())

    # -----------------------------------
    # AI ANALYSIS
    # -----------------------------------

    ai_result = predict_ticket(
        title,
        description
    )

    predicted_category = ai_result["category"]
    predicted_priority = ai_result["priority"]

    # Use user-provided category if supplied.
    # Otherwise use AI predicted category.
    final_category = category or predicted_category

    # -----------------------------------
    # CREATE TICKET
    # -----------------------------------

    ticket = Ticket(
        user_id=user_id,
        title=title,
        description=description,
        category=final_category,
        priority=predicted_priority,
        status="open",
        ai_category=predicted_category,
        ai_priority=predicted_priority
    )

    db.session.add(ticket)
    db.session.flush()

    # -----------------------------------
    # SAVE AI PREDICTION
    # -----------------------------------

    ai_prediction = AIPrediction(
        ticket_id=ticket.id,
        predicted_category=predicted_category,
        predicted_priority=predicted_priority,
        sentiment=ai_result["sentiment"],
        confidence=ai_result["confidence"],
        model_version=ai_result["model_version"]
    )

    db.session.add(ai_prediction)

    # -----------------------------------
    # CREATE HISTORY
    # -----------------------------------

    history = TicketHistory(
        ticket_id=ticket.id,
        changed_by=user_id,
        old_status=None,
        new_status=ticket.status,
        action="CREATED",
        details=(
            f"Ticket created. "
            f"AI predicted category={predicted_category}, "
            f"priority={predicted_priority}, "
            f"sentiment={ai_result['sentiment']}"
        )
    )

    db.session.add(history)

    db.session.commit()

    return {
        "message": "Ticket created successfully",

        "ticket": {
            "id": ticket.id,
            "title": ticket.title,
            "description": ticket.description,
            "category": ticket.category,
            "priority": ticket.priority,
            "status": ticket.status,
            "user_id": ticket.user_id,
            "ai_category": ticket.ai_category,
            "ai_priority": ticket.ai_priority
        },

        "ai_analysis": {
            "category": predicted_category,
            "priority": predicted_priority,
            "sentiment": ai_result["sentiment"],
            "confidence": ai_result["confidence"],
            "model_version": ai_result["model_version"]
        }
    }, 201


@tickets_bp.route("", methods=["GET"])
@jwt_required()
def get_tickets():

    user_id = int(get_jwt_identity())

    tickets = Ticket.query.filter_by(
        user_id=user_id
    ).order_by(
        Ticket.created_at.desc()
    ).all()

    ticket_list = []

    for ticket in tickets:

        ticket_list.append({
            "id": ticket.id,
            "title": ticket.title,
            "description": ticket.description,
            "category": ticket.category,
            "priority": ticket.priority,
            "status": ticket.status,
            "user_id": ticket.user_id,
            "ai_category": ticket.ai_category,
            "ai_priority": ticket.ai_priority,
            "created_at": (
                ticket.created_at.isoformat()
                if ticket.created_at
                else None
            )
        })

    return {
        "count": len(ticket_list),
        "tickets": ticket_list
    }, 200



@tickets_bp.route("/<int:ticket_id>", methods=["GET"])
@jwt_required()
def get_ticket(ticket_id):
    user_id = int(get_jwt_identity())

    current_user = User.query.get(user_id)

    if not current_user or not current_user.is_active:
        return {
            "message": "User not found or inactive"
        }, 403

    ticket = Ticket.query.get(ticket_id)

    if not ticket:
        return {
            "message": "Ticket not found or access denied"
        }, 404

    # Requesters can view their own tickets.
    # Agents can view tickets assigned to them.
    # Admins can view all tickets.
    allowed = (
        current_user.role == "admin"
        or ticket.user_id == user_id
        or (
            current_user.role == "agent"
            and ticket.assigned_to == user_id
        )
    )

    if not allowed:
        return {
            "message": "Ticket not found or access denied"
        }, 404

    return {
        "id": ticket.id,
        "title": ticket.title,
        "description": ticket.description,
        "category": ticket.category,
        "priority": ticket.priority,
        "status": ticket.status,
        "user_id": ticket.user_id,
        "assigned_to": ticket.assigned_to,
        "ai_category": ticket.ai_category,
        "ai_priority": ticket.ai_priority,
        "created_at": (
            ticket.created_at.isoformat()
            if ticket.created_at else None
        ),
        "updated_at": (
            ticket.updated_at.isoformat()
            if ticket.updated_at else None
        )
    }, 200


@tickets_bp.route("/<int:ticket_id>/status", methods=["PUT"])
@jwt_required()
def update_ticket_status(ticket_id):
    user_id = int(get_jwt_identity())

    current_user = User.query.get(user_id)

    if not current_user or not current_user.is_active:
        return {
            "message": "User not found or inactive"
        }, 403

    ticket = Ticket.query.get(ticket_id)

    if not ticket:
        return {
            "message": "Ticket not found or access denied"
        }, 404

    # Requesters can update their own tickets.
    # Agents can update tickets assigned to them.
    # Admins can update all tickets.
    allowed = (
        current_user.role == "admin"
        or ticket.user_id == user_id
        or (
            current_user.role == "agent"
            and ticket.assigned_to == user_id
        )
    )

    if not allowed:
        return {
            "message": "Ticket not found or access denied"
        }, 404

    data = request.get_json(silent=True)

    if not data:
        return {
            "message": "Request body is required"
        }, 400

    new_status = data.get("status")

    allowed_statuses = [
        "open",
        "in_progress",
        "resolved",
        "closed"
    ]

    if new_status not in allowed_statuses:
        return {
            "message": "Invalid status",
            "allowed_statuses": allowed_statuses
        }, 400

    old_status = ticket.status

    if old_status == new_status:
        return {
            "message": "Ticket already has this status"
        }, 400

    ticket.status = new_status

    history = TicketHistory(
        ticket_id=ticket.id,
        changed_by=user_id,
        old_status=old_status,
        new_status=new_status,
        action="STATUS_CHANGED",
        details=(
            f"Ticket status changed "
            f"from {old_status} to {new_status}"
        )
    )

    db.session.add(history)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return {
            "message": "Failed to update ticket status"
        }, 500

    return {
        "message": "Ticket status updated successfully",
        "ticket": {
            "id": ticket.id,
            "status": ticket.status,
            "old_status": old_status,
            "new_status": new_status
        }
    }, 200




@tickets_bp.route("/<int:ticket_id>/comments", methods=["POST"])
@jwt_required()
def add_ticket_comment(ticket_id):

    user_id = int(get_jwt_identity())

    current_user = User.query.get(user_id)

    if not current_user or not current_user.is_active:
        return {
            "message": "User not found or inactive"
        }, 403

    ticket = Ticket.query.get(ticket_id)

    if not ticket:
        return {
            "message": "Ticket not found"
        }, 404

    # Allow admins, ticket creators, and assigned agents
    allowed = (
        current_user.role == "admin"
        or ticket.user_id == user_id
        or (
            current_user.role == "agent"
            and ticket.assigned_to == user_id
        )
    )

    if not allowed:
        return {
            "message": "Access denied"
        }, 403

    data = request.get_json(silent=True)

    if not data:
        return {
            "message": "Request body is required"
        }, 400

    comment_text = data.get("comment")

    if not isinstance(comment_text, str) or not comment_text.strip():
        return {
            "message": "Comment is required"
        }, 400

    comment = TicketComment(
        ticket_id=ticket.id,
        user_id=user_id,
        comment=comment_text.strip()
    )

    db.session.add(comment)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return {
            "message": "Failed to add comment"
        }, 500

    return {
        "message": "Comment added successfully",
        "comment": {
            "id": comment.id,
            "ticket_id": comment.ticket_id,
            "user_id": comment.user_id,
            "comment": comment.comment,
            "created_at": (
                comment.created_at.isoformat()
                if comment.created_at
                else None
            )
        }
    }, 201


@tickets_bp.route("/<int:ticket_id>/comments", methods=["GET"])
@jwt_required()
def get_ticket_comments(ticket_id):
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)

    if not current_user or not current_user.is_active:
        return {"message": "User not found or inactive"}, 403

    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return {"message": "Ticket not found"}, 404

    allowed = (
        current_user.role == "admin"
        or ticket.user_id == user_id
        or (current_user.role == "agent" and ticket.assigned_to == user_id)
    )
    if not allowed:
        return {"message": "Access denied"}, 403

    comments = (
        TicketComment.query.filter_by(ticket_id=ticket.id)
        .order_by(TicketComment.created_at.asc())
        .all()
    )

    return {
        "ticket_id": ticket.id,
        "count": len(comments),
        "comments": [
            {
                "id": comment.id,
                "ticket_id": comment.ticket_id,
                "user_id": comment.user_id,
                "comment": comment.comment,
                "created_at": comment.created_at.isoformat() if comment.created_at else None,
            }
            for comment in comments
        ],
    }, 200


@tickets_bp.route("/<int:ticket_id>/assign", methods=["PUT"])
@role_required("admin")
def assign_ticket(ticket_id):

    user_id = int(get_jwt_identity())

    ticket = Ticket.query.get(ticket_id)

    if not ticket:
        return {
            "message": "Ticket not found"
        }, 404

    data = request.get_json()

    if not data:
        return {
            "message": "Request body is required"
        }, 400

    agent_id = data.get("agent_id")

    if not agent_id:
        return {
            "message": "agent_id is required"
        }, 400

    agent = User.query.filter_by(
        id=agent_id,
        role="agent",
        is_active=True
    ).first()

    if not agent:
        return {
            "message": "Invalid or inactive agent"
        }, 400

    ticket.assigned_to = agent.id

    history = TicketHistory(
        ticket_id=ticket.id,
        changed_by=user_id,
        old_status=ticket.status,
        new_status=ticket.status,
        action="ASSIGNED",
        details=f"Ticket assigned to agent {agent.id}"
    )

    db.session.add(history)

    db.session.commit()

    return {
        "message": "Ticket assigned successfully",
        "ticket": {
            "id": ticket.id,
            "assigned_to": ticket.assigned_to,
            "status": ticket.status
        }
    }, 200


@tickets_bp.route("/<int:ticket_id>/ai-response", methods=["GET"])
@jwt_required()
def get_ai_response(ticket_id):
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)

    if not current_user or not current_user.is_active:
        return {"message": "User not found or inactive"}, 403

    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return {"message": "Ticket not found or access denied"}, 404

    # Requesters may access their own tickets, assigned agents their assigned
    # tickets, and admins all tickets.
    allowed = (
        current_user.role == "admin"
        or ticket.user_id == user_id
        or (current_user.role == "agent" and ticket.assigned_to == user_id)
    )
    if not allowed:
        return {"message": "Ticket not found or access denied"}, 404

    suggested_response = generate_response_suggestion(
        ticket.title,
        ticket.description,
        ticket.ai_category or ticket.category or "general",
        ticket.ai_priority or ticket.priority or "medium",
    )

    return {
        "ticket_id": ticket.id,
        "suggested_response": suggested_response,
        "ai_analysis": {
            "category": ticket.ai_category or ticket.category,
            "priority": ticket.ai_priority or ticket.priority,
        },
    }, 200


@tickets_bp.route("/queue", methods=["GET"])
@role_required("agent", "admin")
def get_ticket_queue():
    user_id = int(get_jwt_identity())

    current_user = User.query.get(user_id)

    if not current_user or not current_user.is_active:
        return {"message": "User not found or inactive"}, 403

    query = Ticket.query

    # Agents see their assigned tickets and unassigned tickets.
    # Admins can see every ticket.
    if current_user.role == "agent":
        from sqlalchemy import or_

        query = query.filter(
            or_(
                Ticket.assigned_to == user_id,
                Ticket.assigned_to.is_(None)
            )
        )

    tickets = query.order_by(
        Ticket.created_at.desc()
    ).all()

    return {
        "count": len(tickets),
        "tickets": [
            {
                "id": ticket.id,
                "title": ticket.title,
                "description": ticket.description,
                "category": ticket.category,
                "priority": ticket.priority,
                "status": ticket.status,
                "user_id": ticket.user_id,
                "assigned_to": ticket.assigned_to,
                "ai_category": ticket.ai_category,
                "ai_priority": ticket.ai_priority,
                "created_at": (
                    ticket.created_at.isoformat()
                    if ticket.created_at else None
                )
            }
            for ticket in tickets
        ]
    }, 200


