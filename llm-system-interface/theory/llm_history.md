=============================
current implement of history
===============================
Frontend sends: [msg1, msg2, msg3, ..., new_question]
Server receives full history, calls Gemini, returns response
Server stores nothing

✅ Stateless servers, perfect for load balancing
✅ Simple, no DB needed for chat
❌ Frontend can tamper with history
❌ History lost on page refresh (unless you localStorage it)
❌ No audit trail, no analytics on conversations
=============================
Professional app approach — backend owns history
================================
This is what ChatGPT, Claude, Cursor etc. all do:
Frontend sends: { session_id: "abc123", message: "new question only" }
Backend:
  1. loads history from DB by session_id
  2. appends new message
  3. calls LLM with full history
  4. saves assistant response to DB
  5. streams response back

  The DB table is simple:
CREATE TABLE messages (
  id          SERIAL PRIMARY KEY,
  session_id  UUID NOT NULL,
  user_id     INTEGER REFERENCES users(id),
  role        VARCHAR(10),        -- 'user' or 'assistant'
  content     TEXT,
  created_at  TIMESTAMP DEFAULT NOW()
);

✅ History survives refresh, logout, device switch
✅ Backend controls what gets sent to LLM (you enforce the 10-message window)
✅ Audit trail, you can build analytics
✅ Users can't tamper with or inflate history
✅ You can cap context window server-side to control Gemini costs
❌ Every request hits the DB (cheap with postgres, but still)
❌ More code

Your load balancer stays stateless — session is in Postgres, not in any server's memory
=============================
  load balancer will solve traffic problems, but it won't solve hardware/API limitations.
===============================
The Real Bottlenecks
Ollama (GPU/RAM): This is your biggest local bottleneck. Ollama processes requests sequentially by default. If student A asks a complex question, student B’s request will hang until the GPU finishes "thinking" for student A.

Gemini API Quota: Since you are on the Free Tier, your RPM (Requests Per Minute) is a hard wall. A load balancer cannot bypass this; if you send 3 requests in a minute and the limit is 2, the API will reject the 3rd regardless of how many "balancers" you have.

Database (Postgres): Unlikely to be a bottleneck for 42 students unless you are running extremely inefficient queries.