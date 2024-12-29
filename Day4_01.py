import re
from collections import Counter
from datetime import datetime

def analyze_logs(log_file, start_time=None, end_time=None):
    """Analyzes log files, extracts errors, and generates summaries."""

    error_patterns = {
        "database_error": r"Database connection failed: (.*)",
        "timeout_error": r"(.*) timeout",
        "memory_error": r"High memory usage: (\d+)%",
    }
    errors = []
    error_counts = Counter()

    try:
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    timestamp_str, severity, message = line.split(' ', 2)
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

                    if (start_time and timestamp < start_time) or (end_time and timestamp > end_time):
                        continue

                    if "[ERROR]" in severity or "[WARNING]" in severity:
                        for error_name, pattern in error_patterns.items():
                            match = re.search(pattern, message)
                            if match:
                                errors.append((timestamp, severity.strip("[]"), error_name, match.group(0)))
                                error_counts[error_name] += 1
                                break # Avoid matching multiple patterns for the same error

                except (ValueError, IndexError):
                    print(f"Skipping malformed log entry: {line.strip()}")
                    continue

    except FileNotFoundError:
        return "Log file not found."
    
    return errors, error_counts

def generate_report(errors, error_counts):
    """Formats the analysis results into a readable report."""
    report = "Log Analysis Report\n"
    if errors:
        report += "\nDetected Errors:\n"
        for timestamp, severity, error_type, message in errors:
            report += f"- {timestamp} [{severity}] {error_type}: {message}\n"
    else:
        report += "\nNo errors found within the specified time range.\n"
    
    if error_counts:
        report += "\nError Summary:\n"
        for error_type, count in error_counts.items():
            report += f"- {error_type}: {count}\n"
    return report

# Example usage:
log_file = "server.log"  # Create a dummy log file for testing
with open(log_file, 'w') as f:
    f.write("""2024-01-15 14:30:25 [ERROR] Database connection failed: timeout
2024-01-15 14:30:28 [WARNING] High memory usage: 85%
2024-01-15 14:30:30 [ERROR] Connection timeout to server A
2024-01-15 14:30:35 [INFO] Server started
2024-01-15 14:30:40 [ERROR] Database connection failed: network issue
invalid line
2024-01-16 10:00:00 [ERROR] Another timeout error""")

start_time = datetime(2024, 1, 15, 14, 30, 0)
end_time = datetime(2024, 1, 15, 14, 31, 0)

errors, error_counts = analyze_logs(log_file, start_time, end_time)
report = generate_report(errors, error_counts)
print(report)

errors_all, error_counts_all = analyze_logs(log_file)
report_all = generate_report(errors_all, error_counts_all)
print("\nFull Log Report:\n", report_all)

#Example of file not found handling
result = analyze_logs("nonexistent_file.log")
print("\nFile not found handling:\n", result)