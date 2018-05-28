#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'julien.bernard <julien.bernard@gmail.com>'
# __description__ = 'Python script to display all comments and notes from a specific Phantom container.'

"""
This scripts displays all comments and notes from a specific container
"""

"""
Phantom instance configuration
"""
PHANTOM_SERVER = 'TBD'
PHANTOM_TOKEN = 'TBD'

import argparse
import logging
import json
import requests


""" main() """
def main():
    """Getting arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("containerID", help="Phantom container ID")
    args = parser.parse_args()

    container_id = args.containerID
    
    """Collecting information"""
    container = get_details(PHANTOM_SERVER, PHANTOM_TOKEN, container_id, "container")
    comments = get_details(PHANTOM_SERVER, PHANTOM_TOKEN, container_id, "comments")
    phases = get_details(PHANTOM_SERVER, PHANTOM_TOKEN, container_id, "phases")
    notes = get_details(PHANTOM_SERVER, PHANTOM_TOKEN, container_id, "notes")

    """Print timeline"""
    try:
        print('{0:30} {1}'.format("Type:", container.get('container_type', "N/A")))
        print('{0:30} {1}'.format("Id:", container.get('id', "N/A")))
        print('{0:30} {1}'.format("Name:", container.get('name', "N/A")))
        print('{0:30} {1}'.format("Description:", container.get('description', "N/A")))
        print('{0:30} {1}'.format("Owner:", container.get('_pretty_owner', "N/A")))
        print('{0:30} {1}'.format("Severity:", container.get('severity', "N/A")))
        print('{0:30} {1}'.format("Phase:", container.get('_pretty_current_phase', "N/A")))
        print('{0:30} {1}'.format("Status:", container.get('status', "N/A")))

        print('{0:30}'.format("-" * 60))
        
        """ SORTING EVERYTHING! """
        activities = []

        for comment in comments.get('data'):
            activities.append([
                comment.get('time'), 
                comment.get('_pretty_user'), 
                'COMMENT', 
                comment.get('comment')])

        for note in notes.get('data'):
            activities.append([
                note.get('create_time'), 
                note.get('_pretty_author'), 
                'NOTE', 
                note.get('title'), 
                note.get('content'), 
                note.get('_pretty_phase')])		
        for phase in phases.get('data'):
            for task in phase.get('tasks'):
                for phasenote in task.get('notes'):
                    activities.append([
                        phasenote.get('create_time'), 
                        phasenote.get('_pretty_author'), 
                        'PHASE', 
                        phase.get('name'),	
                        phasenote.get('_pretty_task'),
                        phasenote.get('title'), 
                        phasenote.get('content')])
                        

        """LOOPING & PRINTING"""

        print('{0:25} {1:25} {2:10} {3:40} {4:40} {5:40} {6}'.format("DATE", "USER", "KIND", "PHASE", "TASK", "TITLE", "CONTENT"))

        for activity in sorted(activities):
            activity_timestamp = activity[0][:19].replace("T", " @ ")
            activity_user = activity[1]
            activity_kind = activity[2]

            # comment
            if activity[2] == "COMMENT":
                comment_text = activity[3]
                print('{0:25} {1:25} {2:10} {3:40} {4:40} {5:40} {6}'.format(activity_timestamp, activity_user,activity_kind, "", "", "",comment_text))

            # NOTES
            if activity[2] == "NOTE":
                note_title = activity[3]
                note_text = activity[4]
                note_phase = activity[5]
                print('{0:25} {1:25} {2:10} {3:40} {4:40} {5:40} {6}'.format(activity_timestamp, activity_user,activity_kind, note_phase, "", note_title,note_text))

            # phase
            if activity[2] == "PHASE":
                phase_name = activity[3]
                task_name = activity[4]
                task_title = activity[5]
                task_content = activity[6]
                print('{0:25} {1:25} {2:10} {3:40} {4:40} {5:40} {6}'.format(activity_timestamp, activity_user,activity_kind, phase_name, task_name, task_title,task_content))

		
    except Exception as e:
        print("Error %s:" % e)



""" get_details() """
def get_details(server, token, container, kind):
    try:
        """Configuring Phantom URL"""

        logging.debug('Configuring Phantom URL')
        if(kind == "container"):
            url = "https://%s/rest/container/%s/?include_expensive&pretty" % (server, container)
        elif(kind == "comments"):
            url = "https://%s/rest/container/%s/comments/?include_expensive&pretty&order=time&order=desc" % (server, container)
        elif(kind == "artifacts"):
            url = "https://%s/rest/container/%s/artifacts/?include_expensive&pretty" % (server, container)
        elif(kind == "actions"):
            url = "https://%s/rest/container/%s/actions/?include_expensive&pretty" % (server, container)
        elif(kind == "attachements"):
            url = "https://%s/rest/container/%s/attachements/?include_expensive&pretty" % (server, container)
        elif(kind == "audit"):
            url = "https://%s/rest/container/%s/audit/?include_expensive&pretty" % (server, container)
        elif(kind == "phases"):
            url = "https://%s/rest/container/%s/phases/?include_expensive&pretty" % (server, container)
        elif(kind == "notes"):
            url = "https://%s/rest/container/%s/notes/?include_expensive&pretty" % (server, container)
        else:
            logging.critical('Error: %s unknown kind', kind)
            exit()

        headers = {
            "ph-auth-token": token
        }
        
        """Running query"""

        logging.info('Collecting data for %s' % kind) 
        
        r = requests.get(url, headers=headers, verify=True)

        """Verifying if query was successful"""
        if (r is None or (r.status_code != 200 and r.status_code != 400)):
            if r is None:
                logging.critical('Error running query')
            else:
                logging.critical('Error: %s - %s', r.status_code, json.loads(r.text)['message'])
                empty_json = '{}'
            return json.loads(empty_json)

        """Query was successful"""
        return json.loads(r.text)
        
    except Exception as e:
        logging.critical('Error: %s', e.args[0])


""" __main__ """
if __name__ == "__main__":
    """Runs main routine."""
    main()
