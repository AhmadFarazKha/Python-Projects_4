import datetime
import pytz  # For timezone handling

class Appointment:
    def __init__(self, patient_name, appointment_type, start_time, duration):
        self.patient_name = patient_name
        self.appointment_type = appointment_type
        self.start_time = start_time
        self.duration = duration
        self.end_time = self.start_time + datetime.timedelta(minutes=duration)

    def __str__(self):
        return f"{self.patient_name} - {self.appointment_type} - {self.start_time.strftime('%Y-%m-%d %H:%M %Z%z')} - {self.duration} minutes"

class Scheduler:
    def __init__(self, timezone="UTC"):
        self.appointments = []
        self.timezone = pytz.timezone(timezone)
        self.business_hours_start = datetime.time(9, 0)  # 9 AM
        self.business_hours_end = datetime.time(17, 0)    # 5 PM
        self.holidays = [] # Add holiday dates as datetime.date objects

    def is_within_business_hours(self, appointment_time):
      appointment_time_local = appointment_time.astimezone(self.timezone)
      return self.business_hours_start <= appointment_time_local.time() <= self.business_hours_end
    
    def is_holiday(self, appointment_date):
        return appointment_date.date() in self.holidays
    
    def add_holiday(self, holiday_date_str):
        try:
            holiday_date = datetime.datetime.strptime(holiday_date_str, "%Y-%m-%d").date()
            self.holidays.append(holiday_date)
            print(f"Added holiday: {holiday_date}")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

    def schedule_appointment(self, patient_name, appointment_type, date_str, time_str, duration):
        try:
            appointment_datetime_str = f"{date_str} {time_str}"
            appointment_time = datetime.datetime.strptime(appointment_datetime_str, "%Y-%m-%d %H:%M")
            appointment_time = self.timezone.localize(appointment_time)

            if not self.is_within_business_hours(appointment_time):
                return "Appointment time is outside business hours."
            
            if self.is_holiday(appointment_time):
                return "Appointment cannot be scheduled on a holiday."

            new_appointment = Appointment(patient_name, appointment_type, appointment_time, duration)
            if any(self.check_overlap(new_appointment, existing) for existing in self.appointments):
                return "Appointment overlaps with an existing appointment."

            self.appointments.append(new_appointment)
            return "Appointment scheduled successfully."

        except ValueError:
            return "Invalid date or time format. Please use YYYY-MM-DD and HH:MM."
        except pytz.exceptions.NonExistentTimeError:
            return "Invalid time for the specified timezone (e.g., during DST transitions)."

    def check_overlap(self, appt1, appt2):
        return appt1.start_time < appt2.end_time and appt2.start_time < appt1.end_time

    def cancel_appointment(self, patient_name, appointment_time):
        for appointment in self.appointments[:]: # Iterate over a copy to allow removal
            if appointment.patient_name == patient_name and appointment.start_time == appointment_time:
                self.appointments.remove(appointment)
                return "Appointment cancelled."
        return "Appointment not found."
    
    def list_appointments(self):
        if not self.appointments:
            return "No appointments scheduled."
        appointments_str = "\nScheduled Appointments:\n"
        for appointment in self.appointments:
            appointments_str += str(appointment) + "\n"
        return appointments_str

# Example Usage
scheduler = Scheduler(timezone="America/New_York") # Example Timezone
scheduler.add_holiday("2024-12-25") # Example Holiday

print(scheduler.schedule_appointment("Alice", "Checkup", "2024-12-24", "10:00", 30))
print(scheduler.schedule_appointment("Bob", "Consultation", "2024-12-24", "10:15", 45))  # Overlap
print(scheduler.schedule_appointment("Charlie", "X-ray", "2024-12-25", "11:00", 60)) # Holiday
print(scheduler.schedule_appointment("David", "Physio", "2024-12-24", "14:00", 60))
print(scheduler.schedule_appointment("Eve", "Therapy", "2024-12-24", "08:00", 60)) # Outside Business Hours
print(scheduler.list_appointments())

print(scheduler.cancel_appointment("Alice", datetime.datetime(2024, 12, 24, 10, 0, tzinfo=pytz.timezone("America/New_York"))))
print(scheduler.list_appointments())

print(scheduler.schedule_appointment("Frank", "Checkup", "2024-12-24", "10:00", 30))
print(scheduler.list_appointments())