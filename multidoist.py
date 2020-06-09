import os

from todoist.api import TodoistAPI
import click
import yaml
from dateutil import parser
import datetime


def get_param(d, key, label="specification"):
    if key not in d:
        click.echo(f"\tCould not find field {key} in {label}")
        exit(1)
    return d[key]


def parse_steps(steps, target_time):
    out = []
    for step in steps:
        name = get_param(step, "name", label="step")
        duration = float(get_param(step, "duration", label=f"step"))
        start_time = target_time - datetime.timedelta(minutes=duration)

        out.append(dict(name=name, start_time=start_time))

        if "steps" in step:
            out += parse_steps(step["steps"], start_time)

    return out


@click.command()
@click.option(
    "--run/--dry-run",
    default=False,
    help="Dry-run only (default) or actually create the tasks in todoist",
)
@click.argument("yml_file", type=click.File("r"))
def plan(yml_file, run):
    click.echo(f"Parsing {yml_file.name}...")
    process = yaml.safe_load(yml_file.read())

    # get required parameters
    todoist_project = get_param(process, "todoist_project")
    process_name = get_param(process, "process_name")

    # get and parse target time
    target_time_str = get_param(process, "target_time")
    target_time = parser.parse(target_time_str)
    click.echo(f"\nPlanning to finish on {str(target_time)}")

    # parse steps
    steps = get_param(process, "steps")
    parsed_steps = parse_steps(steps, target_time)
    print("\nParsed steps:")
    for step in sorted(parsed_steps, key=lambda s: s["start_time"]):
        print(f"\t{str(step['start_time'])}: {step['name']}")

    if run:
        click.echo("\nCreating the tasks...")

        # get API token from environment variables
        token = os.environ["TODOIST_API_TOKEN"]

        # create and sync API instance
        api = TodoistAPI(token=token)
        api.sync()

        # find containing project
        project = [p for p in api.state["projects"] if p["name"] == todoist_project]
        if len(project) != 1:
            click.echo(f"Could not identify todoist project {todoist_project}")
            exit(1)
        project = project[0]

        # add a new section for that project
        section = api.sections.add(process_name, project_id=project["id"])
        api.commit()

        # add tasks and reminders
        for i, step in enumerate(sorted(parsed_steps, key=lambda s: s["start_time"])):
            item = api.items.add(
                step["name"],
                project_id=project["id"],
                section_id=section["id"],
                due=dict(date=step["start_time"].strftime("%Y-%m-%dT%H:%M:%S")),
                day_order=1000 + i,
            )
            print("\n\t", str(item))
            api.commit()

            reminder = api.reminders.add(
                item_id=item["id"],
                service="push",
                due=dict(
                    date=(step["start_time"] - datetime.timedelta(minutes=5)).strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    )
                ),
            )
            print("\n\t", str(reminder))
            api.commit()

    else:
        click.echo("\nJust planning, not creating the tasks...")


if __name__ == "__main__":
    plan()
