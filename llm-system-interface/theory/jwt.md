
# JWT — JSON Web Token

JWT = 3 Base64 strings joined by dots: `header.payload.signature`

- **Header** — which algorithm was used (e.g. HS256)
- **Payload** — data like `userId`, `exp` (expiry), `role`
- **Signature** — HMAC of header+payload using a secret key

The server verifies the signature to prove nobody tampered with the payload.
Your teammates sign the token on login. You verify it on every request.

---

## Step 1 — Context key + helper (middleware/auth.go)

```go
package middleware

import "context"

type contextKey string

const userIDKey contextKey = "userID"

// Call this anywhere downstream to get the logged-in user's ID.
func UserIDFromContext(ctx context.Context) (string, bool) {
    id, ok := ctx.Value(userIDKey).(string)
    return id, ok && id != ""
}
```

`contextKey` is a private type so it never collides with keys from other packages.
`UserIDFromContext` is the public getter — your rate limiter will call this.

---

## Step 2 — JWTAuth middleware (middleware/auth.go continued)

```go
import (
    "net/http"
    "strings"
    "github.com/golang-jwt/jwt/v5"
)

// nestsed funcs in go: middleware factory(pattern used by popular libraries like gorilla/mux and negroni)
func JWTAuth(secret []byte) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {

            // Let CORS preflight through without a token.
            if r.Method == http.MethodOptions {
                next.ServeHTTP(w, r)
                return
            }

            // 1. Pull the token out of the Authorization header.
            raw := r.Header.Get("Authorization")
            if !strings.HasPrefix(raw, "Bearer ") {
                http.Error(w, "Unauthorized", http.StatusUnauthorized)
                return
            }
            tokenStr := strings.TrimPrefix(raw, "Bearer ")

            // 2. Parse + verify signature.
            token, err := jwt.Parse(tokenStr, func(t *jwt.Token) (any, error) {
                if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
                    return nil, jwt.ErrSignatureInvalid // reject unexpected algorithm
                }
                return secret, nil
            })
            if err != nil || !token.Valid {
                http.Error(w, "Unauthorized", http.StatusUnauthorized)
                return
            }

            // 3. Extract user ID from claims and write into context.
            claims, _ := token.Claims.(jwt.MapClaims)
            userID, _ := claims["sub"].(string) // ask teammates if they use "sub" or "userId"
            ctx := context.WithValue(r.Context(), userIDKey, userID)

            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }
}
```

`"sub"` is the standard JWT claim for user ID — confirm the claim name with your teammates.

---

---

## Why func inside func?

```go
func JWTAuth(secret []byte) func(http.Handler) http.Handler {
    //         ^ config in        ^ returns a middleware
    return func(next http.Handler) http.Handler {
        //       ^ the next handler in the chain
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            //                       ^ runs on every request
        })
    }
}
```

**Outer func** — runs once at startup. Receives config (`secret`).
Keeps `secret` alive in a closure so the inner functions can use it.

### What is a closure?

A closure is a function that "closes over" (captures) variables from its outer scope.
The inner function remembers those variables even after the outer function has returned.

```go
func JWTAuth(secret []byte) func(http.Handler) http.Handler {
    // `secret` lives here, in the outer function's scope.

    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            // This inner func still has access to `secret`
            // even though JWTAuth() already finished running.
            token, err := jwt.Parse(tokenStr, func(t *jwt.Token) (any, error) {
                return secret, nil  // <-- closure: using outer variable
            })
        })
    }
}
```

Think of it like a backpack: when the inner function is created,
it packs `secret` into its backpack and carries it forever.

**Middle func** — runs once when you attach the middleware to your router.
Receives `next` (the handler to call if auth passes).

**Inner func** — runs on every single HTTP request.
This is where the actual work happens.

If you wrote it flat with no closure:
```go
// Where would `secret` and `next` come from?
func JWTAuth(w http.ResponseWriter, r *http.Request) { ... }
```
You'd have no way to inject config or chain handlers.

The pattern is the same as `RateLimiter` already in your code — compare them side by side.

---

## Step 3 — update extractClientKey (next)
