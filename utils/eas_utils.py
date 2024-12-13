# Valid Input
print(format_message("FLOOD-Heavy rain expected in your area. Evacuate immediately."))

# Invalid Input (Empty String)
try:
    print(format_message(""))
except ValueError as e:
    print(e)

# Invalid Input (Non-string)
try:
    print(format_message(None))
except ValueError as e:
    print(e)
