from plyer import notification

# this is for testing scheduled tasks
#REMOVE LATER

# create a windows notification
notification.notify(
    title='Notification',
    message='This a notification!',
    app_name='Python',
    timeout=10  # Duration in seconds
)
