# backup-local

Tar up the given directory to the specified folder, retain the specified number of backups, and do so on the given 
frequency via a cron job. This role doesn't transfer the tars off the host. This is assumed to be handled afterwards 
by another process. The simplest transfer would be to utilize a mounted drive as the target backup folder so the files 
are moved automatically when the tar is created.

The user ansible connects with is the user context this process is run under.
If you want this to run under another user, you'll need to either connect with that user, or use
these flags when calling this role, assuming you can do password-less sudo to the user in question
from the ansible user. DISCLAIMER: I have used the below code when running tasks as another user,
but I have not used it with a role. Hypothetically, it should work.

    become: yes
    become_user: "{{ target_user_name }}"
    become_method: sudo
    become_flags: '-i'

For information about PTA and how to use it with this Ansible role please visit https://github.com/Forcepoint/fp-pta-overview/blob/master/README.md

## Requirements

Cron, Tar, and Python3 must be installed. The user context this role runs under is assumed to already
have permissions to read from target folder and to create the destination folder, and the user has
passwordless sudo available.

## Role Variables

### REQUIRED
* backup_local_name: The name for the backup. This must be unique on the host so there's no collision between cron jobs.
* backup_local_target: The folder to tar up.
* backup_local_destination: The folder in which the tar is to be placed.

### OPTIONAL
* backup_local_minute: The minute of the hour to run the job. Defaults to "0", or on the hour.
* backup_local_hour: The hour of the day to run the job. Defaults to "4", or at 4 AM.
* backup_local_day: The day of the month to run the job. Defaults to "*", or every day of the month.
* backup_local_month: The month of the year to run the job. Defaults to "*", or every month of the year.
* backup_local_weekday: The day of the week to run the job. Defaults to "1-5", or Monday through Friday.
* backup_local_retention_number: The number of backups to retain. 0 means infinite (no cleanup). Defaults to 10.
* backup_local_what_if: Logs the operations, but does not actually perform the prescribed tasks. 
  Defaults to 'no'. Useful if you want to double-check what the script will actually do.

## Dependencies

None

## Example Playbook

This performs a backup a folder, Monday through Friday at 6 AM, retaining the 10 most recent backups.

    - hosts: servers
      vars:
        backup_local_name: "App Config"
        backup_local_target: /app/config
        backup_local_destination: /backups/app/config
        backup_local_hour: "6"
      roles:
         - role: backup-local

## License

BSD-3-Clause

## Author Information

Jeremy Cornett <jeremy.cornett@forcepoint.com>
