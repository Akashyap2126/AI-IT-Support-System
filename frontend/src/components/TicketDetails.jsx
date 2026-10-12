import { useEffect, useState } from "react";

function TicketDetails({ ticketId, onBack }) {
  const [ticket, setTicket] = useState(null);
  const [aiResponse, setAiResponse] = useState(null);
  const [comments, setComments] = useState([]);

  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(true);
  const [submittingComment, setSubmittingComment] = useState(false);
  const [message, setMessage] = useState("");

  const token = localStorage.getItem("access_token");

  useEffect(() => {
    fetchTicketDetails();
  }, [ticketId]);

  const fetchTicketDetails = async () => {
    setLoading(true);

    try {
      const ticketResponse = await fetch(
        `http://127.0.0.1:5000/api/tickets/${ticketId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const ticketData = await ticketResponse.json();

      if (!ticketResponse.ok) {
        setMessage(
          ticketData.message || "Unable to load ticket"
        );
        return;
      }

      setTicket(ticketData);

      const aiResponseResult = await fetch(
        `http://127.0.0.1:5000/api/tickets/${ticketId}/ai-response`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const aiData = await aiResponseResult.json();

      if (aiResponseResult.ok) {
        setAiResponse(aiData);
      }

      const commentsResponse = await fetch(
        `http://127.0.0.1:5000/api/tickets/${ticketId}/comments`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const commentsData = await commentsResponse.json();

      if (commentsResponse.ok) {
        setComments(commentsData.comments || []);
      }
    } catch (error) {
      setMessage(
        "Unable to connect to the backend."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleAddComment = async (event) => {
    event.preventDefault();

    if (!comment.trim()) {
      return;
    }

    setSubmittingComment(true);
    setMessage("");

    try {
      const response = await fetch(
        `http://127.0.0.1:5000/api/tickets/${ticketId}/comments`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            comment: comment.trim(),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setMessage(
          data.message || "Unable to add comment"
        );
        return;
      }

      setComment("");

      await fetchTicketDetails();
    } catch (error) {
      setMessage(
        "Unable to connect to the backend."
      );
    } finally {
      setSubmittingComment(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:5000/api/tickets/${ticketId}/status`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            status: newStatus,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setMessage(
          data.message || "Unable to update status"
        );
        return;
      }

      await fetchTicketDetails();
    } catch (error) {
      setMessage(
        "Unable to connect to the backend."
      );
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        Loading ticket...
      </div>
    );
  }

  if (!ticket) {
    return (
      <div className="dashboard-main">
        <button onClick={onBack}>
          ← Back
        </button>

        <p>{message || "Ticket not found."}</p>
      </div>
    );
  }

  return (
    <div className="dashboard">

      <header className="dashboard-header">

        <div className="brand">
          <span className="brand-icon">
            🛡️
          </span>

          <div>
            <h1>AI IT Support</h1>
            <p>Ticket Details</p>
          </div>
        </div>

      </header>

      <main className="dashboard-main">

        <button
          className="back-button"
          onClick={onBack}
        >
          ← Back to Dashboard
        </button>

        {message && (
          <div className="dashboard-message">
            {message}
          </div>
        )}

        {/* TICKET */}

        <section className="ticket-detail-card">

          <div className="ticket-detail-header">

            <div>
              <span className="ticket-number">
                Ticket #{ticket.id}
              </span>

              <h2>{ticket.title}</h2>
            </div>

            <span
              className={`priority ${ticket.priority}`}
            >
              {ticket.priority}
            </span>

          </div>

          <div className="ticket-description">
            <h3>Description</h3>

            <p>
              {ticket.description}
            </p>
          </div>

          <div className="ticket-detail-meta">

            <div>
              <span>Category</span>
              <strong>
                {ticket.category || "General"}
              </strong>
            </div>

            <div>
              <span>Status</span>
              <strong>
                {ticket.status.replace(
                  "_",
                  " "
                )}
              </strong>
            </div>

            <div>
              <span>AI Category</span>
              <strong>
                {ticket.ai_category || "N/A"}
              </strong>
            </div>

            <div>
              <span>AI Priority</span>
              <strong>
                {ticket.ai_priority || "N/A"}
              </strong>
            </div>

          </div>

          {/* STATUS */}

          <div className="status-controls">

            <label>
              Update Status
            </label>

            <select
              value={ticket.status}
              onChange={(event) =>
                handleStatusChange(
                  event.target.value
                )
              }
            >
              <option value="open">
                Open
              </option>

              <option value="in_progress">
                In Progress
              </option>

              <option value="resolved">
                Resolved
              </option>

              <option value="closed">
                Closed
              </option>
            </select>

          </div>

        </section>

        {/* AI RESPONSE */}

        {aiResponse && (

          <section className="ai-response-card">

            <div className="ai-response-header">

              <h2>
                🤖 AI Suggested Response
              </h2>

              <span>
                AI-powered
              </span>

            </div>

            <p>
              {aiResponse.suggested_response}
            </p>

          </section>

        )}

        {/* COMMENTS */}

        <section className="comments-card">

          <h2>
            💬 Comments
          </h2>

          {comments.length === 0 ? (

            <p className="no-comments">
              No comments yet.
            </p>

          ) : (

            <div className="comments-list">

              {comments.map((item) => (

                <div
                  className="comment-item"
                  key={item.id}
                >

                  <p>
                    {item.comment}
                  </p>

                  <span>
                    {item.created_at
                      ? new Date(
                          item.created_at
                        ).toLocaleString()
                      : ""}
                  </span>

                </div>

              ))}

            </div>

          )}

          <form
            className="comment-form"
            onSubmit={handleAddComment}
          >

            <textarea
              placeholder="Write a comment..."
              value={comment}
              onChange={(event) =>
                setComment(
                  event.target.value
                )
              }
            />

            <button
              type="submit"
              disabled={submittingComment}
            >
              {submittingComment
                ? "Adding..."
                : "Add Comment"}
            </button>

          </form>

        </section>

      </main>

    </div>
  );
}

export default TicketDetails;