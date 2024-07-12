import time
import re

# Sample state mappings
state_mappings = {
    r".*main menu.*": "IN-MENU",
    r".*selecting opponent.*squad battles.*": "IN-MENU-SQUAD-BATTLES-OPPONENT-SELECT",
    r".*in match.*": "IN-MATCH",
    r".*half-time.*": "IN-MENU-HALF-TIME",
    r".*full-time.*": "IN-MENU-FULL-TIME"
}

# Function to extract state from text
def extract_state_from_text(text):
    for pattern, state in state_mappings.items():
        if re.match(pattern, text, re.IGNORECASE):
            return state
    return None  # Default or error state if no match is found

# Evaluate performance
test_texts = ["The game is currently in the main menu", "Selecting opponent in squad battles", "Half-time menu", "In match", "Full-time menu"]
expected_states = ["IN-MENU", "IN-MENU-SQUAD-BATTLES-OPPONENT-SELECT", "IN-MENU-HALF-TIME", "IN-MATCH", "IN-MENU-FULL-TIME"]

# Measure accuracy
correct_predictions = 0
for text, expected in zip(test_texts, expected_states):
    predicted = extract_state_from_text(text)
    if predicted == expected:
        correct_predictions += 1
accuracy = correct_predictions / len(test_texts)
print(f"Accuracy: {accuracy * 100:.2f}%")

# Measure speed
start_time = time.time()
for _ in range(1000):
    for text in test_texts:
        extract_state_from_text(text)
end_time = time.time()
average_time = (end_time - start_time) / (1000 * len(test_texts))
print(f"Average processing time: {average_time * 1000:.2f} ms")
