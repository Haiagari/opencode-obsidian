package main

import (
	"bytes"
	"context"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/hex"
	"fmt"
	"io"
	"net"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

const maxBodyBytes = 10 << 20 // 10 MiB

func envDefault(key, fallback string) string {
	if value := strings.TrimSpace(os.Getenv(key)); value != "" {
		return value
	}
	return fallback
}

func unauthorized(w http.ResponseWriter) {
	http.Error(w, "unauthorized", http.StatusUnauthorized)
}

func requireToken(w http.ResponseWriter, r *http.Request, token string) bool {
	provided := r.Header.Get("X-Bunker-Token")
	if provided == "" {
		provided = strings.TrimPrefix(r.Header.Get("Authorization"), "Bearer ")
	}
	if subtle.ConstantTimeCompare([]byte(provided), []byte(token)) != 1 {
		unauthorized(w)
		return false
	}
	return true
}

func safeSlug(raw string) string {
	// Filenames must not disclose the first words of potentially sensitive notes.
	digest := sha256.Sum256([]byte(raw))
	return "memo-" + hex.EncodeToString(digest[:8])
}

func categorize(raw string) (tag string, isArchitecture bool) {
	lower := strings.ToLower(raw)
	switch {
	case strings.Contains(lower, "error"), strings.Contains(lower, "bug"), strings.Contains(lower, "fallo"), strings.Contains(lower, "falla"):
		return "bug", false
	case strings.Contains(lower, "decidimos"), strings.Contains(lower, "estándar"), strings.Contains(lower, "estandar"), strings.Contains(lower, "arquitectura"), strings.Contains(lower, "regla"):
		return "decision", true
	case strings.Contains(lower, "todo"), strings.Contains(lower, "tarea"), strings.Contains(lower, "revisar"):
		return "task", false
	default:
		return "memo", false
	}
}

func newHandler(inboxDir, token, sanitizerPath string) http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet && r.Method != http.MethodHead {
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"status":"ok","service":"bunker-ingest"}` + "\n"))
	})

	mux.HandleFunc("/ingest", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
			return
		}
		if !requireToken(w, r, token) {
			return
		}

		r.Body = http.MaxBytesReader(w, r.Body, maxBodyBytes)
		body, err := io.ReadAll(r.Body)
		if err != nil {
			http.Error(w, "body too large or read failed", http.StatusRequestEntityTooLarge)
			return
		}
		rawContent := strings.TrimSpace(string(body))
		if rawContent == "" {
			http.Error(w, "empty body", http.StatusBadRequest)
			return
		}

		ctx, cancel := context.WithTimeout(r.Context(), 10*time.Second)
		defer cancel()
		cmd := exec.CommandContext(ctx, "python3", sanitizerPath)
		cmd.Stdin = strings.NewReader(rawContent)
		sanitized, err := cmd.Output()
		if err != nil {
			http.Error(w, "failed to sanitize note", http.StatusInternalServerError)
			return
		}
		rawContent = strings.TrimSpace(string(sanitized))
		if len(sanitized) > maxBodyBytes {
			http.Error(w, "sanitized body too large", http.StatusRequestEntityTooLarge)
			return
		}
		if rawContent == "" {
			http.Error(w, "empty body", http.StatusBadRequest)
			return
		}

		tag, isArchitecture := categorize(rawContent)
		lowerContent := strings.ToLower(rawContent)
		titleSlug := safeSlug(rawContent)

		complianceReport := ""
		if isArchitecture && strings.Contains(lowerContent, "ioutil") {
			cmd := exec.Command("grep", "-r", "ioutil", "bin/")
			var out bytes.Buffer
			cmd.Stdout = &out
			_ = cmd.Run()
			if strings.TrimSpace(out.String()) != "" {
				complianceReport = "\n\n## Bunker Sentinel: Compliance Report\nNon-compliant pattern detected: `ioutil`.\n"
			}
		}

		if err := os.MkdirAll(inboxDir, 0o700); err != nil {
			http.Error(w, "failed to create inbox", http.StatusInternalServerError)
			return
		}

		filename := filepath.Join(inboxDir, fmt.Sprintf("%s.md", titleSlug))
		frontmatter := fmt.Sprintf("---\ntype: %s\ncreated: %s\nsource: smart-ingest-local\ntags: [%s]\n---\n\n", tag, time.Now().Format(time.RFC3339), tag)
		fullContent := frontmatter + rawContent + complianceReport + "\n"

		file, err := os.CreateTemp(inboxDir, ".note-*.tmp")
		if err != nil {
			http.Error(w, "failed to write note", http.StatusInternalServerError)
			return
		}
		tempName := file.Name()
		defer os.Remove(tempName)
		if err := file.Chmod(0o600); err != nil {
			_ = file.Close()
			http.Error(w, "failed to protect note", http.StatusInternalServerError)
			return
		}
		if _, err := file.Write([]byte(fullContent)); err != nil {
			_ = file.Close()
			http.Error(w, "failed to write note", http.StatusInternalServerError)
			return
		}
		if err := file.Close(); err != nil {
			http.Error(w, "failed to write note", http.StatusInternalServerError)
			return
		}
		// Linking the complete temp file publishes it atomically without replacing a prior note.
		if err := os.Link(tempName, filename); err != nil {
			if os.IsExist(err) {
				http.Error(w, "note already exists", http.StatusConflict)
				return
			}
			http.Error(w, "failed to publish note", http.StatusInternalServerError)
			return
		}
		w.Header().Set("Content-Type", "text/plain; charset=utf-8")
		fmt.Fprintf(w, "saved as %s\n", filepath.Base(filename))
	})
	return mux
}

func validateConfig(bind, token string) error {
	if len(token) < 32 {
		return fmt.Errorf("BUNKER_INGEST_TOKEN must contain at least 32 characters")
	}
	host, _, err := net.SplitHostPort(bind)
	if err != nil {
		return fmt.Errorf("invalid BUNKER_INGEST_BIND: %w", err)
	}
	if host != "localhost" {
		ip := net.ParseIP(host)
		if ip == nil || !ip.IsLoopback() {
			return fmt.Errorf("Bunker ingest API only supports loopback binding; configure a local reverse proxy for remote access")
		}
	}
	return nil
}

func main() {
	cwd, err := os.Getwd()
	if err != nil {
		fmt.Printf("error getting cwd: %v\n", err)
		os.Exit(1)
	}

	bind := envDefault("BUNKER_INGEST_BIND", "127.0.0.1:9090")
	token := os.Getenv("BUNKER_INGEST_TOKEN")
	if err := validateConfig(bind, token); err != nil {
		fmt.Fprintln(os.Stderr, "configuration error:", err)
		os.Exit(2)
	}
	inboxDir := envDefault("BUNKER_INBOX_DIR", filepath.Join(cwd, "wiki", "inbox"))
	sanitizerPath := envDefault("BUNKER_SANITIZER_PATH", filepath.Join(cwd, "scripts", "sanitize_ingest.py"))

	fmt.Printf("Bunker Smart-Ingest Server running on http://%s\n", bind)
	fmt.Printf("Inbox: %s\n", inboxDir)
	server := &http.Server{
		Addr: bind, Handler: newHandler(inboxDir, token, sanitizerPath),
		ReadHeaderTimeout: 5 * time.Second,
		ReadTimeout:       15 * time.Second,
		WriteTimeout:      15 * time.Second,
		IdleTimeout:       60 * time.Second,
	}
	if err := server.ListenAndServe(); err != nil {
		fmt.Printf("server error: %v\n", err)
		os.Exit(1)
	}
}
