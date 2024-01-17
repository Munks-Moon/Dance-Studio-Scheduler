# Dance Studio Scheduling App

----

## Purpose

This project is primarily being used to demonstrate the author's proficiency in backend development. While the app's frontend provides an intuitive and user-friendly interface, the backend architecture showcases the ability to write clean and maintainable code.

## Description

The Dance Studio Scheduling App is a Django-based web application crafted to streamline the process of scheduling dance classes for children. This application has been thoughtfully designed to cater to the needs of dance studios and their clients, primarily focusing on enabling parents to easily book and manage their children's dance sessions.

----

## Features

### Interactive Calendar

- **Easy-to-Use Interface:** Our interactive calendar provides a clear view of available timeslots, making it effortless for parents to find and book the perfect time for their child's dance class.
- **Real-Time Availability Updates:** The calendar is updated in real-time, ensuring that available slots are accurately displayed, preventing double bookings.

### Waitlists

- **Seamless Waitlist Integration:** For timeslots that are already filled, clients have the option to join a waitlist. This feature enhances the opportunity for their child to participate in a class, should a slot become available.
- **Automated Notifications:** Waitlisted parents are automatically notified when an opening arises, ensuring they don't miss out on the opportunity to book.

### Admin Features

- **Client Profiles:** Admins have the ability to view detailed client profiles.
- **Invoicing and Billing:** The app streamlines the creation and distribution of invoices, making the billing process efficient and paperless.
- **Email Integration:** Directly email invoices and important notifications to clients through the app, ensuring timely and effective communication.

### Other Notable Features

- **Responsive Design:** The app is fully responsive, ensuring a seamless experience across various devices and screen sizes.

----

## Installation

To run this app, the following are required: Python (v3.9+).

### How to run locally

After cloning the app to your computer, navigate to the project directory in the terminal. Initiate the virtual environment, install the requirements, migrate and run the project. 

1. Virtual environment command: 
`env\Scripts\activate`

2. Install the project requirements: 
`pip install -r requirements.txt`

3. Migrate and run the project:
`python manage.py migrate`
`python manage.py runserver`

- **Email Testing:** To properly test the email functions within the project change the EMAIL_HOST_USER and EMAIL_HOST_PASSSWORD within the settings.py file to your preferred email. Furthermore, you can change certain parameters within the functions found in the views.py file to meet your specific needs. As an example, using a gmail account you can create an app password (https://security.google.com/settings/security/apppasswords) and use the password provided for EMAIL_HOST_PASSWORD to allow this app to send emails.

----

## Usage

### Registration

To begin using the app, navigate to the registration page. Here, you can create a new user account.

### Access Code

During registration, use the access code "007" to successfully create your account. This code ensures that only authorized users gain access to the app (Clients).

### Profile Setup

After registration, you can set up your profile by adding relevant details such as your name, address, and other information.

### Accessing Admin Features

- **Creating a Superuser:** If you need access to admin features, you can create a superuser account. This is done through the terminal using the command `python manage.py createsuperuser`.
- **Admin Dashboard:** Once you have created a superuser account, navigate to the `/admin` page. Here, you will have access to a comprehensive dashboard with various administrative tools and features.

### Using the App

- **Scheduling Classes:** You can view, sign up for, and manage dance classes. The scheduler allows you to see available slots, instructors, and class types.
- **Managing Bookings:** Keep track of your bookings, make changes, or cancel as needed. The app provides flexibility and ease in managing your dance schedule.
- **Notifications and Reminders:** Stay updated with class schedules, changes, and important announcements through in-app notifications and reminders.

----

## Contact

Hunter Weselosky - huntermweselosky@gmail.com