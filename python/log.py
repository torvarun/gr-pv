import logging

log = logging.getLogger()
log.setLevel(logging.DEBUG)

# Debug Logger
debug_handler = logging.FileHandler(filename='test_debug.log', mode='w')
debug_handler.setLevel(logging.DEBUG)

debug_formatter = logging.Formatter("%(levelname)-8s  %(message)-8s", "%Y-%m-%d %H:%M")
debug_handler.setFormatter(debug_formatter)

log.addHandler(debug_handler)

# Test Results Logger
results_handler = logging.FileHandler(filename='test_results.log', mode='w')
results_handler.setLevel(logging.INFO) #Ignores all debug messages

#results_formatter = logging.Formatter("%(asctime)s : %(levelname)-8s %(message)s", "%Y-%m-%d %H:%M")
results_formatter = logging.Formatter("%(message)s")
results_handler.setFormatter(results_formatter)

log.addHandler(results_handler)

# Console output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

console_formatter = logging.Formatter("%(message)s")
console_handler.setFormatter(console_formatter)

log.addHandler(console_handler)
