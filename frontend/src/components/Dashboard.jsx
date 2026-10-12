import { useEffect, useState } from "react";
import TicketDetails from "./TicketDetails";
import { apiFetch } from "../api";

function Dashboard() {
  const [selectedTicketId, setSelectedTicketId] = useState(null);

  const [user, setUser] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);

  const [showCreateForm, setShowCreateForm] = useState(false);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const [creating, setCreating] = useState(false);
  const [message, setMessage] = useState("");
  const [aiAnalysis, setAiAnalysis] = useState(null);


  // ==========================================
  // GET TICKETS
  // ==========================================

  
const fetchTickets = async () => {
  try {
    const storedUser = localStorage.getItem("user");
    const currentUser = storedUser
      ? JSON.parse(storedUser)
      : null;

    const isStaff =
      currentUser?.role === "agent" ||
      currentUser?.role === "admin";

    const endpoint = isStaff
      ? "/api/tickets/queue"
      : "/api/tickets";

    const response = await apiFetch(endpoint, {
      method: "GET",
    });

    const data = await response.json();

    if (!response.ok) {
      setMessage(
        data.message || "Unable to load tickets"
      );
      return;
    }

    setTickets(data.tickets || []);
    setMessage("");
  } catch (error) {
    setMessage(
      error.message ||
        "Unable to connect to the backend."
    );
  } finally {
    setLoading(false);
  }
};

  useEffect(() => {
    const storedUser = localStorage.getItem("user");

    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }

    fetchTickets();
  }, []);


  // ==========================================
  // CREATE TICKET
  // ==========================================

  const handleCreateTicket = async (event) => {
    event.preventDefault();

    setCreating(true);
    setMessage("");
    setAiAnalysis(null);

  
try {
  const response = await apiFetch("/api/tickets", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      title,
      description,
    }),
  });

      
      const data = await response.json();

      if (!response.ok) {
        setMessage(
          data.message || "Ticket creation failed"
        );
        return;
      }

      setMessage(
        "Ticket created successfully!"
      );

      setAiAnalysis(data.ai_analysis);

      setTitle("");
      setDescription("");

      await fetchTickets();

    } catch (error) {
      setMessage(
        "Unable to connect to the backend."
      );
    } finally {
      setCreating(false);
    }
  };

  // ==========================================
  // LOGOUT
  // ==========================================

  const handleLogout = async () => {
    const refreshToken =
      localStorage.getItem("refresh_token");

    try {
    
if (refreshToken) {
  await apiFetch("/api/auth/logout", {
    method: "POST",
    token: refreshToken,
  });
}

    } catch (error) {
      console.log("Logout request failed");
    }

    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");

    window.location.reload();
  };

  // ==========================================
  // TICKET STATISTICS
  // ==========================================

  const openTickets = tickets.filter(
    (ticket) =>
      ticket.status === "open"
  ).length;

  const inProgressTickets = tickets.filter(
    (ticket) =>
      ticket.status === "in_progress"
  ).length;

  const resolvedTickets = tickets.filter(
    (ticket) =>
      ticket.status === "resolved" ||
      ticket.status === "closed"
  ).length;

  // ==========================================
  // LOADING
  // ==========================================

  if (loading) {
    return (
      <div className="dashboard-loading">
        Loading dashboard...
      </div>
    );
  }

  // ==========================================
  // OPEN TICKET DETAILS
  // ==========================================

  if (selectedTicketId) {
    return (
      <TicketDetails
        ticketId={selectedTicketId}
        onBack={() =>
          setSelectedTicketId(null)
        }
      />
    );
  }

  // ==========================================
  // DASHBOARD
  // ==========================================

  return (
    <div className="dashboard">

      {/* HEADER */}

      <header className="dashboard-header">

        <div className="brand">

          <span className="brand-icon">
            🛡️
          </span>

          <div>

            <h1>
              AI IT Support
            </h1>

            <p>
              Intelligent Support System
            </p>

          </div>

        </div>

        <div className="header-right">

          <div className="user-info">

            <strong>
              {user?.name || "User"}
            </strong>

            <span>
              {user?.role || "user"}
            </span>

          </div>

          <button
            className="logout-button"
            onClick={handleLogout}
          >
            Logout
          </button>

        </div>

      </header>

      {/* MAIN */}

      <main className="dashboard-main">

        {/* WELCOME */}

        <section className="welcome-section">

          <h2>
            Welcome back
            {user?.name
              ? `, ${user.name}`
              : ""}! 👋
          </h2>

          <p>
            Manage your IT support requests
            and monitor AI-powered ticket
            analysis.
          </p>

        </section>

        {/* STATISTICS */}

        <section className="stats-grid">

          <div className="stat-card">

            <div className="stat-icon">
              📂
            </div>

            <div>

              <span>
                Total Tickets
              </span>

              <strong>
                {tickets.length}
              </strong>

            </div>

          </div>

          <div className="stat-card">

            <div className="stat-icon">
              🔵
            </div>

            <div>

              <span>
                Open
              </span>

              <strong>
                {openTickets}
              </strong>

            </div>

          </div>

          <div className="stat-card">

            <div className="stat-icon">
              🟡
            </div>

            <div>

              <span>
                In Progress
              </span>

              <strong>
                {inProgressTickets}
              </strong>

            </div>

          </div>

          <div className="stat-card">

            <div className="stat-icon">
              🟢
            </div>

            <div>

              <span>
                Resolved
              </span>

              <strong>
                {resolvedTickets}
              </strong>

            </div>

          </div>

        </section>

        {/* TICKETS */}

        <section className="tickets-section">

          <div className="section-header">

            <div>

              <h2>
                My Tickets
              </h2>

              <p>
                Your recent IT support requests
              </p>

            </div>

            <button
              className="create-ticket-button"
              onClick={() => {
                setShowCreateForm(
                  !showCreateForm
                );

                setMessage("");
                setAiAnalysis(null);
              }}
            >
              {showCreateForm
                ? "✕ Close"
                : "+ Create Ticket"}
            </button>

          </div>

          {/* CREATE TICKET FORM */}

          {showCreateForm && (

            <div className="create-ticket-form">

              <h3>
                Create New Support Ticket
              </h3>

              <p>
                Describe your issue and our AI
                will automatically analyze it.
              </p>

              <form
                onSubmit={handleCreateTicket}
              >

                <div className="form-group">

                  <label>
                    Ticket Title
                  </label>

                  <input
                    type="text"
                    placeholder="Example: VPN connection is not working"
                    value={title}
                    onChange={(event) =>
                      setTitle(
                        event.target.value
                      )
                    }
                    required
                  />

                </div>

                <div className="form-group">

                  <label>
                    Problem Description
                  </label>

                  <textarea
                    placeholder="Describe your IT problem in detail..."
                    value={description}
                    onChange={(event) =>
                      setDescription(
                        event.target.value
                      )
                    }
                    required
                  />

                </div>

                <button
                  type="submit"
                  className="submit-ticket-button"
                  disabled={creating}
                >
                  {creating
                    ? "Analyzing & Creating..."
                    : "Create Ticket"}
                </button>

              </form>

            </div>

          )}

          {/* MESSAGE */}

          {message && (

            <div className="dashboard-message">
              {message}
            </div>

          )}

          {/* AI ANALYSIS */}

          {aiAnalysis && (

            <div className="ai-result">

              <div className="ai-result-header">

                <h3>
                  🤖 AI Ticket Analysis
                </h3>

                <span>
                  AI v1
                </span>

              </div>

              <div className="ai-result-grid">

                <div>

                  <label>
                    Category
                  </label>

                  <strong>
                    {aiAnalysis.category}
                  </strong>

                </div>

                <div>

                  <label>
                    Priority
                  </label>

                  <strong>
                    {aiAnalysis.priority}
                  </strong>

                </div>

                <div>

                  <label>
                    Sentiment
                  </label>

                  <strong>
                    {aiAnalysis.sentiment}
                  </strong>

                </div>

                <div>

                  <label>
                    Confidence
                  </label>

                  <strong>
                    {Math.round(
                      aiAnalysis.confidence * 100
                    )}%
                  </strong>

                </div>

              </div>

            </div>

          )}

          {/* TICKET LIST */}

          {tickets.length === 0 ? (

            <div className="empty-state">

              <div className="empty-icon">
                🎫
              </div>

              <h3>
                No tickets yet
              </h3>

              <p>
                Create your first IT support
                ticket.
              </p>

            </div>

          ) : (

            <div className="ticket-list">

              {tickets.map((ticket) => (

                <div
                  className="ticket-card"
                  key={ticket.id}
                  onClick={() =>
                    setSelectedTicketId(
                      ticket.id
                    )
                  }
                  style={{
                    cursor: "pointer",
                  }}
                >

                  <div className="ticket-main">

                    <div className="ticket-title-row">

                      <h3>
                        {ticket.title}
                      </h3>

                      <span
                        className={`priority ${ticket.priority}`}
                      >
                        {ticket.priority}
                      </span>

                    </div>

                    <p>
                      {ticket.description}
                    </p>

                    <div className="ticket-meta">

                      <span>
                        #{ticket.id}
                      </span>

                      <span>
                        {ticket.category ||
                          "General"}
                      </span>

                      <span>
                        {ticket.status.replace(
                          "_",
                          " "
                        )}
                      </span>

                    </div>

                  </div>

                  <div className="ai-info">

                    <span className="ai-label">
                      🤖 AI
                    </span>

                    <span>
                      {ticket.ai_category ||
                        "Analyzing"}
                    </span>
                    


                  </div>
<button
  className="view-ticket-button"
  onClick={() => setSelectedTicketId(ticket.id)}
>
  View Details →
</button>

                </div>

              ))}

            </div>

          )}

        </section>

      </main>

    </div>
  );
}

export default Dashboard;