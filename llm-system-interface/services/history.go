package services

// import (
//     "database/sql"
//     "llm-system-interface/models"
// )

// func GetRecentMessages(db *sql.DB, sessionID string, limit int) ([]models.Message, error) {
//     rows, err := db.Query(`
//         SELECT role, content FROM messages
//         WHERE session_id = $1
//         ORDER BY created_at DESC
//         LIMIT $2
//     `, sessionID, limit)
//     // ... scan rows, reverse order, return
// }

// func SaveMessage(db *sql.DB, sessionID string, msg models.Message) error {
//     _, err := db.Exec(`
//         INSERT INTO messages (session_id, role, content)
//         VALUES ($1, $2, $3)
//     `, sessionID, msg.Role, msg.Content)
//     return err
// }

// Placeholder for future database history logic
func SaveChatToDB() {
    // Coming soon...
}