# multidoist
Schedule and plan multiple todoist tasks for long-running multi-step processes.

**Disclaimer:** This is a quick, hacky script. Use at your own risk.

## What for?
This is ideal for your favourite Covid-19 lockdown activity: bread baking!
Good bread requires multiple steps with long wait times in-between.
This script helps you plan your bread baking process.
You describe the process in a YML file, giving the ``target_time`` when to finish the final step of the process.
Then you list all prerequisite steps in a tree-like fashion, with their respective duration.
The script will plan all tasks accordingly to reach the end of the process at the desired target time.

These tasks are saved to Todoist, via the API.
Tasks are added to the project set as ``todoist_project`` in the YML file (see [example file](example_process.yml)).
Inside the project, the script adds a new section named like the ``process_name`` given in the YML file.
All tasks are added to that section, with their due date and time set (start time of each task).
Each defined process step results in a Todoist task, with its given ``name``.
Step ``duration`` is given in minutes.

The script also adds reminders, set to 5 minutes before each tasks due date and time.
This means that you need a Todoist premium account to run it.
If you don't have one, comment out the reminders part.

The script doesn't check if tasks or sections already exists, they will always be created new.
The project has to already exist, though.


## Requirements

* Install ``todoist-python`` via ``pip install todoist-python``
* Install the ``pyyaml``, ``dateutil`` and ``click`` packages using ``pip`` or your favourite Python package manager
* Get your API token from [https://todoist.com/prefs/integrations](https://todoist.com/prefs/integrations)
* Export your API token as environment variable ``TODOIST_API_TOKEN``


## Usage

Running
```bash
python multidoist.py <process definition.yml>
```
will print the planned tasks and times, without actually saving tasks to Todoist.

Running this on [example_process.yml](example_process.yml) gives you
```
Parsing example_process.yml...

Planning to finish on 2021-08-20 09:30:00

Parsed steps:
        2021-08-20 07:00:00: C This has to happen so that B can be done, takes 120 min
        2021-08-20 07:30:00: E This needs to be done early, takes 30 min
        2021-08-20 08:00:00: D This also has to happen before B and takes 60 min, but there is a preparation step E
        2021-08-20 08:45:00: A This has no preparation steps, takes 45 minutes
        2021-08-20 09:00:00: B This has two preparation steps, C and D, and takes 30 min itself

Just planning, not creating the tasks...
```

To save the tasks to Todoist, add the ``--run`` option:
```bash
python multidoist.py --run <process definition.yml>
```


## YML process spec

Study the code, study the example processes... Good luck! :-) 

There is a second example, representing a real sourdough bread baking session, in ``whole_wheat_bread.yml``.
Planning this with ``multidoist`` yields the following output:
```
Parsing whole_wheat_bread.yml...

Planning to finish on 2020-06-10 15:30:00

Parsed steps:
        2020-06-09 13:00:00: Mix sourdough, ferment 18 hours at room temperature
        2020-06-10 07:00:00: Mix autolysis dough (15 min prep), let sit for 30 minutse
        2020-06-10 07:45:00: Knead main dough (30 min), 3 hours intermediate proofing
        2020-06-10 11:15:00: Shape bread (15 min), 3 hours final proofing
        2020-06-10 14:00:00: Pre-heat oven
        2020-06-10 14:30:00: Bake for 60 minutes

Just planning, not creating the tasks...
```
