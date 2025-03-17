#!/bin/bash
set -e

SESSION="batch_inference"
SCRIPT="python3 batch_inference.py"

PROMPTS=(
#   "What is the capital of France?"
  "Explain the theory of relativity."
  "How does photosynthesis work?"
  "Tell me a brief story about courage"
  "Tell me a brief story about wisdom."
#   "Tell me a brief story about humor."
#   "Tell me a brief story about humans."
#   "Tell me a brief story about the moon."
)

if [ -n "$TMUX" ]; then
    echo "Please run outside of tmux."
    exit 1
fi

tmux kill-session -t "$SESSION" 2>/dev/null || true
sleep 1

echo "Creating tmux session '$SESSION'..."

tmux new-session -d -s "$SESSION" -n "pane_1"
tmux send-keys -t "${SESSION}:0.0" "${SCRIPT} \"${PROMPTS[0]}\"" C-m
sleep 0.5

pane_count=1
for prompt in "${PROMPTS[@]:1}"; do
    if (( pane_count % 2 )); then
        tmux split-window -h -t "${SESSION}:0"
    else
        tmux split-window -v -t "${SESSION}:0"
    fi
    sleep 0.5
    tmux send-keys -t "${SESSION}:0.${pane_count}" "${SCRIPT} \"${prompt}\"" C-m
    pane_count=$((pane_count + 1))
    tmux select-layout -t "${SESSION}" tiled
done

tmux select-layout -t "${SESSION}" tiled

echo "Attaching to session '$SESSION'..."
tmux attach-session -t "$SESSION"
