review:
	@echo "Open Claude Code chat and paste contents of .vscode/review.md"

lint:
	ruff check .

format:
	black .

check: format lint
	@echo "All checks passed"
